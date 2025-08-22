/**
 * JobInput Component
 * Handles job description text input with validation
 */

import React from 'react';
import './JobInput.css';

const JobInput = ({ value, onChange, disabled }) => {
  const handleChange = (e) => {
    onChange(e.target.value);
  };

  const characterCount = value.length;
  const minLength = 50;
  const isValid = characterCount >= minLength;

  return (
    <div className="job-input">
      <label htmlFor="job-description" className="job-input-label">
        Job Description
      </label>
      <div className="job-input-container">
        <textarea
          id="job-description"
          className={`job-textarea ${!isValid && value.length > 0 ? 'invalid' : ''}`}
          placeholder="Paste the job description here... Include requirements, responsibilities, and desired skills for the best analysis."
          value={value}
          onChange={handleChange}
          disabled={disabled}
          rows={8}
        />
        <div className="job-input-footer">
          <div className={`character-count ${!isValid && value.length > 0 ? 'invalid' : ''}`}>
            {characterCount} characters
            {!isValid && value.length > 0 && (
              <span className="min-length-hint">
                (minimum {minLength} characters required)
              </span>
            )}
          </div>
          {isValid && (
            <div className="validation-check">
              ✓ Ready for analysis
            </div>
          )}
        </div>
      </div>
      {!isValid && value.length > 0 && (
        <div className="validation-message">
          Please provide a more detailed job description for better analysis results.
        </div>
      )}
    </div>
  );
};

export default JobInput;

