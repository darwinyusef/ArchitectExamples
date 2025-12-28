export interface Task {
  id: string;
  description: string;
  example?: string; // Code example for the task
  code: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  validationResult?: ValidationResult;
}

export interface Goal {
  id: string;
  title: string;
  description: string;
  documentation: string;
  documentationFile?: string; // Path to .md file: "./docs/goal1.md"
  training?: string; // AI training context/instructions for this goal
  trainingFile?: string; // Path to training .md file: "./training/goal1.md"
  tasks: Task[];
  status: 'pending' | 'in_progress' | 'completed';
  currentTaskIndex: number;
  week?: string; // Format: "2025-W01" or custom like "Semana 1"
  date?: string; // Format: "2025-01-15" ISO date
}

export interface ValidationResult {
  success: boolean;
  message: string;
  suggestions?: string[];
}

export interface GoalsData {
  workshopTitle?: string; // Title of the workshop
  date?: string; // Date of the workshop
  documentationFile?: string; // Path to documentation.md for the entire workshop
  goals: Goal[];
}
