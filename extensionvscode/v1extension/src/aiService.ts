import * as vscode from 'vscode';
import axios from 'axios';
import { ValidationResult } from './types';

export class AIService {
  private apiKey: string;
  private apiUrl = 'https://api.openai.com/v1/chat/completions';

  constructor() {
    this.apiKey = this.getApiKey();
  }

  private getApiKey(): string {
    const config = vscode.workspace.getConfiguration('aiGoalsTracker');
    const apiKey = config.get<string>('openaiApiKey');

    if (!apiKey) {
      vscode.window.showErrorMessage(
        'OpenAI API Key not configured. Please set it in settings: aiGoalsTracker.openaiApiKey'
      );
      return '';
    }

    return apiKey;
  }

  private getModel(): string {
    const config = vscode.workspace.getConfiguration('aiGoalsTracker');
    return config.get<string>('model') || 'gpt-4o-mini';
  }

  async validateCode(
    taskDescription: string,
    code: string,
    goalContext: string
  ): Promise<ValidationResult> {
    if (!this.apiKey) {
      return {
        success: false,
        message: '⚠️ API Key not configured. Please configure OpenAI API key in settings.',
        suggestions: ['Go to Settings and add aiGoalsTracker.openaiApiKey']
      };
    }

    try {
      // Limit code length to prevent excessive token usage
      const maxCodeLength = 3000; // ~750 tokens
      let codeToValidate = code;
      let truncated = false;

      if (code.length > maxCodeLength) {
        codeToValidate = code.substring(0, maxCodeLength);
        truncated = true;
      }

      const prompt = `Validate if code accomplishes task.

Task: ${taskDescription}

Code:
\`\`\`
${codeToValidate}${truncated ? '\n... (truncated)' : ''}
\`\`\`

Respond ONLY with JSON:
{"success": true/false, "message": "brief explanation", "suggestions": ["suggestion 1"]}

Rules:
- success=true ONLY if code FULLY accomplishes the task
- message: brief explanation (max 50 words)
- suggestions: ONLY if success=false (max 2 suggestions)`;

      const response = await axios.post(
        this.apiUrl,
        {
          model: this.getModel(),
          messages: [
            {
              role: 'system',
              content: 'Strict code validator. Respond ONLY with JSON.'
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.1,
          max_tokens: 150 // Reduced from 300
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000 // 30 seconds timeout
        }
      );

      const content = response.data.choices[0].message.content.trim();

      // Extract JSON from markdown code blocks if present
      let jsonContent = content;
      const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
      if (jsonMatch) {
        jsonContent = jsonMatch[1];
      } else {
        const codeBlockMatch = content.match(/```\s*([\s\S]*?)\s*```/);
        if (codeBlockMatch) {
          jsonContent = codeBlockMatch[1];
        }
      }

      try {
        const result = JSON.parse(jsonContent);
        return {
          success: result.success === true,
          message: result.message || (result.success ? '✅ Task completed!' : '❌ Task incomplete'),
          suggestions: result.suggestions || []
        };
      } catch (parseError) {
        console.error('JSON parse error:', parseError);
        console.error('Content:', content);
        return {
          success: false,
          message: '❌ Error parsing AI response. Please try again.',
          suggestions: ['The AI response was not in valid JSON format']
        };
      }
    } catch (error: any) {
      console.error('Error validating code:', error);

      // Handle timeout specifically
      if (error.code === 'ECONNABORTED') {
        return {
          success: false,
          message: '⏱️ Validation timed out. The request took too long.',
          suggestions: ['Try with smaller code', 'Check your internet connection']
        };
      }

      // Handle rate limiting
      if (error.response?.status === 429) {
        return {
          success: false,
          message: '🚫 Rate limit exceeded. Too many requests.',
          suggestions: ['Wait a moment and try again', 'Check your OpenAI plan limits']
        };
      }

      return {
        success: false,
        message: `❌ Error: ${error.message}`,
        suggestions: ['Check your API key and internet connection', 'Verify you have credits in your OpenAI account']
      };
    }
  }

  async reviewCodeAsExpert(
    code: string,
    language: string,
    goalTitle: string,
    fileName: string,
    training?: string
  ): Promise<string> {
    if (!this.apiKey) {
      return '⚠️ API Key not configured. Please configure OpenAI API key in settings.';
    }

    try {
      // Build specialized system prompt with training context
      let systemPrompt = 'You are a SENIOR SOFTWARE ENGINEER and CODE REVIEWER with 15+ years of experience.';

      if (training) {
        systemPrompt += `\n\n## SPECIALIZED TRAINING FOR THIS GOAL:\n${training}\n\nUse this specialized knowledge to provide expert-level review specific to this goal.`;
      }

      const prompt = `Review the following code as an expert in ${language}.

File: ${fileName}
Goal/Context: ${goalTitle}
Language: ${language}

Code to review:
\`\`\`${language}
${code}
\`\`\`

Provide a comprehensive code review covering:

1. **Code Quality** (1-10): Rate the overall quality
2. **Best Practices**: Are industry standards followed?
3. **Performance**: Any performance concerns or optimizations?
4. **Security**: Potential security vulnerabilities?
5. **Readability**: Is the code clean and maintainable?
6. **Bugs/Issues**: Any bugs or potential issues?
7. **Specific to Goal**: Does it meet the goal's requirements?
8. **Recommendations**: Specific improvements to make

${training ? '**IMPORTANT**: Apply your specialized training knowledge for this goal in your review.' : ''}

Be professional, constructive, and detailed. Format your response in markdown.`;

      const response = await axios.post(
        this.apiUrl,
        {
          model: this.getModel(),
          messages: [
            {
              role: 'system',
              content: systemPrompt
            },
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.3,
          max_tokens: 2000
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.choices[0].message.content.trim();
    } catch (error: any) {
      console.error('Error reviewing code:', error);
      return `❌ Error reviewing code: ${error.message}\n\nPlease check your API key and internet connection.`;
    }
  }

  async suggestNextTask(
    goalDescription: string,
    completedTasks: string[],
    currentCode: string
  ): Promise<string> {
    if (!this.apiKey) {
      return 'Configure API Key to get AI suggestions';
    }

    try {
      const prompt = `Given the following goal and completed tasks, suggest the next logical task.

Goal: ${goalDescription}

Completed Tasks:
${completedTasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

Current Code State:
\`\`\`
${currentCode}
\`\`\`

Suggest a specific, actionable next task (one sentence).`;

      const response = await axios.post(
        this.apiUrl,
        {
          model: this.getModel(),
          messages: [
            {
              role: 'user',
              content: prompt
            }
          ],
          temperature: 0.7,
          max_tokens: 100
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.choices[0].message.content.trim();
    } catch (error: any) {
      console.error('Error suggesting next task:', error);
      return 'Error getting AI suggestion';
    }
  }
}
