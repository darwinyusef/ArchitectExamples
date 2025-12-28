/**
 * WebSocket Client for real-time communication with backend
 */

import * as vscode from 'vscode';
import WebSocket from 'ws';
import { EventEmitter } from 'events';

interface WebSocketMessage {
    type: string;
    payload: any;
    correlation_id: string;
    timestamp: string;
}

export class WebSocketClient extends EventEmitter {
    private ws: WebSocket | null = null;
    private serverUrl: string;
    private token: string | null = null;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private reconnectInterval: number;
    private isConnecting: boolean = false;
    private shouldReconnect: boolean = true;
    private context: vscode.ExtensionContext;

    constructor(serverUrl: string, context: vscode.ExtensionContext) {
        super();
        this.serverUrl = serverUrl;
        this.context = context;

        const config = vscode.workspace.getConfiguration('aiGoalsV2');
        this.reconnectInterval = config.get<number>('reconnectInterval', 5000);
    }

    /**
     * Connect to WebSocket server with JWT token
     */
    public connect(token: string): void {
        if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
            console.log('Already connected or connecting');
            return;
        }

        this.token = token;
        this.isConnecting = true;
        this.shouldReconnect = true;

        const urlWithToken = `${this.serverUrl}?token=${token}`;

        try {
            this.ws = new WebSocket(urlWithToken);

            this.ws.on('open', () => this.onOpen());
            this.ws.on('message', (data) => this.onMessage(data));
            this.ws.on('close', (code, reason) => this.onClose(code, reason));
            this.ws.on('error', (error) => this.onError(error));

        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.isConnecting = false;
            this.scheduleReconnect();
        }
    }

    /**
     * Disconnect from server
     */
    public disconnect(): void {
        this.shouldReconnect = false;

        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    /**
     * Send message to server
     */
    public send(type: string, payload: any): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('WebSocket is not connected');
            return;
        }

        const message: WebSocketMessage = {
            type,
            payload,
            correlation_id: this.generateCorrelationId(),
            timestamp: new Date().toISOString(),
        };

        this.ws.send(JSON.stringify(message));
    }

    /**
     * Check if connected
     */
    public isConnected(): boolean {
        return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }

    // ==================== Private Methods ====================

    private onOpen(): void {
        console.log('WebSocket connected');
        this.isConnecting = false;
        this.emit('connected');

        // Start heartbeat
        this.startHeartbeat();
    }

    private onMessage(data: WebSocket.Data): void {
        try {
            const message: WebSocketMessage = JSON.parse(data.toString());
            console.log('Received message:', message.type);

            // Emit event based on message type
            this.emit(message.type, message.payload);

            // Also emit generic 'message' event
            this.emit('message', message);

        } catch (error) {
            console.error('Error parsing message:', error);
        }
    }

    private onClose(code: number, reason: Buffer): void {
        console.log(`WebSocket closed: ${code} - ${reason.toString()}`);
        this.isConnecting = false;
        this.ws = null;
        this.emit('disconnected', { code, reason: reason.toString() });

        if (this.shouldReconnect) {
            this.scheduleReconnect();
        }
    }

    private onError(error: Error): void {
        console.error('WebSocket error:', error);
        this.emit('error', error.message);
    }

    private scheduleReconnect(): void {
        if (this.reconnectTimer) {
            return;
        }

        console.log(`Reconnecting in ${this.reconnectInterval}ms...`);

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;

            if (this.token && this.shouldReconnect) {
                console.log('Attempting to reconnect...');
                this.connect(this.token);
            }
        }, this.reconnectInterval);
    }

    private startHeartbeat(): void {
        // Send ping every 30 seconds
        const interval = setInterval(() => {
            if (this.isConnected()) {
                this.send('ping', { timestamp: Date.now() });
            } else {
                clearInterval(interval);
            }
        }, 30000);
    }

    private generateCorrelationId(): string {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
}
