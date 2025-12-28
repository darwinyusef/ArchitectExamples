import * as vscode from 'vscode';
import { Goal, Task } from './types';

export class GoalsTreeProvider implements vscode.TreeDataProvider<TreeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<TreeItem | undefined | null | void> = new vscode.EventEmitter<TreeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

  constructor(private goals: Goal[]) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  updateGoals(goals: Goal[]): void {
    this.goals = goals;
    this.refresh();
  }

  getTreeItem(element: TreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(element?: TreeItem): Thenable<TreeItem[]> {
    if (!element) {
      // Return root level - goals
      return Promise.resolve(
        this.goals.map(goal => new GoalTreeItem(goal))
      );
    } else if (element instanceof GoalTreeItem) {
      // Return tasks for a goal
      return Promise.resolve(
        element.goal.tasks.map((task, index) => new TaskTreeItem(task, element.goal, index))
      );
    }
    return Promise.resolve([]);
  }

  getGoalById(goalId: string): Goal | undefined {
    return this.goals.find(g => g.id === goalId);
  }

  getTaskById(goalId: string, taskId: string): Task | undefined {
    const goal = this.getGoalById(goalId);
    return goal?.tasks.find(t => t.id === taskId);
  }
}

type TreeItem = GoalTreeItem | TaskTreeItem;

class GoalTreeItem extends vscode.TreeItem {
  constructor(public goal: Goal) {
    super(goal.title, vscode.TreeItemCollapsibleState.Expanded);

    // Show week/date and task progress
    const weekInfo = goal.week || goal.date || '';
    const taskProgress = `${goal.tasks.filter(t => t.status === 'completed').length}/${goal.tasks.length} tasks`;
    this.description = weekInfo ? `${weekInfo} | ${taskProgress}` : taskProgress;
    this.tooltip = `${goal.description}\n${weekInfo}`;
    this.contextValue = 'goal';

    // Set icon based on status
    if (goal.status === 'completed') {
      this.iconPath = new vscode.ThemeIcon('check', new vscode.ThemeColor('terminal.ansiGreen'));
    } else if (goal.status === 'in_progress') {
      this.iconPath = new vscode.ThemeIcon('sync~spin', new vscode.ThemeColor('terminal.ansiYellow'));
    } else {
      this.iconPath = new vscode.ThemeIcon('circle-outline', new vscode.ThemeColor('terminal.ansiBlue'));
    }
  }
}

class TaskTreeItem extends vscode.TreeItem {
  constructor(
    public task: Task,
    public goal: Goal,
    public index: number
  ) {
    super(task.description, vscode.TreeItemCollapsibleState.None);

    this.contextValue = 'task';
    this.tooltip = this.getTooltip();

    // Set icon based on status
    if (task.status === 'completed') {
      this.iconPath = new vscode.ThemeIcon('pass-filled', new vscode.ThemeColor('terminal.ansiGreen'));
      this.description = '✓ Done';
    } else if (task.status === 'in_progress') {
      this.iconPath = new vscode.ThemeIcon('loading~spin', new vscode.ThemeColor('terminal.ansiYellow'));
      this.description = '⟳ In Progress';
    } else if (task.status === 'failed') {
      this.iconPath = new vscode.ThemeIcon('error', new vscode.ThemeColor('terminal.ansiRed'));
      this.description = '✗ Failed';
    } else {
      this.iconPath = new vscode.ThemeIcon('circle-large-outline');
      this.description = 'Pending';
    }
  }

  private getTooltip(): string {
    let tooltip = this.task.description;

    if (this.task.validationResult) {
      tooltip += `\n\n${this.task.validationResult.message}`;
      if (this.task.validationResult.suggestions) {
        tooltip += '\n\nSuggestions:\n' + this.task.validationResult.suggestions.join('\n');
      }
    }

    return tooltip;
  }
}
