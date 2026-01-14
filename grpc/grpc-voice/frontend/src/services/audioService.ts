// Servicio simplificado para audio (sin gRPC-Web por ahora)
// Se puede integrar gRPC-Web después de generar los archivos proto

export interface TranscriptionResult {
  text: string;
  language?: string;
  duration?: number;
  confidence?: number;
  timestamp?: number;
}

export class AudioService {
  private apiUrl: string;

  constructor(apiUrl: string = 'http://localhost:8001') {
    this.apiUrl = apiUrl;
  }

  /**
   * Transcribir audio usando el endpoint REST
   */
  async transcribeAudio(
    audioBlob: Blob,
    language?: string
  ): Promise<TranscriptionResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.mp3');

    if (language) {
      formData.append('language', language);
    }

    try {
      const response = await fetch(`${this.apiUrl}/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      return {
        text: data.transcription,
        language: data.language,
        duration: data.duration,
      };
    } catch (error) {
      console.error('Error transcribing audio:', error);
      throw error;
    }
  }

  /**
   * Verificar salud del servicio
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

export const audioService = new AudioService();
