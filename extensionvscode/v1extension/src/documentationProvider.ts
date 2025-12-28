import * as vscode from 'vscode';
import { Goal } from './types';

export class DocumentationProvider implements vscode.WebviewViewProvider {
  private _view?: vscode.WebviewView;

  constructor(
    private readonly _extensionUri: vscode.Uri,
    private readonly viewType: 'current' | 'upcoming'
  ) {}

  public resolveWebviewView(
    webviewView: vscode.WebviewView,
    context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken,
  ) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this._extensionUri]
    };

    webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
  }

  public updateDocumentation(goals: Goal[], currentGoalId?: string) {
    if (!this._view) {
      return;
    }

    let content = '';

    if (this.viewType === 'current' && currentGoalId) {
      const currentGoal = goals.find(g => g.id === currentGoalId);
      if (currentGoal) {
        content = this._formatGoalDocumentation(currentGoal, true);
      } else {
        content = '<p style="color: #888;">No active goal selected</p>';
      }
    } else if (this.viewType === 'upcoming') {
      const upcomingGoals = goals.filter(g => g.status === 'pending');
      if (upcomingGoals.length > 0) {
        content = upcomingGoals.map(g => this._formatGoalDocumentation(g, false)).join('<hr/>');
      } else {
        content = '<p style="color: #888;">No upcoming goals</p>';
      }
    }

    this._view.webview.html = this._getHtmlForWebview(this._view.webview, content);
  }

  private _formatGoalDocumentation(goal: Goal, isCurrentGoal: boolean): string {
    const progressPercent = Math.round(
      (goal.tasks.filter(t => t.status === 'completed').length / goal.tasks.length) * 100
    );

    return `
      <div class="goal-doc">
        <h2>${goal.title}</h2>
        ${isCurrentGoal ? `
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${progressPercent}%"></div>
          </div>
          <p class="progress-text">${progressPercent}% Complete</p>
        ` : ''}
        <p class="description">${goal.description}</p>
        <div class="documentation">
          ${this._markdownToHtml(goal.documentation)}
        </div>
        ${isCurrentGoal ? `
          <h3>Tasks Progress</h3>
          <ul class="task-list">
            ${goal.tasks.map(task => `
              <li class="task-item task-${task.status}">
                <span class="task-icon">${this._getTaskIcon(task.status)}</span>
                <span class="task-desc">${task.description}</span>
              </li>
            `).join('')}
          </ul>
        ` : ''}
      </div>
    `;
  }

  private _getTaskIcon(status: string): string {
    switch (status) {
      case 'completed': return '✓';
      case 'in_progress': return '⟳';
      case 'failed': return '✗';
      default: return '○';
    }
  }

  private _markdownToHtml(markdown: string): string {
    // Convert markdown to HTML with support for YouTube videos and images
    let html = markdown;

    // YouTube videos: [youtube](video_id) or [youtube](https://youtube.com/watch?v=VIDEO_ID)
    html = html.replace(/\[youtube\]\((https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+).*?)\)/g,
      '<div class="video-container"><iframe src="https://www.youtube.com/embed/$2" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>');

    html = html.replace(/\[youtube\]\(([a-zA-Z0-9_-]+)\)/g,
      '<div class="video-container"><iframe src="https://www.youtube.com/embed/$1" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>');

    // Images: ![alt](url)
    html = html.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1" class="doc-image" />');

    // Links: [text](url)
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // Headers
    html = html.replace(/### (.*)/g, '<h4>$1</h4>');
    html = html.replace(/## (.*)/g, '<h3>$1</h3>');
    html = html.replace(/# (.*)/g, '<h2>$1</h2>');

    // Text formatting
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');

    // Line breaks
    html = html.replace(/\n/g, '<br/>');

    return html;
  }

  private _getHtmlForWebview(webview: vscode.Webview, content: string = ''): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Documentation</title>
  <style>
    body {
      padding: 10px;
      color: var(--vscode-foreground);
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      line-height: 1.6;
    }

    .goal-doc {
      margin-bottom: 20px;
    }

    h2 {
      color: var(--vscode-textLink-foreground);
      margin-top: 0;
      border-bottom: 1px solid var(--vscode-panel-border);
      padding-bottom: 8px;
    }

    h3 {
      color: var(--vscode-textLink-activeForeground);
      margin-top: 16px;
      margin-bottom: 8px;
    }

    h4 {
      color: var(--vscode-textPreformat-foreground);
      margin-top: 12px;
      margin-bottom: 6px;
    }

    .description {
      color: var(--vscode-descriptionForeground);
      font-style: italic;
      margin: 10px 0;
    }

    .documentation {
      margin: 15px 0;
      padding: 10px;
      background-color: var(--vscode-textBlockQuote-background);
      border-left: 3px solid var(--vscode-textBlockQuote-border);
      border-radius: 3px;
    }

    code {
      background-color: var(--vscode-textCodeBlock-background);
      padding: 2px 4px;
      border-radius: 3px;
      font-family: var(--vscode-editor-font-family);
    }

    .progress-bar {
      width: 100%;
      height: 8px;
      background-color: var(--vscode-progressBar-background);
      border-radius: 4px;
      overflow: hidden;
      margin: 10px 0;
    }

    .progress-fill {
      height: 100%;
      background-color: var(--vscode-progressBar-background);
      background: linear-gradient(90deg,
        var(--vscode-textLink-foreground) 0%,
        var(--vscode-textLink-activeForeground) 100%);
      transition: width 0.3s ease;
    }

    .progress-text {
      font-size: 0.9em;
      color: var(--vscode-descriptionForeground);
      text-align: right;
      margin: 4px 0 10px 0;
    }

    .task-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .task-item {
      padding: 8px;
      margin: 4px 0;
      border-radius: 4px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .task-item.task-completed {
      background-color: rgba(0, 255, 0, 0.1);
    }

    .task-item.task-in_progress {
      background-color: rgba(255, 255, 0, 0.1);
    }

    .task-item.task-failed {
      background-color: rgba(255, 0, 0, 0.1);
    }

    .task-item.task-pending {
      background-color: var(--vscode-list-hoverBackground);
    }

    .task-icon {
      font-weight: bold;
      min-width: 20px;
    }

    .task-completed .task-icon {
      color: #4CAF50;
    }

    .task-in_progress .task-icon {
      color: #FFC107;
    }

    .task-failed .task-icon {
      color: #F44336;
    }

    .task-pending .task-icon {
      color: #888;
    }

    .task-desc {
      flex: 1;
    }

    hr {
      border: none;
      border-top: 1px solid var(--vscode-panel-border);
      margin: 20px 0;
    }

    strong {
      color: var(--vscode-textLink-foreground);
    }

    em {
      color: var(--vscode-textPreformat-foreground);
    }

    /* Video container for responsive YouTube embeds */
    .video-container {
      position: relative;
      padding-bottom: 56.25%; /* 16:9 aspect ratio */
      height: 0;
      overflow: hidden;
      max-width: 100%;
      margin: 15px 0;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .video-container iframe {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border-radius: 8px;
    }

    /* Images in documentation */
    .doc-image {
      max-width: 100%;
      height: auto;
      margin: 15px 0;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      display: block;
    }

    /* Links */
    a {
      color: var(--vscode-textLink-foreground);
      text-decoration: none;
    }

    a:hover {
      text-decoration: underline;
      color: var(--vscode-textLink-activeForeground);
    }
  </style>
</head>
<body>
  ${content || '<p style="color: #888;">No documentation available</p>'}
</body>
</html>`;
  }
}
