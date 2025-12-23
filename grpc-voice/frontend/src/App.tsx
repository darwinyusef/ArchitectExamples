import React, { useState } from 'react';
import { AudioRecorder } from './components/AudioRecorder';
import { FileUploader } from './components/FileUploader';
import { TranscriptionDisplay, Transcription } from './components/TranscriptionDisplay';
import { audioService } from './services/audioService';
import './App.css';

function App() {
  const [transcriptions, setTranscriptions] = useState<Transcription[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'record' | 'upload'>('record');

  const handleAudioProcess = async (audioBlob: Blob) => {
    setIsLoading(true);

    try {
      const result = await audioService.transcribeAudio(audioBlob);

      const newTranscription: Transcription = {
        id: Date.now().toString(),
        text: result.text,
        language: result.language,
        duration: result.duration,
        timestamp: Date.now(),
        confidence: result.confidence,
      };

      setTranscriptions((prev) => [newTranscription, ...prev]);
    } catch (error) {
      console.error('Error processing audio:', error);
      alert('Error al procesar el audio. Por favor, intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsLoading(true);

    try {
      // Convertir File a Blob
      const audioBlob = new Blob([file], { type: file.type });
      await handleAudioProcess(audioBlob);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error al subir el archivo. Por favor, intenta de nuevo.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">🎙️ gRPC Voice Streaming</h1>
        <p className="app-subtitle">
          Transcripción de audio en tiempo real con Whisper y gRPC
        </p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'record' ? 'active' : ''}`}
              onClick={() => setActiveTab('record')}
            >
              🎤 Grabar
            </button>
            <button
              className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
              onClick={() => setActiveTab('upload')}
            >
              📁 Subir Archivo
            </button>
          </div>

          <div className="tab-content">
            {activeTab === 'record' ? (
              <AudioRecorder onRecordingComplete={handleAudioProcess} />
            ) : (
              <FileUploader onFileSelect={handleFileUpload} />
            )}
          </div>

          <div className="info-card">
            <h3>ℹ️ Información</h3>
            <ul>
              <li>Formatos soportados: MP3, WAV, M4A, WebM</li>
              <li>Tamaño máximo: 25MB</li>
              <li>Las transcripciones se publican en RabbitMQ</li>
              <li>Usa Whisper para transcripción precisa</li>
            </ul>
          </div>
        </div>

        <div className="right-panel">
          <TranscriptionDisplay
            transcriptions={transcriptions}
            isLoading={isLoading}
          />
        </div>
      </div>

      <footer className="app-footer">
        <p>
          Powered by <strong>Whisper</strong>, <strong>gRPC</strong> y{' '}
          <strong>RabbitMQ</strong>
        </p>
      </footer>
    </div>
  );
}

export default App;
