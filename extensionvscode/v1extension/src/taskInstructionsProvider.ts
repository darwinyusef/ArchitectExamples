import * as vscode from 'vscode';
import { Goal, Task } from './types';

export class TaskInstructionsProvider implements vscode.WebviewViewProvider {
  private _view?: vscode.WebviewView;
  private _extensionUri: vscode.Uri;
  private currentTask?: Task;
  private currentGoal?: Goal;

  constructor(extensionUri: vscode.Uri) {
    this._extensionUri = extensionUri;
  }

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    this._update();
  }

  public updateTask(task: Task | undefined, goal: Goal | undefined) {
    this.currentTask = task;
    this.currentGoal = goal;
    this._update();
  }

  private _update() {
    if (this._view) {
      this._view.webview.html = this._getHtmlContent();
    }
  }

  private _getHtmlContent(): string {
    if (!this.currentTask || !this.currentGoal) {
      return this._getEmptyStateHtml();
    }

    const taskHtml = this._markdownToHtml(this.currentTask.description);
    const exampleHtml = this.currentTask.example
      ? this._formatCodeExample(this.currentTask.example)
      : '<p class="no-example">No example provided for this task.</p>';

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Task Instructions</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 15px;
      line-height: 1.6;
    }

    h1 {
      font-size: 1.3em;
      color: var(--vscode-titleBar-activeForeground);
      margin-top: 0;
      margin-bottom: 10px;
      border-bottom: 2px solid var(--vscode-panel-border);
      padding-bottom: 8px;
    }

    h2 {
      font-size: 1.1em;
      color: var(--vscode-foreground);
      margin-top: 20px;
      margin-bottom: 10px;
    }

    .task-status {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 12px;
      font-size: 0.85em;
      font-weight: 600;
      margin-left: 10px;
    }

    .status-pending {
      background-color: #ffa50055;
      color: #ffaa00;
    }

    .status-in_progress {
      background-color: #00bfff55;
      color: #00bfff;
    }

    .status-completed {
      background-color: #00ff0055;
      color: #00ff00;
    }

    .task-description {
      background-color: var(--vscode-textBlockQuote-background);
      border-left: 4px solid var(--vscode-textLink-foreground);
      padding: 12px 15px;
      margin: 15px 0;
      border-radius: 4px;
    }

    .example-section {
      margin-top: 20px;
    }

    .code-example {
      background-color: var(--vscode-textCodeBlock-background);
      border: 1px solid var(--vscode-panel-border);
      border-radius: 6px;
      padding: 12px;
      margin: 10px 0;
      overflow-x: auto;
      font-family: var(--vscode-editor-font-family);
      font-size: 0.9em;
      line-height: 1.5;
    }

    .code-example pre {
      margin: 0;
      white-space: pre-wrap;
      word-wrap: break-word;
    }

    .code-example code {
      color: var(--vscode-editor-foreground);
    }

    .no-example {
      color: var(--vscode-descriptionForeground);
      font-style: italic;
      padding: 10px;
    }

    .goal-context {
      background-color: var(--vscode-editor-inactiveSelectionBackground);
      padding: 8px 12px;
      border-radius: 4px;
      margin-bottom: 15px;
      font-size: 0.9em;
    }

    .goal-context strong {
      color: var(--vscode-textLink-foreground);
    }
  </style>
</head>
<body>
  <div class="goal-context">
    <strong>Goal:</strong> ${this.currentGoal.title}
  </div>

  <h1>
    Current Task
    <span class="task-status status-${this.currentTask.status}">
      ${this._formatStatus(this.currentTask.status)}
    </span>
  </h1>

  <div class="task-description">
    ${taskHtml}
  </div>

  <div class="example-section">
    <h2>📝 Example</h2>
    ${exampleHtml}
  </div>
</body>
</html>`;
  }

  private _getEmptyStateHtml(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Task Instructions</title>
  <style>
    body {
      font-family: var(--vscode-font-family);
      color: var(--vscode-foreground);
      background-color: var(--vscode-editor-background);
      padding: 20px;
      text-align: center;
    }

    .empty-state {
      margin-top: 50px;
      color: var(--vscode-descriptionForeground);
    }

    .empty-state h2 {
      font-size: 1.2em;
      margin-bottom: 10px;
    }

    .empty-state p {
      font-size: 0.95em;
      line-height: 1.6;
    }
  </style>
</head>
<body>
  <div class="empty-state">
    <h2>📋 No Task Selected</h2>
    <p>Start a goal to see task instructions here.</p>
    <p>Load a workshop and select a goal to begin!</p>
  </div>
</body>
</html>`;
  }

  private _formatStatus(status: string): string {
    const statusMap: { [key: string]: string } = {
      'pending': '⏳ Pending',
      'in_progress': '▶️ In Progress',
      'completed': '✅ Completed',
      'failed': '❌ Failed'
    };
    return statusMap[status] || status;
  }

  private _markdownToHtml(text: string): string {
    // Simple markdown to HTML conversion
    let html = text;

    // Code blocks with backticks
    html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<pre><code>${this._escapeHtml(code)}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Bold
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Italic
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Line breaks
    html = html.replace(/\n/g, '<br>');

    return html;
  }

  private _formatCodeExample(example: string): string {
    // Remove markdown code fences if present
    let code = example.replace(/```(\w+)?\n([\s\S]*?)```/g, '$2').trim();

    return `<div class="code-example">
      <pre><code>${this._escapeHtml(code)}</code></pre>
    </div>`;
  }

  private _escapeHtml(text: string): string {
    const div = { textContent: text } as any;
    const temp = { innerHTML: '' } as any;
    const node = { appendChild: () => {}, childNodes: [div] };

    return text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
}
