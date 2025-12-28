/**
 * Extension V2 - Integrated with Backend
 *
 * This is the new version that connects to the AI Goals Tracker V2 backend
 */

import * as vscode from 'vscode';
import { BackendService } from './backendService';
import { Config } from './config';
import { GoalsTreeProvider } from './goalsTreeProvider';
import { DocumentationProvider } from './documentationProvider';
import { TaskInstructionsProvider } from './taskInstructionsProvider';
import { Goal, Task } from './types';

let backend: BackendService;
let goalsTreeProvider: GoalsTreeProvider;
let currentGoalDocsProvider: DocumentationProvider;
let taskInstructionsProvider: TaskInstructionsProvider;
let goals: Goal[] = [];
let syncTimer: NodeJS.Timeout | null = null;

export function activate(context: vscode.ExtensionContext) {
    console.log('AI Goals Tracker V2 extension is now active!');

    // Check if backend is enabled
    if (!Config.isBackendEnabled()) {
        vscode.window.showWarningMessage('AI Goals Tracker: Backend connection is disabled. Enable it in settings.');
        return;
    }

    // Initialize backend service
    try {
        backend = new BackendService({
            apiUrl: Config.getApiUrl(),
            wsUrl: Config.getWebSocketUrl(),
            userId: Config.getUserId()
        });

        // Test connection
        backend.healthCheck().then(healthy => {
            if (healthy) {
                vscode.window.showInformationMessage(`✅ AI Goals Tracker: Connected to backend at ${Config.getApiUrl()}`);

                // Connect WebSocket if enabled
                if (Config.isWebSocketEnabled()) {
                    backend.connectWebSocket();
                }

                // Load goals from backend
                loadGoalsFromBackend();

                // Setup auto-sync
                setupAutoSync();
            } else {
                vscode.window.showErrorMessage(`❌ AI Goals Tracker: Backend is not reachable at ${Config.getApiUrl()}`);
                vscode.window.showInformationMessage('Please make sure the backend is running: docker-compose up -d');
            }
        }).catch(error => {
            vscode.window.showErrorMessage(`Failed to connect to backend: ${error.message}`);
        });

    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to initialize backend service: ${error.message}`);
        return;
    }

    // Initialize Tree Provider
    goalsTreeProvider = new GoalsTreeProvider(goals);
    context.subscriptions.push(
        vscode.window.registerTreeDataProvider('aiGoalsExplorer', goalsTreeProvider)
    );

    // Initialize Documentation Provider
    currentGoalDocsProvider = new DocumentationProvider(
        context.extensionUri,
        'current'
    );
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('currentGoalDocs', currentGoalDocsProvider)
    );

    // Initialize Task Instructions Provider
    taskInstructionsProvider = new TaskInstructionsProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('taskInstructions', taskInstructionsProvider)
    );

    // Setup WebSocket event handlers
    setupWebSocketHandlers();

    // Register commands
    registerCommands(context);

    // Cleanup on deactivate
    context.subscriptions.push({
        dispose: () => {
            if (syncTimer) {
                clearInterval(syncTimer);
            }
            if (backend) {
                backend.dispose();
            }
        }
    });
}

/**
 * Setup WebSocket event handlers
 */
function setupWebSocketHandlers() {
    if (!backend) { return; }

    // Goal created
    backend.on('goal_created', (data) => {
        vscode.window.showInformationMessage(`📌 New goal created: ${data.title}`);
        loadGoalsFromBackend();
    });

    // Goal updated
    backend.on('goal_updated', (data) => {
        vscode.window.showInformationMessage(`✏️ Goal updated: ${data.title}`);
        loadGoalsFromBackend();
    });

    // Task completed
    backend.on('task_completed', (data) => {
        vscode.window.showInformationMessage(`✅ Task completed: ${data.title}`);
        loadGoalsFromBackend();
    });

    // Code validation result
    backend.on('code_validation_result', (data) => {
        if (data.validation_passed) {
            vscode.window.showInformationMessage(`✅ Code validation passed! Score: ${data.validation_score}`);
        } else {
            vscode.window.showWarningMessage(`⚠️ Code validation failed. Check feedback.`);
        }
    });
}

/**
 * Setup auto-sync with backend
 */
function setupAutoSync() {
    const interval = Config.getSyncInterval();
    if (interval <= 0) {
        return;
    }

    syncTimer = setInterval(() => {
        loadGoalsFromBackend();
    }, interval * 1000);
}

/**
 * Load goals from backend
 */
async function loadGoalsFromBackend() {
    if (!backend) { return; }

    try {
        const backendGoals = await backend.getGoals();

        // Convert backend goals to extension format
        goals = await Promise.all(backendGoals.map(async (bg) => {
            // Load tasks for this goal
            const backendTasks = await backend.getTasks(bg.id);

            const tasks: Task[] = backendTasks.map(bt => ({
                id: bt.id,
                title: bt.title,
                description: bt.description,
                code: '',
                validation: bt.status === 'completed' ? {
                    passed: true,
                    aiReview: 'Task completed',
                    suggestions: []
                } : undefined,
                status: bt.status as any
            }));

            const goal: Goal = {
                id: bg.id,
                title: bg.title,
                description: bg.description,
                documentation: '', // We can load this from backend if needed
                tasks: tasks,
                status: bg.status as any,
                currentTaskIndex: 0
            };

            return goal;
        }));

        // Update tree view
        goalsTreeProvider.updateGoals(goals);

        console.log(`Loaded ${goals.length} goals from backend`);

    } catch (error: any) {
        console.error('Failed to load goals from backend:', error);
        vscode.window.showErrorMessage(`Failed to sync with backend: ${error.message}`);
    }
}

/**
 * Register all commands
 */
function registerCommands(context: vscode.ExtensionContext) {
    // Refresh goals
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.refreshGoals', async () => {
            await loadGoalsFromBackend();
            vscode.window.showInformationMessage('Goals refreshed from backend!');
        })
    );

    // Add new goal
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.addGoal', async () => {
            const title = await vscode.window.showInputBox({
                prompt: 'Enter goal title',
                placeHolder: 'e.g., Implement user authentication'
            });

            if (!title) { return; }

            const description = await vscode.window.showInputBox({
                prompt: 'Enter goal description',
                placeHolder: 'Brief description of what this goal accomplishes'
            });

            // Ask for priority
            const priorityOptions = [
                { label: 'High', value: 'high' },
                { label: 'Medium', value: 'medium' },
                { label: 'Low', value: 'low' }
            ];

            const priorityChoice = await vscode.window.showQuickPick(priorityOptions, {
                placeHolder: 'Select priority'
            });

            try {
                const newGoal = await backend.createGoal({
                    title,
                    description: description || '',
                    user_id: Config.getUserId(),
                    course_id: Config.getCourseId(),
                    priority: (priorityChoice?.value as any) || 'medium'
                });

                vscode.window.showInformationMessage(`✅ Goal "${title}" created!`);
                await loadGoalsFromBackend();

            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to create goal: ${error.message}`);
            }
        })
    );

    // Delete goal
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.deleteGoal', async (item) => {
            if (!item || !item.id) { return; }

            const confirm = await vscode.window.showWarningMessage(
                `Are you sure you want to delete "${item.label}"?`,
                'Yes', 'No'
            );

            if (confirm !== 'Yes') { return; }

            try {
                await backend.deleteGoal(item.id);
                vscode.window.showInformationMessage(`Goal "${item.label}" deleted`);
                await loadGoalsFromBackend();
            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to delete goal: ${error.message}`);
            }
        })
    );

    // Start goal (mark as in progress)
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.startGoal', async (item) => {
            if (!item || !item.id) { return; }

            try {
                await backend.updateGoal(item.id, { status: 'in_progress' });
                vscode.window.showInformationMessage(`Started goal: ${item.label}`);
                await loadGoalsFromBackend();
            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to start goal: ${error.message}`);
            }
        })
    );

    // Validate task (mark as completed)
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.validateTask', async (item) => {
            if (!item || !item.id) { return; }

            try {
                await backend.completeTask(item.id);
                vscode.window.showInformationMessage(`✅ Task completed: ${item.label}`);
                await loadGoalsFromBackend();
            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to complete task: ${error.message}`);
            }
        })
    );

    // Show backend output
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.showBackendOutput', () => {
            if (backend) {
                backend.showOutput();
            }
        })
    );

    // Show rate limit status
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.showRateLimits', async () => {
            try {
                const status = await backend.getRateLimitStatus();
                if (!status) {
                    vscode.window.showInformationMessage('Rate limit status not available');
                    return;
                }

                const message = `Rate Limits for ${Config.getUserId()}:\n\n` +
                    Object.entries(status.limits).map(([action, limits]: [string, any]) => {
                        return `${action}: ${limits.available_tokens}/${limits.max_capacity} available`;
                    }).join('\n');

                vscode.window.showInformationMessage(message, { modal: true });

            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to fetch rate limits: ${error.message}`);
            }
        })
    );

    // Clear all goals (with confirmation)
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsTracker.clearGoals', async () => {
            const confirm = await vscode.window.showWarningMessage(
                'Are you sure you want to delete ALL goals? This cannot be undone!',
                'Yes, delete all', 'Cancel'
            );

            if (confirm !== 'Yes, delete all') { return; }

            try {
                const allGoals = await backend.getGoals();
                for (const goal of allGoals) {
                    await backend.deleteGoal(goal.id);
                }
                vscode.window.showInformationMessage('All goals deleted');
                await loadGoalsFromBackend();
            } catch (error: any) {
                vscode.window.showErrorMessage(`Failed to clear goals: ${error.message}`);
            }
        })
    );
}

export function deactivate() {
    if (syncTimer) {
        clearInterval(syncTimer);
    }
    if (backend) {
        backend.dispose();
    }
}
