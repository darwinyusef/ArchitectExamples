import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { GoalsTreeProvider } from './goalsTreeProvider';
import { DocumentationProvider } from './documentationProvider';
import { TaskInstructionsProvider } from './taskInstructionsProvider';
import { AIService } from './aiService';
import { AuthService } from './authService';
import { Goal, Task, GoalsData } from './types';

let goalsTreeProvider: GoalsTreeProvider;
let currentGoalDocsProvider: DocumentationProvider;
let taskInstructionsProvider: TaskInstructionsProvider;
let aiService: AIService;
let authService: AuthService;
let goals: Goal[] = [];
let currentGoalId: string | undefined;

export function activate(context: vscode.ExtensionContext) {
  console.log('AI Goals Tracker extension is now active!');

  // Initialize services
  aiService = new AIService();
  authService = new AuthService(context);

  // Check if this is first time - validate credentials ONCE
  const isAuthenticated = context.globalState.get<boolean>('aiGoalsTracker.authenticated', false);

  if (!isAuthenticated) {
    // Primera vez - validar credenciales
    authService.ensureAuthenticated().then(success => {
      if (success) {
        vscode.window.showInformationMessage('✅ AI Goals Tracker: Authenticated! You won\'t need to login again.');
      } else {
        vscode.window.showWarningMessage('⚠️ Authentication pending. Configure username and password in Settings.');
      }
    });
  } else {
    console.log('Already authenticated - skipping login');
  }

  // Load goals from workspace
  loadGoals();

  // Register tree data provider
  goalsTreeProvider = new GoalsTreeProvider(goals);
  context.subscriptions.push(
    vscode.window.registerTreeDataProvider('aiGoalsExplorer', goalsTreeProvider)
  );

  // Register documentation provider
  currentGoalDocsProvider = new DocumentationProvider(
    context.extensionUri,
    'current'
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('currentGoalDocs', currentGoalDocsProvider)
  );

  // Register task instructions provider
  taskInstructionsProvider = new TaskInstructionsProvider(context.extensionUri);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('taskInstructions', taskInstructionsProvider)
  );

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.refreshGoals', () => {
      loadGoals();
      goalsTreeProvider.updateGoals(goals);
      updateDocumentationViews();
      vscode.window.showInformationMessage('Goals refreshed!');
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.addGoal', async () => {
      const title = await vscode.window.showInputBox({
        prompt: 'Enter goal title',
        placeHolder: 'e.g., Implement user authentication'
      });

      if (!title) {
        return;
      }

      const description = await vscode.window.showInputBox({
        prompt: 'Enter goal description',
        placeHolder: 'Brief description of what this goal accomplishes'
      });

      const newGoal: Goal = {
        id: Date.now().toString(),
        title,
        description: description || '',
        documentation: '# Documentation\n\nAdd documentation for this goal here.',
        tasks: [],
        status: 'pending',
        currentTaskIndex: 0
      };

      goals.push(newGoal);
      saveGoals();
      goalsTreeProvider.updateGoals(goals);
      updateDocumentationViews();

      vscode.window.showInformationMessage(`Goal "${title}" added!`);
    })
  );

  // Command: Load Workshop Goals
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.loadWorkshop', async () => {
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders) {
        vscode.window.showErrorMessage('No workspace folder open');
        return;
      }

      const workspaceRoot = workspaceFolders[0].uri.fsPath;

      // Look for workshops folder
      const workshopsDir = path.join(workspaceRoot, 'workshops');

      if (!fs.existsSync(workshopsDir)) {
        vscode.window.showErrorMessage('No "workshops" folder found in workspace. Create a folder named "workshops" with your workshop folders inside.');
        return;
      }

      // Read all folders in workshops directory
      const workshopFolders = fs.readdirSync(workshopsDir)
        .filter(name => {
          const fullPath = path.join(workshopsDir, name);
          return fs.statSync(fullPath).isDirectory();
        })
        .map(folderName => ({
          label: folderName,
          description: `Workshop: ${folderName}`,
          path: path.join(workshopsDir, folderName)
        }));

      if (workshopFolders.length === 0) {
        vscode.window.showWarningMessage('No workshop folders found in "workshops" directory');
        return;
      }

      // Let user select a workshop folder
      const selectedWorkshop = await vscode.window.showQuickPick(workshopFolders, {
        placeHolder: 'Select a workshop to load'
      });

      if (!selectedWorkshop) {
        return;
      }

      const examplesPath = path.join(selectedWorkshop.path, 'goals.json');

      if (!fs.existsSync(examplesPath)) {
        vscode.window.showErrorMessage(`No goals.json found in ${selectedWorkshop.label}`);
        return;
      }

      try {
        const data = fs.readFileSync(examplesPath, 'utf8');
        const workshopData: GoalsData = JSON.parse(data);
        const workshopGoals = workshopData.goals || [];

        if (workshopGoals.length === 0) {
          vscode.window.showWarningMessage('No goals found in workshop file');
          return;
        }

        // Load workshop documentation from documentation.md
        const workshopFolder = path.dirname(examplesPath);
        let workshopDocumentation = '';

        if (workshopData.documentationFile) {
          const docPath = path.join(workshopFolder, workshopData.documentationFile);
          if (fs.existsSync(docPath)) {
            workshopDocumentation = fs.readFileSync(docPath, 'utf8');
            console.log(`Loaded workshop documentation from ${docPath}`);
          }
        }

        // Let user select which goals to load
        const quickPickItems = workshopGoals.map(goal => ({
          label: goal.title,
          description: goal.description,
          picked: false,
          goal: goal
        }));

        const selectedItems = await vscode.window.showQuickPick(quickPickItems, {
          canPickMany: true,
          placeHolder: 'Select the goals you want to work on'
        });

        if (!selectedItems || selectedItems.length === 0) {
          return;
        }

        const selectedGoals = selectedItems.map(item => item.goal);

        // Apply workshop documentation to all selected goals
        selectedGoals.forEach(goal => {
          // Use workshop documentation for all goals
          if (workshopDocumentation) {
            goal.documentation = workshopDocumentation;
          }
        });

        // Add selected goals to current goals
        goals.push(...selectedGoals);
        saveGoals();
        goalsTreeProvider.updateGoals(goals);
        updateDocumentationViews();

        vscode.window.showInformationMessage(`✅ Loaded ${selectedGoals.length} workshop goal(s)!`);
      } catch (error) {
        console.error('Error loading workshop goals:', error);
        vscode.window.showErrorMessage('Error loading workshop goals');
      }
    })
  );

  // Command: Clear All Goals
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.clearGoals', async () => {
      const answer = await vscode.window.showWarningMessage(
        '🗑️ Are you sure you want to clear all goals? This action cannot be undone.',
        'Yes, Clear All',
        'Cancel'
      );

      if (answer === 'Yes, Clear All') {
        goals = [];
        currentGoalId = undefined;
        saveGoals();
        goalsTreeProvider.updateGoals(goals);
        updateDocumentationViews();
        taskInstructionsProvider.updateTask(undefined, undefined);
        vscode.window.showInformationMessage('✅ All goals cleared successfully!');
      }
    })
  );

  // Command: Delete Single Goal
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.deleteGoal', async (item: any) => {
      if (!item || !item.goal) {
        return;
      }

      const goal: Goal = item.goal;

      const answer = await vscode.window.showWarningMessage(
        `🗑️ Delete goal "${goal.title}"?`,
        'Yes, Delete',
        'Cancel'
      );

      if (answer === 'Yes, Delete') {
        const index = goals.indexOf(goal);
        if (index > -1) {
          goals.splice(index, 1);

          // If this was the current goal, clear current goal
          if (currentGoalId === goal.id) {
            currentGoalId = undefined;
            taskInstructionsProvider.updateTask(undefined, undefined);
          }

          saveGoals();
          goalsTreeProvider.updateGoals(goals);
          updateDocumentationViews();
          vscode.window.showInformationMessage(`✅ Goal "${goal.title}" deleted!`);
        }
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.startGoal', async (item: any) => {
      if (!item || !item.goal) {
        return;
      }

      const goal: Goal = item.goal;

      // Set current goal
      currentGoalId = goal.id;
      goal.status = 'in_progress';

      // Start first pending task
      const firstPendingTask = goal.tasks.find(t => t.status === 'pending');
      if (firstPendingTask) {
        firstPendingTask.status = 'in_progress';

        // Update task instructions panel
        taskInstructionsProvider.updateTask(firstPendingTask, goal);

        vscode.window.showInformationMessage(
          `Started goal: ${goal.title}\nCurrent task: ${firstPendingTask.description}`
        );
      }

      saveGoals();
      goalsTreeProvider.refresh();
      updateDocumentationViews();
    })
  );

  // Command: Execute Code (Play button) - Now with AI Validation
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.executeCode', async (item: any) => {
      if (!item || !item.goal) {
        return;
      }

      const goal: Goal = item.goal;

      // Check authentication
      if (!authService.isUserAuthenticated()) {
        vscode.window.showErrorMessage('❌ Please authenticate first. Restart VS Code to authenticate.');
        return;
      }

      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage('❌ No active editor. Open a file to execute.');
        return;
      }

      const fileName = path.basename(editor.document.fileName);
      const fileExt = path.extname(editor.document.fileName);
      const languageId = editor.document.languageId;

      // Get the code to validate
      const code = editor.document.getText();

      // Find the current in_progress task
      const currentTask = goal.tasks.find(t => t.status === 'in_progress');

      if (!currentTask) {
        vscode.window.showWarningMessage('⚠️ No task in progress. Start a task first.');
        return;
      }

      // First, execute the code
      let command = '';
      let shouldExecute = true;

      if (fileExt === '.ipynb') {
        // Jupyter Notebook
        vscode.window.showInformationMessage('📓 Jupyter Notebook detected. Use "Run All" in notebook interface.');
        vscode.commands.executeCommand('notebook.execute');
        shouldExecute = false;
      } else if (languageId === 'python' || fileExt === '.py') {
        command = `python "${editor.document.fileName}"`;
      } else if (languageId === 'javascript' || fileExt === '.js') {
        command = `node "${editor.document.fileName}"`;
      } else if (languageId === 'typescript' || fileExt === '.ts') {
        command = `ts-node "${editor.document.fileName}"`;
      } else if (fileExt === '.sh') {
        command = `bash "${editor.document.fileName}"`;
      } else if (languageId === 'html') {
        // For HTML files, don't execute but still validate
        shouldExecute = false;
        vscode.window.showInformationMessage('📄 HTML file detected. Validation will proceed.');
      } else {
        vscode.window.showWarningMessage(`❌ Don't know how to execute ${fileExt} files`);
        return;
      }

      if (shouldExecute && command) {
        const terminal = vscode.window.createTerminal(`Execute: ${fileName}`);
        terminal.show();
        terminal.sendText(command);
        vscode.window.showInformationMessage(`▶️ Executing: ${fileName}`);
      }

      // Now validate with AI
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `🤖 AI validating your code...`,
          cancellable: false
        },
        async (progress) => {
          progress.report({ increment: 0 });

          // Validate with AI
          const validationResult = await aiService.validateCode(
            currentTask.description,
            code,
            goal.description
          );

          progress.report({ increment: 100 });

          // Update task with validation result
          currentTask.validationResult = validationResult;
          currentTask.code = code;

          if (validationResult.success) {
            // Task completed!
            currentTask.status = 'completed';

            // Move to next task
            const currentIndex = goal.tasks.indexOf(currentTask);
            const nextTask = goal.tasks[currentIndex + 1];

            if (nextTask) {
              nextTask.status = 'in_progress';
              taskInstructionsProvider.updateTask(nextTask, goal);

              vscode.window.showInformationMessage(
                `✅ ${validationResult.message}\n\nNext task: ${nextTask.description}`,
                'OK'
              );
            } else {
              // Goal completed
              goal.status = 'completed';
              taskInstructionsProvider.updateTask(undefined, undefined);

              vscode.window.showInformationMessage(
                `🎉 Goal "${goal.title}" completed!\n\n${validationResult.message}`,
                'OK'
              );
            }
          } else {
            // Task failed validation
            const suggestions = validationResult.suggestions?.join('\n• ') || '';
            vscode.window.showWarningMessage(
              `❌ ${validationResult.message}\n\nSuggestions:\n• ${suggestions}`,
              'OK'
            );
          }

          saveGoals();
          goalsTreeProvider.refresh();
          updateDocumentationViews();
        }
      );
    })
  );

  // Command: Review Code with AI Expert (Eye button)
  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.reviewCode', async (item: any) => {
      if (!item || !item.goal) {
        return;
      }

      if (!authService.isUserAuthenticated()) {
        vscode.window.showErrorMessage('❌ Please authenticate first. Restart VS Code to authenticate.');
        return;
      }

      const goal: Goal = item.goal;
      const editor = vscode.window.activeTextEditor;

      if (!editor) {
        vscode.window.showWarningMessage('❌ No active editor. Open the file you want to review.');
        return;
      }

      const code = editor.document.getText();
      const fileName = path.basename(editor.document.fileName);
      const fileExt = path.extname(editor.document.fileName);
      let language = editor.document.languageId;

      // Read .ipynb files specially
      let codeToReview = code;
      if (fileExt === '.ipynb') {
        try {
          const notebook = JSON.parse(code);
          // Extract all code cells
          codeToReview = notebook.cells
            .filter((cell: any) => cell.cell_type === 'code')
            .map((cell: any) => cell.source.join('\n'))
            .join('\n\n');
          language = 'python'; // Most notebooks are python
        } catch (error) {
          vscode.window.showErrorMessage('❌ Error parsing notebook file');
          return;
        }
      }

      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `👁️ AI Expert reviewing your code...`,
          cancellable: false
        },
        async (progress) => {
          progress.report({ increment: 0 });

          const review = await aiService.reviewCodeAsExpert(
            codeToReview,
            language,
            goal.title,
            fileName,
            goal.training // Pass training context for specialized review
          );

          progress.report({ increment: 100 });

          // Show review in a new document
          const doc = await vscode.workspace.openTextDocument({
            content: `# Code Review - ${fileName}\n\n## Goal: ${goal.title}\n\n${review}`,
            language: 'markdown'
          });

          await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
          vscode.window.showInformationMessage('✅ Code review complete!');
        }
      );
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aiGoalsTracker.validateTask', async (item: any) => {
      if (!item || !item.task || !item.goal) {
        return;
      }

      // Ya no necesita validar - está autenticado permanentemente
      // Solo verificamos si está autenticado
      if (!authService.isUserAuthenticated()) {
        vscode.window.showErrorMessage('❌ Please authenticate first. Restart VS Code to authenticate.');
        return;
      }

      const task: Task = item.task;
      const goal: Goal = item.goal;

      // Show progress
      await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: `Validating task: ${task.description}`,
          cancellable: false
        },
        async (progress) => {
          progress.report({ increment: 0 });

          // Get current code from active editor
          const editor = vscode.window.activeTextEditor;
          if (!editor) {
            vscode.window.showWarningMessage('No active editor. Open the file you want to validate.');
            return;
          }

          const code = editor.document.getText();
          progress.report({ increment: 30, message: 'Analyzing code...' });

          // Validate with AI
          const validationResult = await aiService.validateCode(
            task.description,
            code,
            goal.description
          );

          progress.report({ increment: 70, message: 'Processing results...' });

          // Update task with validation result
          task.validationResult = validationResult;
          task.status = 'completed';
          task.code = code;

          // Move to next task
          const currentIndex = goal.tasks.indexOf(task);
          const nextTask = goal.tasks[currentIndex + 1];

          if (nextTask) {
            nextTask.status = 'in_progress';
            vscode.window.showInformationMessage(
              `✅ Task completed!\n\n${validationResult.message}\n\nNext task: ${nextTask.description}`,
              'OK'
            );
          } else {
            // Goal completed
            goal.status = 'completed';
            vscode.window.showInformationMessage(
              `🎉 Goal "${goal.title}" completed!\n\n${validationResult.message}`,
              'OK'
            );
          }

          saveGoals();
          goalsTreeProvider.refresh();
          updateDocumentationViews();

          // Ya NO cerramos sesión - permanece autenticado
        }
      );
    })
  );

  // Update documentation views on startup
  updateDocumentationViews();

  console.log('AI Goals Tracker activated successfully');
  console.log(`Loaded ${goals.length} goals`);
}

function loadGoals() {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) {
    goals = [];
    return;
  }

  const goalsFilePath = path.join(workspaceFolders[0].uri.fsPath, '.vscode', 'goals.json');
  const workspaceRoot = workspaceFolders[0].uri.fsPath;

  if (fs.existsSync(goalsFilePath)) {
    try {
      const data = fs.readFileSync(goalsFilePath, 'utf8');
      const goalsData: GoalsData = JSON.parse(data);
      goals = goalsData.goals || [];

      // Load external documentation and training files
      goals.forEach(goal => {
        // Load documentation from .md file if specified
        if (goal.documentationFile) {
          const docPath = path.join(workspaceRoot, goal.documentationFile);
          if (fs.existsSync(docPath)) {
            goal.documentation = fs.readFileSync(docPath, 'utf8');
            console.log(`Loaded documentation from ${goal.documentationFile}`);
          }
        }

        // Load training from .md file if specified
        if (goal.trainingFile) {
          const trainingPath = path.join(workspaceRoot, goal.trainingFile);
          if (fs.existsSync(trainingPath)) {
            goal.training = fs.readFileSync(trainingPath, 'utf8');
            console.log(`Loaded training from ${goal.trainingFile}`);
          }
        }
      });

      // Find current goal
      currentGoalId = goals.find(g => g.status === 'in_progress')?.id;
    } catch (error) {
      console.error('Error loading goals:', error);
      vscode.window.showErrorMessage('Error loading goals.json');
      goals = [];
    }
  } else {
    // Create default goals file
    goals = createDefaultGoals();
    saveGoals();
  }
}

function saveGoals() {
  const workspaceFolders = vscode.workspace.workspaceFolders;
  if (!workspaceFolders) {
    return;
  }

  const vscodeDir = path.join(workspaceFolders[0].uri.fsPath, '.vscode');
  if (!fs.existsSync(vscodeDir)) {
    fs.mkdirSync(vscodeDir, { recursive: true });
  }

  const goalsFilePath = path.join(vscodeDir, 'goals.json');
  const goalsData: GoalsData = { goals };

  try {
    fs.writeFileSync(goalsFilePath, JSON.stringify(goalsData, null, 2), 'utf8');
  } catch (error) {
    console.error('Error saving goals:', error);
    vscode.window.showErrorMessage('Error saving goals.json');
  }
}

function updateDocumentationViews() {
  currentGoalDocsProvider.updateDocumentation(goals, currentGoalId);
}

function createDefaultGoals(): Goal[] {
  return [
    {
      id: '1',
      title: 'Setup Project Structure',
      description: 'Initialize the project with basic folder structure and configuration files',
      documentation: `# Setup Project Structure

## Objective
Create a well-organized project structure that follows best practices.

## Key Points
- Use clear folder naming conventions
- Separate concerns (src, tests, config)
- Include necessary configuration files

## Resources
- Follow the project template guidelines
- Use industry-standard folder structures`,
      tasks: [
        {
          id: '1-1',
          description: 'Create src, tests, and config folders',
          code: '',
          status: 'pending'
        },
        {
          id: '1-2',
          description: 'Add package.json with project dependencies',
          code: '',
          status: 'pending'
        },
        {
          id: '1-3',
          description: 'Create README.md with project description',
          code: '',
          status: 'pending'
        }
      ],
      status: 'pending',
      currentTaskIndex: 0
    },
    {
      id: '2',
      title: 'Implement Core Functionality',
      description: 'Build the main features of the application',
      documentation: `# Implement Core Functionality

## Objective
Develop the primary features that deliver value to users.

## Key Points
- Write clean, maintainable code
- Follow SOLID principles
- Add appropriate error handling

## Testing
- Write unit tests for each function
- Ensure edge cases are covered`,
      tasks: [
        {
          id: '2-1',
          description: 'Implement main business logic',
          code: '',
          status: 'pending'
        },
        {
          id: '2-2',
          description: 'Add error handling and validation',
          code: '',
          status: 'pending'
        },
        {
          id: '2-3',
          description: 'Write unit tests',
          code: '',
          status: 'pending'
        }
      ],
      status: 'pending',
      currentTaskIndex: 0
    }
  ];
}

export function deactivate() {
  // Cleanup if needed
}
