import React from 'react';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import './AudioRecorder.css';

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({ onRecordingComplete }) => {
  const {
    isRecording,
    isPaused,
    recordingTime,
    audioBlob,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    clearRecording,
  } = useAudioRecorder();

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleStop = () => {
    stopRecording();
  };

  const handleSubmit = () => {
    if (audioBlob) {
      onRecordingComplete(audioBlob);
      clearRecording();
    }
  };

  return (
    <div className="audio-recorder">
      <div className="recorder-display">
        <div className="status-indicator">
          {isRecording && !isPaused && <span className="recording-dot"></span>}
          {isRecording && isPaused && <span className="paused-dot"></span>}
        </div>

        <div className="time-display">{formatTime(recordingTime)}</div>

        {isRecording && (
          <div className="waveform">
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
          </div>
        )}
      </div>

      <div className="recorder-controls">
        {!isRecording && !audioBlob && (
          <button
            className="btn btn-primary btn-record"
            onClick={startRecording}
          >
            <span className="icon">🎤</span>
            Iniciar Grabación
          </button>
        )}

        {isRecording && (
          <>
            {!isPaused ? (
              <button className="btn btn-secondary" onClick={pauseRecording}>
                <span className="icon">⏸</span>
                Pausar
              </button>
            ) : (
              <button className="btn btn-secondary" onClick={resumeRecording}>
                <span className="icon">▶️</span>
                Reanudar
              </button>
            )}

            <button className="btn btn-danger" onClick={handleStop}>
              <span className="icon">⏹</span>
              Detener
            </button>
          </>
        )}

        {audioBlob && !isRecording && (
          <>
            <audio
              src={URL.createObjectURL(audioBlob)}
              controls
              className="audio-player"
            />

            <div className="audio-actions">
              <button className="btn btn-success" onClick={handleSubmit}>
                <span className="icon">📤</span>
                Transcribir
              </button>

              <button className="btn btn-secondary" onClick={clearRecording}>
                <span className="icon">🗑</span>
                Descartar
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
