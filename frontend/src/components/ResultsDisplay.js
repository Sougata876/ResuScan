/**
 * ResultsDisplay Component
 * Displays the analysis results in a comprehensive format
 */

import React from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results }) => {
  if (!results || !results.analysis) {
    return null;
  }

  const { analysis, metadata } = results;

  const getScoreColor = (score) => {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
  };

  const ScoreCircle = ({ score, label }) => (
    <div className="score-circle">
      <div className={`circle ${getScoreColor(score)}`}>
        <span className="score-value">{score}%</span>
      </div>
      <div className="score-label">{label}</div>
    </div>
  );

  const KeywordList = ({ keywords, title, type = 'default' }) => (
    <div className={`keyword-section ${type}`}>
      <h4 className="keyword-title">{title}</h4>
      {keywords.length > 0 ? (
        <div className="keyword-list">
          {keywords.map((keyword, index) => (
            <span key={index} className={`keyword-tag ${type}`}>
              {keyword}
            </span>
          ))}
        </div>
      ) : (
        <p className="no-keywords">None found</p>
      )}
    </div>
  );

  return (
    <div className="results-display">
      <div className="results-header">
        <h2>Analysis Results</h2>
        <div className="file-info">
          <span className="filename">📄 {metadata.filename}</span>
        </div>
      </div>

      {/* Overall Score Section */}
      <div className="score-section">
        <div className="main-score">
          <ScoreCircle score={analysis.overall_score} label="Overall Match" />
        </div>
        <div className="sub-scores">
          <ScoreCircle score={analysis.keyword_score} label="Keywords" />
          <ScoreCircle score={analysis.tech_skill_score} label="Tech Skills" />
        </div>
      </div>

      {/* Keywords Analysis */}
      <div className="analysis-section">
        <h3>Keyword Analysis</h3>
        <div className="keyword-grid">
          <KeywordList 
            keywords={analysis.keyword_matches} 
            title="✅ Keywords Found" 
            type="found" 
          />
          <KeywordList 
            keywords={analysis.keyword_misses} 
            title="❌ Keywords Missing" 
            type="missing" 
          />
        </div>
      </div>

      {/* Technical Skills Analysis */}
      <div className="analysis-section">
        <h3>Technical Skills Analysis</h3>
        <div className="keyword-grid">
          <KeywordList 
            keywords={analysis.tech_skill_matches} 
            title="✅ Skills Found" 
            type="found" 
          />
          <KeywordList 
            keywords={analysis.tech_skill_misses} 
            title="❌ Skills Missing" 
            type="missing" 
          />
        </div>
      </div>

      {/* Resume Structure */}
      <div className="analysis-section">
        <h3>Resume Structure</h3>
        <div className="structure-info">
          <div className="structure-item">
            <span className="structure-label">Sections Found:</span>
            <span className="structure-value">
              {analysis.structure.sections_found.length > 0 
                ? analysis.structure.sections_found.join(', ')
                : 'None detected'
              }
            </span>
          </div>
          <div className="structure-item">
            <span className="structure-label">Strong Action Verbs:</span>
            <span className="structure-value">{analysis.structure.strong_verbs_count}</span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="analysis-section recommendations">
        <h3>💡 Recommendations</h3>
        <div className="recommendations-list">
          {analysis.recommendations.map((recommendation, index) => (
            <div key={index} className="recommendation-item">
              <span className="recommendation-number">{index + 1}</span>
              <span className="recommendation-text">{recommendation}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="metadata-section">
        <h4>Analysis Details</h4>
        <div className="metadata-grid">
          <div className="metadata-item">
            <span className="metadata-label">Resume Length:</span>
            <span className="metadata-value">{metadata.resume_length.toLocaleString()} characters</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Job Description Length:</span>
            <span className="metadata-value">{metadata.job_description_length.toLocaleString()} characters</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Keywords Analyzed:</span>
            <span className="metadata-value">{metadata.total_job_keywords}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Tech Skills Analyzed:</span>
            <span className="metadata-value">{metadata.total_job_tech_skills}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;

