/**
 * TreeView Provider for Goals and Tasks
 */

import * as vscode from 'vscode';
import { WebSocketClient } from '../services/websocket';

export class GoalsTreeProvider implements vscode.TreeDataProvider<GoalTreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<GoalTreeItem | undefined | null | void> =
        new vscode.EventEmitter<GoalTreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<GoalTreeItem | undefined | null | void> =
        this._onDidChangeTreeData.event;

    private goals: Goal[] = [];

    constructor(private wsClient: WebSocketClient) {
        // Listen for goal updates from WebSocket
        this.wsClient.on('goals.list', (data) => {
            this.goals = data.goals || [];
            this.refresh();
        });
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: GoalTreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: GoalTreeItem): Promise<GoalTreeItem[]> {
        if (!element) {
            // Root level - return goals
            return this.goals.map(goal => new GoalTreeItem(goal, 'goal'));
        } else if (element.contextValue === 'goal') {
            // Return tasks for this goal
            const goal = this.goals.find(g => g.id === element.id);
            if (goal && goal.tasks) {
                return goal.tasks.map(task => new TaskTreeItem(task, goal.id));
            }
        }
        return [];
    }

    // ==================== Helper Methods ====================

    public getGoals(): Goal[] {
        return this.goals;
    }

    public getGoal(goalId: string): Goal | undefined {
        return this.goals.find(g => g.id === goalId);
    }
}

class GoalTreeItem extends vscode.TreeItem {
    constructor(
        public readonly goal: Goal,
        public readonly contextValue: string
    ) {
        super(goal.title, vscode.TreeItemCollapsibleState.Collapsed);

        this.id = goal.id;
        this.description = goal.status;
        this.tooltip = goal.description;

        // Icon based on status
        this.iconPath = new vscode.ThemeIcon(
            goal.status === 'completed' ? 'check' :
            goal.status === 'in_progress' ? 'loading~spin' :
            goal.status === 'failed' ? 'error' :
            'circle-outline'
        );
    }
}

class TaskTreeItem extends vscode.TreeItem {
    constructor(
        public readonly task: Task,
        public readonly goalId: string
    ) {
        super(task.title, vscode.TreeItemCollapsibleState.None);

        this.id = task.id;
        this.contextValue = 'task';
        this.description = task.status;
        this.tooltip = task.description;

        // Icon based on status
        this.iconPath = new vscode.ThemeIcon(
            task.status === 'completed' ? 'pass' :
            task.status === 'in_progress' ? 'sync~spin' :
            task.status === 'failed' ? 'error' :
            'circle-outline'
        );
    }
}

// ==================== Types ====================

interface Goal {
    id: string;
    title: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    tasks?: Task[];
}

interface Task {
    id: string;
    title: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
}
