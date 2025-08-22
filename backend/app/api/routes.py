"""
API Routes for the Resume Reviewer application.
"""

import logging
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.core.config import Config
from app.services.resume_parser import ResumeParser
from app.services.analysis_engine import AnalysisEngine

logger = logging.getLogger(__name__)

# Create Blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
resume_parser = ResumeParser()
analysis_engine = AnalysisEngine()


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Resume Reviewer API is running'
    })


@api_bp.route('/analyze', methods=['POST'])
def analyze_resume():
    """
    Analyze a resume against a job description.
    
    Expected form data:
    - resume_file: PDF or DOCX file
    - job_description: Text content of the job description
    
    Returns:
    - JSON response with analysis results
    """
    try:
        # Validate request
        if 'resume_file' not in request.files:
            return jsonify({
                'error': 'No resume file provided'
            }), 400
        
        if 'job_description' not in request.form:
            return jsonify({
                'error': 'No job description provided'
            }), 400
        
        resume_file = request.files['resume_file']
        job_description = request.form['job_description'].strip()
        
        # Validate file
        if resume_file.filename == '':
            return jsonify({
                'error': 'No file selected'
            }), 400
        
        if not Config.allowed_file(resume_file.filename):
            return jsonify({
                'error': 'Invalid file type. Please upload a PDF or DOCX file.'
            }), 400
        
        # Validate job description
        if not job_description:
            return jsonify({
                'error': 'Job description cannot be empty'
            }), 400
        
        if len(job_description) < 50:
            return jsonify({
                'error': 'Job description is too short. Please provide a more detailed description.'
            }), 400
        
        # Parse resume file
        filename = secure_filename(resume_file.filename)
        file_content = resume_file.read()
        
        logger.info(f"Processing resume file: {filename}")
        resume_text = resume_parser.parse_resume(file_content, filename)
        
        if not resume_text or len(resume_text.strip()) < 100:
            return jsonify({
                'error': 'Could not extract sufficient text from the resume. Please ensure the file is not corrupted and contains readable text.'
            }), 400
        
        # Clean the extracted text
        resume_text = resume_parser.clean_text(resume_text)
        
        # Perform analysis
        logger.info("Performing resume analysis")
        keyword_analysis = analysis_engine.calculate_keyword_match(resume_text, job_description)
        structure_analysis = analysis_engine.analyze_resume_structure(resume_text)
        recommendations = analysis_engine.generate_recommendations(keyword_analysis, structure_analysis)
        
        # Prepare response
        response_data = {
            'success': True,
            'analysis': {
                'overall_score': keyword_analysis['overall_score'],
                'keyword_score': keyword_analysis['keyword_score'],
                'tech_skill_score': keyword_analysis['tech_skill_score'],
                'keyword_matches': keyword_analysis['keyword_matches'],
                'keyword_misses': keyword_analysis['keyword_misses'][:10],  # Limit to top 10
                'tech_skill_matches': keyword_analysis['tech_skill_matches'],
                'tech_skill_misses': keyword_analysis['tech_skill_misses'][:5],  # Limit to top 5
                'structure': {
                    'sections_found': structure_analysis['sections_found'],
                    'sections_count': structure_analysis['sections_count'],
                    'strong_verbs_count': structure_analysis['strong_verbs_count']
                },
                'recommendations': recommendations
            },
            'metadata': {
                'filename': filename,
                'resume_length': len(resume_text),
                'job_description_length': len(job_description),
                'total_job_keywords': keyword_analysis['total_job_keywords'],
                'total_job_tech_skills': keyword_analysis['total_job_tech_skills']
            }
        }
        
        logger.info(f"Analysis completed successfully. Overall score: {keyword_analysis['overall_score']}")
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return jsonify({
            'error': f'Analysis failed: {str(e)}'
        }), 500


@api_bp.route('/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported file formats."""
    return jsonify({
        'supported_formats': list(Config.ALLOWED_EXTENSIONS),
        'max_file_size_mb': Config.MAX_CONTENT_LENGTH // (1024 * 1024)
    })


@api_bp.errorhandler(413)
def file_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'error': f'File too large. Maximum size is {Config.MAX_CONTENT_LENGTH // (1024 * 1024)}MB'
    }), 413


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request error."""
    return jsonify({
        'error': 'Bad request'
    }), 400


@api_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server error."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error'
    }), 500

