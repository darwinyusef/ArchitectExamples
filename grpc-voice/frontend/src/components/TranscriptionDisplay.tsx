import React from 'react';
import './TranscriptionDisplay.css';

export interface Transcription {
  id: string;
  text: string;
  language?: string;
  duration?: number;
  timestamp: number;
  confidence?: number;
}

interface TranscriptionDisplayProps {
  transcriptions: Transcription[];
  isLoading?: boolean;
}

export const TranscriptionDisplay: React.FC<TranscriptionDisplayProps> = ({
  transcriptions,
  isLoading = false,
}) => {
  const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatDuration = (duration?: number): string => {
    if (!duration) return '';
    const mins = Math.floor(duration / 60);
    const secs = Math.floor(duration % 60);
    return `${mins}m ${secs}s`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Podrías agregar un toast notification aquí
  };

  return (
    <div className="transcription-display">
      <h2 className="transcription-title">
        📝 Transcripciones
        {isLoading && <span className="loading-indicator">Procesando...</span>}
      </h2>

      {transcriptions.length === 0 && !isLoading && (
        <div className="empty-state">
          <p>No hay transcripciones aún</p>
          <p className="empty-hint">
            Graba audio o sube un archivo para comenzar
          </p>
        </div>
      )}

      <div className="transcriptions-list">
        {transcriptions.map((transcription) => (
          <div key={transcription.id} className="transcription-card">
            <div className="transcription-header">
              <div className="transcription-meta">
                <span className="time">
                  🕐 {formatTimestamp(transcription.timestamp)}
                </span>
                {transcription.language && (
                  <span className="language">
                    🌐 {transcription.language.toUpperCase()}
                  </span>
                )}
                {transcription.duration && (
                  <span className="duration">
                    ⏱ {formatDuration(transcription.duration)}
                  </span>
                )}
              </div>

              <button
                className="btn-icon"
                onClick={() => copyToClipboard(transcription.text)}
                title="Copiar al portapapeles"
              >
                📋
              </button>
            </div>

            <div className="transcription-content">
              <p>{transcription.text}</p>
            </div>

            {transcription.confidence !== undefined && (
              <div className="confidence-bar">
                <div className="confidence-label">
                  Confianza: {Math.round(transcription.confidence * 100)}%
                </div>
                <div className="confidence-track">
                  <div
                    className="confidence-fill"
                    style={{ width: `${transcription.confidence * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
