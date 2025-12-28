/**
 * Register all VS Code commands
 */

import * as vscode from 'vscode';
import { WebSocketClient } from '../services/websocket';
import { GoalsTreeProvider } from '../providers/goalsTreeProvider';

export function registerCommands(
    context: vscode.ExtensionContext,
    wsClient: WebSocketClient,
    goalsTreeProvider: GoalsTreeProvider
): void {

    // Connect to server
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.connect', async () => {
            // TODO: Implement actual authentication
            const token = 'placeholder-token';
            wsClient.connect(token);
        })
    );

    // Disconnect from server
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.disconnect', () => {
            wsClient.disconnect();
        })
    );

    // Create new goal
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.createGoal', async () => {
            const title = await vscode.window.showInputBox({
                prompt: 'Enter goal title',
                placeHolder: 'Learn React Hooks'
            });

            if (title) {
                wsClient.send('goal.create', {
                    title,
                    description: '',
                });
            }
        })
    );

    // Start goal
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.startGoal', (item: any) => {
            const goalId = item.id;
            wsClient.send('goal.start', { goal_id: goalId });
        })
    );

    // Validate task
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.validateTask', async (item: any) => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const code = editor.document.getText();
            const taskId = item.id;

            wsClient.send('task.validate', {
                task_id: taskId,
                code
            });

            vscode.window.showInformationMessage('Validating task...');
        })
    );

    // Refresh goals
    context.subscriptions.push(
        vscode.commands.registerCommand('aiGoalsV2.refreshGoals', () => {
            wsClient.send('goals.list', {});
            goalsTreeProvider.refresh();
        })
    );
}
