/**
 * API service for communicating with the Resume Reviewer backend
 */

import axios from 'axios';

// Configure the base URL for the API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
});

/**
 * Analyze a resume against a job description
 * @param {File} resumeFile - The resume file (PDF or DOCX)
 * @param {string} jobDescription - The job description text
 * @returns {Promise} - Promise that resolves to the analysis results
 */
export const analyzeResume = async (resumeFile, jobDescription) => {
  try {
    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    formData.append('job_description', jobDescription);

    const response = await api.post('/api/analyze', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    if (error.response) {
      // Server responded with error status
      throw new Error(error.response.data.error || 'Analysis failed');
    } else if (error.request) {
      // Request was made but no response received
      throw new Error('Unable to connect to the server. Please try again.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
};

/**
 * Get supported file formats
 * @returns {Promise} - Promise that resolves to supported formats info
 */
export const getSupportedFormats = async () => {
  try {
    const response = await api.get('/api/supported-formats');
    return response.data;
  } catch (error) {
    console.error('Error fetching supported formats:', error);
    return {
      supported_formats: ['pdf', 'docx'],
      max_file_size_mb: 16
    };
  }
};

/**
 * Health check endpoint
 * @returns {Promise} - Promise that resolves to health status
 */
export const healthCheck = async () => {
  try {
    const response = await api.get('/api/health');
    return response.data;
  } catch (error) {
    throw new Error('Server is not responding');
  }
};

export default api;

