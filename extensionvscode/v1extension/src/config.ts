/**
 * Configuration for AI Goals Tracker Extension
 */

import * as vscode from 'vscode';

export class Config {
    /**
     * Get backend API URL from settings
     */
    static getApiUrl(): string {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<string>('backendApiUrl', 'http://localhost:8000');
    }

    /**
     * Get WebSocket URL from settings
     */
    static getWebSocketUrl(): string {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        const apiUrl = this.getApiUrl();

        // Convert http:// to ws://
        const wsUrl = apiUrl.replace('http://', 'ws://').replace('https://', 'wss://');
        return config.get<string>('backendWsUrl', `${wsUrl}/api/v1/ws`);
    }

    /**
     * Get user ID from settings
     */
    static getUserId(): string {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        let userId = config.get<string>('userId', '');

        // If no user ID, generate one
        if (!userId) {
            userId = `vscode-user-${Date.now()}`;
            config.update('userId', userId, vscode.ConfigurationTarget.Global);
        }

        return userId;
    }

    /**
     * Get course ID from settings (optional)
     */
    static getCourseId(): string | undefined {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<string>('courseId');
    }

    /**
     * Get OpenAI API key from settings
     */
    static getOpenAIKey(): string {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<string>('openaiApiKey', '');
    }

    /**
     * Check if backend connection is enabled
     */
    static isBackendEnabled(): boolean {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<boolean>('enableBackend', true);
    }

    /**
     * Check if WebSocket connection is enabled
     */
    static isWebSocketEnabled(): boolean {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<boolean>('enableWebSocket', true);
    }

    /**
     * Get auto-sync interval in seconds
     */
    static getSyncInterval(): number {
        const config = vscode.workspace.getConfiguration('aiGoalsTracker');
        return config.get<number>('syncInterval', 30);
    }
}
