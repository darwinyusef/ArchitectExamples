/**
 * AI Goals Tracker V2 - Main Extension Entry Point
 *
 * Features:
 * - Persistent WebSocket connection to backend
 * - Real-time goal and task updates
 * - TreeView for goals visualization
 * - Webview for documentation
 */

import * as vscode from 'vscode';
import { WebSocketClient } from './services/websocket';
import { GoalsTreeProvider } from './providers/goalsTreeProvider';
import { ConnectionStatusProvider } from './providers/connectionStatusProvider';
import { registerCommands } from './commands';

let wsClient: WebSocketClient;
let goalsTreeProvider: GoalsTreeProvider;
let connectionStatusProvider: ConnectionStatusProvider;

export async function activate(context: vscode.ExtensionContext) {
    console.log('AI Goals Tracker V2 is now active!');

    // Get configuration
    const config = vscode.workspace.getConfiguration('aiGoalsV2');
    const serverUrl = config.get<string>('serverUrl', 'ws://localhost:8000/api/v1/ws');
    const autoConnect = config.get<boolean>('autoConnect', true);

    // Initialize WebSocket client
    wsClient = new WebSocketClient(serverUrl, context);

    // Initialize Tree Provider
    goalsTreeProvider = new GoalsTreeProvider(wsClient);
    vscode.window.registerTreeDataProvider('goalsTreeView', goalsTreeProvider);

    // Initialize Connection Status Provider
    connectionStatusProvider = new ConnectionStatusProvider(context.extensionUri, wsClient);
    vscode.window.registerWebviewViewProvider('connectionStatus', connectionStatusProvider);

    // Register commands
    registerCommands(context, wsClient, goalsTreeProvider);

    // Setup WebSocket event listeners
    setupWebSocketListeners();

    // Auto-connect if enabled
    if (autoConnect) {
        // Get authentication token (placeholder - implement actual auth)
        const token = await getAuthToken();
        if (token) {
            wsClient.connect(token);
        } else {
            vscode.window.showWarningMessage('Please login to connect to AI Goals Tracker');
        }
    }

    // Show status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(cloud-upload) AI Goals';
    statusBarItem.command = 'aiGoalsV2.connect';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Update status bar based on connection
    wsClient.on('connected', () => {
        statusBarItem.text = '$(check) AI Goals';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.prominentBackground');
    });

    wsClient.on('disconnected', () => {
        statusBarItem.text = '$(x) AI Goals';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    });
}

function setupWebSocketListeners() {
    // Goal events
    wsClient.on('goal.created', (data) => {
        vscode.window.showInformationMessage(`Goal created: ${data.title}`);
        goalsTreeProvider.refresh();
    });

    wsClient.on('goal.started', (data) => {
        vscode.window.showInformationMessage(`Goal started: ${data.goal_id}`);
        goalsTreeProvider.refresh();
    });

    // Task events
    wsClient.on('task.validation_result', (data) => {
        if (data.passed) {
            vscode.window.showInformationMessage(`✓ Task validated: ${data.feedback}`);
        } else {
            vscode.window.showWarningMessage(`✗ Task validation failed: ${data.feedback}`);
        }
        goalsTreeProvider.refresh();
    });

    // Motivation events (from Nodo 8)
    wsClient.on('motivation.sent', (data) => {
        vscode.window.showInformationMessage(data.message, { modal: true });
    });

    // Feedback events (from Nodo 4)
    wsClient.on('feedback.generated', (data) => {
        vscode.window.showInformationMessage(`💡 ${data.feedback}`);
    });

    // Connection events
    wsClient.on('connected', () => {
        vscode.window.showInformationMessage('Connected to AI Goals Tracker');
    });

    wsClient.on('disconnected', () => {
        vscode.window.showWarningMessage('Disconnected from AI Goals Tracker');
    });

    wsClient.on('error', (error) => {
        vscode.window.showErrorMessage(`WebSocket error: ${error}`);
    });
}

async function getAuthToken(): Promise<string | null> {
    // TODO: Implement actual authentication flow
    // For now, return a placeholder token
    // In production:
    // 1. Check if token exists in SecretStorage
    // 2. If not, prompt user to login
    // 3. Call /api/v1/auth/login
    // 4. Store token securely

    return 'placeholder-token-implement-real-auth';
}

export function deactivate() {
    if (wsClient) {
        wsClient.disconnect();
    }
}
