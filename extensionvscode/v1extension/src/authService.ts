import * as vscode from 'vscode';
import axios from 'axios';

interface AuthCredentials {
  user: string;
  pass: string;
}

export class AuthService {
  private readonly mockUrl = 'https://raw.githubusercontent.com/darwinyusef/darwinyusef/refs/heads/master/information/loggin_mock.json';
  private context: vscode.ExtensionContext | null = null;

  constructor(context?: vscode.ExtensionContext) {
    if (context) {
      this.context = context;
    }
  }

  async validateCredentials(): Promise<boolean> {
    // Check if already authenticated in previous sessions
    if (this.context) {
      const isAlreadyAuthenticated = this.context.globalState.get<boolean>('aiGoalsTracker.authenticated', false);
      if (isAlreadyAuthenticated) {
        console.log('Already authenticated in previous session');
        return true;
      }
    }

    const config = vscode.workspace.getConfiguration('aiGoalsTracker');
    const username = config.get<string>('username');
    const password = config.get<string>('password');

    if (!username || !password) {
      vscode.window.showErrorMessage(
        'Username and password not configured. Please set them in settings: aiGoalsTracker.username and aiGoalsTracker.password'
      );
      return false;
    }

    try {
      // Fetch mock credentials
      const response = await axios.get<AuthCredentials>(this.mockUrl);
      const validCredentials = response.data;

      // Validate credentials
      if (username === validCredentials.user && password === validCredentials.pass) {
        // Save authentication state permanently
        if (this.context) {
          await this.context.globalState.update('aiGoalsTracker.authenticated', true);
        }
        console.log('Authentication successful - saved to globalState');
        return true;
      } else {
        vscode.window.showErrorMessage(
          '❌ Authentication failed: Invalid username or password'
        );
        return false;
      }
    } catch (error: any) {
      console.error('Error validating credentials:', error);
      vscode.window.showErrorMessage(
        `Error validating credentials: ${error.message}`
      );
      return false;
    }
  }

  async promptForCredentials(): Promise<boolean> {
    const username = await vscode.window.showInputBox({
      prompt: 'Enter your username',
      placeHolder: 'username',
      ignoreFocusOut: true
    });

    if (!username) {
      return false;
    }

    const password = await vscode.window.showInputBox({
      prompt: 'Enter your password',
      placeHolder: 'password',
      password: true,
      ignoreFocusOut: true
    });

    if (!password) {
      return false;
    }

    // Save to configuration
    const config = vscode.workspace.getConfiguration('aiGoalsTracker');
    await config.update('username', username, vscode.ConfigurationTarget.Global);
    await config.update('password', password, vscode.ConfigurationTarget.Global);

    // Validate
    return await this.validateCredentials();
  }

  isUserAuthenticated(): boolean {
    if (this.context) {
      return this.context.globalState.get<boolean>('aiGoalsTracker.authenticated', false);
    }
    return false;
  }

  async logout() {
    if (this.context) {
      await this.context.globalState.update('aiGoalsTracker.authenticated', false);
    }
    console.log('Session logged out');
  }

  async ensureAuthenticated(): Promise<boolean> {
    const config = vscode.workspace.getConfiguration('aiGoalsTracker');
    const username = config.get<string>('username');
    const password = config.get<string>('password');

    if (!username || !password) {
      const response = await vscode.window.showInformationMessage(
        'Authentication required. Would you like to enter your credentials?',
        'Yes', 'No'
      );

      if (response === 'Yes') {
        return await this.promptForCredentials();
      }
      return false;
    }

    return await this.validateCredentials();
  }
}
