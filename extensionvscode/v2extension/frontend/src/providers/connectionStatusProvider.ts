/**
 * Webview Provider for Connection Status
 */

import * as vscode from 'vscode';
import { WebSocketClient } from '../services/websocket';

export class ConnectionStatusProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(
        private readonly extensionUri: vscode.Uri,
        private wsClient: WebSocketClient
    ) {
        // Listen for connection status changes
        this.wsClient.on('connected', () => this.updateView());
        this.wsClient.on('disconnected', () => this.updateView());
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this.extensionUri]
        };

        webviewView.webview.html = this.getHtmlContent();

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(data => {
            switch (data.type) {
                case 'connect':
                    vscode.commands.executeCommand('aiGoalsV2.connect');
                    break;
                case 'disconnect':
                    vscode.commands.executeCommand('aiGoalsV2.disconnect');
                    break;
            }
        });
    }

    private updateView() {
        if (this._view) {
            this._view.webview.html = this.getHtmlContent();
        }
    }

    private getHtmlContent(): string {
        const isConnected = this.wsClient.isConnected();

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Connection Status</title>
            <style>
                body {
                    padding: 16px;
                    font-family: var(--vscode-font-family);
                    color: var(--vscode-foreground);
                }
                .status {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 16px;
                }
                .status-indicator {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background-color: ${isConnected ? '#4caf50' : '#f44336'};
                }
                .status-text {
                    font-weight: 600;
                }
                button {
                    background-color: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 8px 16px;
                    cursor: pointer;
                    border-radius: 4px;
                }
                button:hover {
                    background-color: var(--vscode-button-hoverBackground);
                }
            </style>
        </head>
        <body>
            <div class="status">
                <div class="status-indicator"></div>
                <div class="status-text">${isConnected ? 'Connected' : 'Disconnected'}</div>
            </div>

            ${isConnected ? `
                <button onclick="disconnect()">Disconnect</button>
            ` : `
                <button onclick="connect()">Connect</button>
            `}

            <script>
                const vscode = acquireVsCodeApi();

                function connect() {
                    vscode.postMessage({ type: 'connect' });
                }

                function disconnect() {
                    vscode.postMessage({ type: 'disconnect' });
                }
            </script>
        </body>
        </html>`;
    }
}
