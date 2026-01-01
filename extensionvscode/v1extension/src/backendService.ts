/**
 * Backend Service - Connects VSCode Extension to AI Goals Tracker V2 Backend
 *
 * Features:
 * - REST API calls to FastAPI backend
 * - WebSocket connection for real-time updates
 * - Automatic reconnection
 * - Error handling
 */

import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';
import WebSocket from 'ws';
import { Goal, Task } from './types';

export interface BackendConfig {
    apiUrl: string;
    wsUrl: string;
    userId: string;
}

export interface CreateGoalRequest {
    title: string;
    description: string;
    user_id: string;
    course_id?: string;
    priority?: 'low' | 'medium' | 'high';
}

export interface CreateTaskRequest {
    title: string;
    description: string;
    goal_id: string;
    user_id: string;
    task_type?: 'learning' | 'coding' | 'testing' | 'documentation' | 'review';
}

export interface BackendGoal {
    id: string;
    title: string;
    description: string;
    user_id: string;
    course_id?: string;
    status: 'not_started' | 'in_progress' | 'completed' | 'blocked';
    priority: 'low' | 'medium' | 'high';
    progress_percentage: number;
    created_at: string;
    updated_at: string;
    tasks?: BackendTask[];
}

export interface BackendTask {
    id: string;
    title: string;
    description: string;
    goal_id: string;
    user_id: string;
    status: 'todo' | 'in_progress' | 'completed' | 'blocked';
    task_type: 'learning' | 'coding' | 'testing' | 'documentation' | 'review';
    created_at: string;
    completed_at?: string;
}

export class BackendService {
    private api: AxiosInstance;
    private config: BackendConfig;
    private ws: WebSocket | null = null;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private eventHandlers: Map<string, Set<(data: any) => void>> = new Map();
    private outputChannel: vscode.OutputChannel;

    constructor(config: BackendConfig) {
        this.config = config;
        this.outputChannel = vscode.window.createOutputChannel('AI Goals Tracker - Backend');

        this.api = axios.create({
            baseURL: config.apiUrl,
            timeout: 10000,
            headers: {
                'Content-Type': 'application/json',
                'X-User-ID': config.userId
            }
        });

        // Add response interceptor for logging
        this.api.interceptors.response.use(
            response => {
                this.log(`✓ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
                return response;
            },
            error => {
                this.log(`✗ ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status || 'FAILED'}`, 'error');
                return Promise.reject(error);
            }
        );

        this.log(`Backend Service initialized - API: ${config.apiUrl}, WS: ${config.wsUrl}`);
    }

    private log(message: string, level: 'info' | 'error' | 'warn' = 'info') {
        const timestamp = new Date().toISOString();
        const prefix = level === 'error' ? '❌' : level === 'warn' ? '⚠️' : 'ℹ️';
        this.outputChannel.appendLine(`[${timestamp}] ${prefix} ${message}`);
    }

    // ============================================================================
    // REST API Methods
    // ============================================================================

    /**
     * Health check
     */
    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.api.get('/health');
            return response.data.status === 'healthy';
        } catch (error) {
            this.log(`Health check failed: ${error}`, 'error');
            return false;
        }
    }

    /**
     * Get all goals for current user
     */
    async getGoals(): Promise<BackendGoal[]> {
        try {
            const response = await this.api.get(`/api/v1/goals`, {
                params: { user_id: this.config.userId }
            });
            return response.data;
        } catch (error) {
            this.log(`Failed to fetch goals: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Get a specific goal by ID
     */
    async getGoal(goalId: string): Promise<BackendGoal> {
        try {
            const response = await this.api.get(`/api/v1/goals/${goalId}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to fetch goal ${goalId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Create a new goal
     */
    async createGoal(data: CreateGoalRequest): Promise<BackendGoal> {
        try {
            const response = await this.api.post('/api/v1/goals', data);
            this.log(`Created goal: ${response.data.title}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to create goal: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Update a goal
     */
    async updateGoal(goalId: string, updates: Partial<BackendGoal>): Promise<BackendGoal> {
        try {
            const response = await this.api.patch(`/api/v1/goals/${goalId}`, updates);
            this.log(`Updated goal: ${goalId}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to update goal ${goalId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Delete a goal
     */
    async deleteGoal(goalId: string): Promise<void> {
        try {
            await this.api.delete(`/api/v1/goals/${goalId}`);
            this.log(`Deleted goal: ${goalId}`);
        } catch (error) {
            this.log(`Failed to delete goal ${goalId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Get tasks for a goal
     */
    async getTasks(goalId: string): Promise<BackendTask[]> {
        try {
            const response = await this.api.get('/api/v1/tasks', {
                params: {
                    goal_id: goalId,
                    user_id: this.config.userId
                }
            });
            return response.data;
        } catch (error) {
            this.log(`Failed to fetch tasks for goal ${goalId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Create a new task
     */
    async createTask(data: CreateTaskRequest): Promise<BackendTask> {
        try {
            const response = await this.api.post('/api/v1/tasks', data);
            this.log(`Created task: ${response.data.title}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to create task: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Update a task
     */
    async updateTask(taskId: string, updates: Partial<BackendTask>): Promise<BackendTask> {
        try {
            const response = await this.api.patch(`/api/v1/tasks/${taskId}`, updates);
            this.log(`Updated task: ${taskId}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to update task ${taskId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Complete a task
     */
    async completeTask(taskId: string): Promise<BackendTask> {
        try {
            const response = await this.api.post(`/api/v1/tasks/${taskId}/complete`);
            this.log(`Completed task: ${taskId}`);
            return response.data;
        } catch (error) {
            this.log(`Failed to complete task ${taskId}: ${error}`, 'error');
            throw error;
        }
    }

    /**
     * Get rate limit status for current user
     */
    async getRateLimitStatus(): Promise<any> {
        try {
            const response = await this.api.get(`/api/v1/admin/rate-limits/users/${this.config.userId}/status`);
            return response.data;
        } catch (error) {
            this.log(`Failed to fetch rate limit status: ${error}`, 'error');
            return null;
        }
    }

    // ============================================================================
    // WebSocket Methods
    // ============================================================================

    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.log('WebSocket already connected');
            return;
        }

        try {
            const wsUrl = `${this.config.wsUrl}/${this.config.userId}`;
            this.log(`Connecting to WebSocket: ${wsUrl}`);

            this.ws = new WebSocket(wsUrl);

            this.ws.on('open', () => {
                this.log('✓ WebSocket connected');

                // Subscribe to events
                this.send({
                    type: 'subscribe',
                    channels: ['goals', 'tasks', 'code_validation']
                });
            });

            this.ws.on('message', (data: WebSocket.Data) => {
                try {
                    const message = data.toString();
                    const parsed = JSON.parse(message);
                    this.handleWebSocketMessage(parsed);
                } catch (error) {
                    this.log(`Failed to parse WebSocket message: ${error}`, 'error');
                }
            });

            this.ws.on('error', (error: Error) => {
                this.log(`WebSocket error: ${error.message}`, 'error');
            });

            this.ws.on('close', () => {
                this.log('WebSocket disconnected', 'warn');
                this.scheduleReconnect();
            });

        } catch (error) {
            this.log(`Failed to connect WebSocket: ${error}`, 'error');
            this.scheduleReconnect();
        }
    }

    /**
     * Send message through WebSocket
     */
    private send(message: any) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            this.log('Cannot send message: WebSocket not connected', 'warn');
        }
    }

    /**
     * Handle incoming WebSocket messages
     */
    private handleWebSocketMessage(data: any) {
        this.log(`WebSocket event: ${data.type || 'unknown'}`);

        const eventType = data.type || data.event_type;
        const handlers = this.eventHandlers.get(eventType);

        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    this.log(`Error in event handler for ${eventType}: ${error}`, 'error');
                }
            });
        }
    }

    /**
     * Subscribe to WebSocket events
     */
    on(eventType: string, handler: (data: any) => void) {
        if (!this.eventHandlers.has(eventType)) {
            this.eventHandlers.set(eventType, new Set());
        }
        this.eventHandlers.get(eventType)!.add(handler);
    }

    /**
     * Unsubscribe from WebSocket events
     */
    off(eventType: string, handler: (data: any) => void) {
        const handlers = this.eventHandlers.get(eventType);
        if (handlers) {
            handlers.delete(handler);
        }
    }

    /**
     * Schedule reconnection
     */
    private scheduleReconnect() {
        if (this.reconnectTimer) {
            return;
        }

        this.log('Scheduling WebSocket reconnection in 5 seconds...');
        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connectWebSocket();
        }, 5000);
    }

    /**
     * Disconnect WebSocket
     */
    disconnectWebSocket() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.log('WebSocket disconnected');
        }
    }

    /**
     * Show output channel
     */
    showOutput() {
        this.outputChannel.show();
    }

    /**
     * Dispose resources
     */
    dispose() {
        this.disconnectWebSocket();
        this.outputChannel.dispose();
    }
}
