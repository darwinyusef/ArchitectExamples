import React, { useRef, useState } from 'react';
import './FileUploader.css';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  acceptedFormats?: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  onFileSelect,
  acceptedFormats = '.mp3,.wav,.m4a,.webm',
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file: File) => {
    // Validar formato
    const validFormats = acceptedFormats.split(',').map(f => f.trim());
    const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;

    if (!validFormats.includes(fileExtension)) {
      alert(`Formato no válido. Formatos aceptados: ${acceptedFormats}`);
      return;
    }

    // Validar tamaño (25MB máximo)
    const maxSize = 25 * 1024 * 1024; // 25MB
    if (file.size > maxSize) {
      alert('El archivo es demasiado grande. Tamaño máximo: 25MB');
      return;
    }

    setSelectedFile(file);
  };

  const handleSubmit = () => {
    if (selectedFile) {
      onFileSelect(selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="file-uploader">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats}
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />

        <div className="drop-zone-content">
          <span className="upload-icon">📁</span>
          <p className="drop-zone-text">
            Arrastra un archivo de audio aquí o haz clic para seleccionar
          </p>
          <p className="drop-zone-hint">
            Formatos: MP3, WAV, M4A, WebM (máx. 25MB)
          </p>
        </div>
      </div>

      {selectedFile && (
        <div className="selected-file">
          <div className="file-info">
            <span className="file-icon">🎵</span>
            <div className="file-details">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">{formatFileSize(selectedFile.size)}</p>
            </div>
          </div>

          <div className="file-actions">
            <button className="btn btn-success" onClick={handleSubmit}>
              <span className="icon">📤</span>
              Transcribir
            </button>

            <button className="btn btn-secondary" onClick={handleClear}>
              <span className="icon">✕</span>
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
