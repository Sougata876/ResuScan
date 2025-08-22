/**
 * Main App Component
 * Resume Reviewer Application
 */

import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import JobInput from './components/JobInput';
import ResultsDisplay from './components/ResultsDisplay';
import { analyzeResume } from './services/api';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError(null);
    setResults(null);
  };

  const handleJobDescriptionChange = (value) => {
    setJobDescription(value);
    setError(null);
    setResults(null);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a resume file.');
      return;
    }

    if (!jobDescription || jobDescription.trim().length < 50) {
      setError('Please provide a detailed job description (at least 50 characters).');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResults(null);

    try {
      const analysisResults = await analyzeResume(selectedFile, jobDescription.trim());
      setResults(analysisResults);
    } catch (err) {
      setError(err.message || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setJobDescription('');
    setResults(null);
    setError(null);
  };

  const isReadyToAnalyze = selectedFile && jobDescription.trim().length >= 50;

  return (
    <div className="App">
      <div className="container">
        {/* Header */}
        <header className="app-header">
          <h1 className="app-title">
            🤖 AI-Powered Resume Reviewer
          </h1>
          <p className="app-subtitle">
            Optimize your resume for any job description with AI-powered analysis
          </p>
        </header>

        {/* Main Content */}
        <main className="app-main">
          {/* Input Section */}
          <div className="input-section">
            <div className="input-card">
              <h2 className="section-title">Upload Your Resume</h2>
              <FileUploader
                onFileSelect={handleFileSelect}
                selectedFile={selectedFile}
                disabled={isAnalyzing}
              />
            </div>

            <div className="input-card">
              <h2 className="section-title">Job Description</h2>
              <JobInput
                value={jobDescription}
                onChange={handleJobDescriptionChange}
                disabled={isAnalyzing}
              />
            </div>
          </div>

          {/* Action Buttons */}
          <div className="action-section">
            <button
              className={`analyze-button ${isReadyToAnalyze ? 'ready' : 'disabled'}`}
              onClick={handleAnalyze}
              disabled={!isReadyToAnalyze || isAnalyzing}
            >
              {isAnalyzing ? (
                <>
                  <span className="spinner"></span>
                  Analyzing Resume...
                </>
              ) : (
                <>
                  🔍 Analyze Resume
                </>
              )}
            </button>

            {(results || error) && (
              <button
                className="reset-button"
                onClick={handleReset}
                disabled={isAnalyzing}
              >
                🔄 Start New Analysis
              </button>
            )}
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-section">
              <div className="error-message">
                <span className="error-icon">⚠️</span>
                {error}
              </div>
            </div>
          )}

          {/* Results Display */}
          {results && <ResultsDisplay results={results} />}
        </main>

        {/* Footer */}
        <footer className="app-footer">
          <p>
            Built with React and Flask • AI-powered by spaCy NLP
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;

