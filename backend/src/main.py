"""
Standalone Flask application for deployment.
"""

import os
import sys
import logging
import io
import re
from typing import Dict, List, Set
from collections import Counter

from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Document parsing imports
from docx import Document
from PyPDF2 import PdfReader

# NLP imports
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    CORS_ORIGINS = '*'
    
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Resume Parser
class ResumeParser:
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF file: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        try:
            docx_file = io.BytesIO(file_content)
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX: {str(e)}")
            raise Exception(f"Failed to parse DOCX file: {str(e)}")
    
    @staticmethod
    def parse_resume(file_content: bytes, filename: str) -> str:
        filename_lower = filename.lower()
        if filename_lower.endswith('.pdf'):
            return ResumeParser.extract_text_from_pdf(file_content)
        elif filename_lower.endswith('.docx'):
            return ResumeParser.extract_text_from_docx(file_content)
        else:
            raise Exception("Unsupported file type. Please upload a PDF or DOCX file.")
    
    @staticmethod
    def clean_text(text: str) -> str:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)

# Analysis Engine
class AnalysisEngine:
    def __init__(self):
        if nlp is None:
            raise Exception("spaCy model not available.")
        self.nlp = nlp
    
    def extract_keywords(self, text: str, min_length: int = 2) -> Set[str]:
        doc = self.nlp(text.lower())
        keywords = set()
        
        for token in doc:
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) >= min_length and
                token.text.isalpha()):
                keywords.add(token.lemma_)
        
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE'] and len(ent.text) >= min_length:
                keywords.add(ent.text.lower())
        
        return keywords
    
    def extract_technical_skills(self, text: str) -> Set[str]:
        tech_skills = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'nodejs',
            'html', 'css', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github',
            'machine learning', 'ai', 'artificial intelligence', 'data science',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'flask', 'django', 'fastapi', 'spring', 'express',
            'linux', 'windows', 'macos', 'unix'
        }
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in tech_skills:
            if skill in text_lower:
                found_skills.add(skill)
        
        return found_skills
    
    def calculate_keyword_match(self, resume_text: str, job_description: str) -> Dict:
        job_keywords = self.extract_keywords(job_description)
        resume_keywords = self.extract_keywords(resume_text)
        
        job_tech_skills = self.extract_technical_skills(job_description)
        resume_tech_skills = self.extract_technical_skills(resume_text)
        
        keyword_matches = job_keywords.intersection(resume_keywords)
        keyword_misses = job_keywords - resume_keywords
        
        tech_skill_matches = job_tech_skills.intersection(resume_tech_skills)
        tech_skill_misses = job_tech_skills - resume_tech_skills
        
        total_job_keywords = len(job_keywords)
        total_job_tech_skills = len(job_tech_skills)
        
        keyword_score = len(keyword_matches) / total_job_keywords if total_job_keywords > 0 else 0
        tech_skill_score = len(tech_skill_matches) / total_job_tech_skills if total_job_tech_skills > 0 else 1
        
        overall_score = (keyword_score * 0.6 + tech_skill_score * 0.4) * 100
        
        return {
            'overall_score': round(overall_score, 1),
            'keyword_score': round(keyword_score * 100, 1),
            'tech_skill_score': round(tech_skill_score * 100, 1),
            'keyword_matches': sorted(list(keyword_matches)),
            'keyword_misses': sorted(list(keyword_misses)),
            'tech_skill_matches': sorted(list(tech_skill_matches)),
            'tech_skill_misses': sorted(list(tech_skill_misses)),
            'total_job_keywords': total_job_keywords,
            'total_job_tech_skills': total_job_tech_skills
        }
    
    def analyze_resume_structure(self, resume_text: str) -> Dict:
        lines = resume_text.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        
        sections_found = []
        section_patterns = {
            'contact': r'(email|phone|address|linkedin)',
            'experience': r'(experience|work|employment|career)',
            'education': r'(education|degree|university|college)',
            'skills': r'(skills|technologies|competencies)',
            'projects': r'(projects|portfolio)',
            'certifications': r'(certifications|certificates)'
        }
        
        text_lower = resume_text.lower()
        for section, pattern in section_patterns.items():
            if re.search(pattern, text_lower):
                sections_found.append(section)
        
        strong_verbs = {
            'achieved', 'developed', 'implemented', 'managed', 'led', 'created',
            'improved', 'increased', 'reduced', 'optimized', 'designed', 'built',
            'launched', 'delivered', 'coordinated', 'supervised'
        }
        
        doc = self.nlp(resume_text.lower())
        verbs_used = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        strong_verbs_found = [verb for verb in verbs_used if verb in strong_verbs]
        
        return {
            'total_lines': total_lines,
            'sections_found': sections_found,
            'sections_count': len(sections_found),
            'strong_verbs_count': len(set(strong_verbs_found)),
            'strong_verbs_found': sorted(list(set(strong_verbs_found)))
        }
    
    def generate_recommendations(self, analysis_result: Dict, structure_analysis: Dict) -> List[str]:
        recommendations = []
        
        if analysis_result['overall_score'] < 50:
            recommendations.append("Your resume has a low match score. Consider adding more relevant keywords and skills from the job description.")
        
        if analysis_result['tech_skill_score'] < 70:
            recommendations.append("Add more technical skills mentioned in the job description to strengthen your profile.")
        
        if analysis_result['keyword_misses']:
            top_misses = analysis_result['keyword_misses'][:5]
            recommendations.append(f"Consider incorporating these important keywords: {', '.join(top_misses)}")
        
        if analysis_result['tech_skill_misses']:
            top_tech_misses = analysis_result['tech_skill_misses'][:3]
            recommendations.append(f"Consider highlighting experience with: {', '.join(top_tech_misses)}")
        
        if structure_analysis['sections_count'] < 4:
            recommendations.append("Your resume might be missing important sections. Consider adding sections like Skills, Projects, or Certifications.")
        
        if structure_analysis['strong_verbs_count'] < 5:
            recommendations.append("Use more action verbs (like 'developed', 'implemented', 'managed') to make your experience more impactful.")
        
        if len(recommendations) == 0:
            recommendations.append("Your resume looks well-matched to the job description! Consider fine-tuning the language to match the company's tone.")
        
        return recommendations[:5]

# Initialize services
resume_parser = ResumeParser()
analysis_engine = AnalysisEngine()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

@app.route('/')
def index():
    return {
        'message': 'Resume Reviewer API',
        'version': '1.0.0',
        'status': 'running'
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Resume Reviewer API is running'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    try:
        if 'resume_file' not in request.files:
            return jsonify({'error': 'No resume file provided'}), 400
        
        if 'job_description' not in request.form:
            return jsonify({'error': 'No job description provided'}), 400
        
        resume_file = request.files['resume_file']
        job_description = request.form['job_description'].strip()
        
        if resume_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not Config.allowed_file(resume_file.filename):
            return jsonify({'error': 'Invalid file type. Please upload a PDF or DOCX file.'}), 400
        
        if not job_description or len(job_description) < 50:
            return jsonify({'error': 'Job description is too short. Please provide a more detailed description.'}), 400
        
        filename = secure_filename(resume_file.filename)
        file_content = resume_file.read()
        
        logger.info(f"Processing resume file: {filename}")
        resume_text = resume_parser.parse_resume(file_content, filename)
        
        if not resume_text or len(resume_text.strip()) < 100:
            return jsonify({'error': 'Could not extract sufficient text from the resume.'}), 400
        
        resume_text = resume_parser.clean_text(resume_text)
        
        logger.info("Performing resume analysis")
        keyword_analysis = analysis_engine.calculate_keyword_match(resume_text, job_description)
        structure_analysis = analysis_engine.analyze_resume_structure(resume_text)
        recommendations = analysis_engine.generate_recommendations(keyword_analysis, structure_analysis)
        
        response_data = {
            'success': True,
            'analysis': {
                'overall_score': keyword_analysis['overall_score'],
                'keyword_score': keyword_analysis['keyword_score'],
                'tech_skill_score': keyword_analysis['tech_skill_score'],
                'keyword_matches': keyword_analysis['keyword_matches'],
                'keyword_misses': keyword_analysis['keyword_misses'][:10],
                'tech_skill_matches': keyword_analysis['tech_skill_matches'],
                'tech_skill_misses': keyword_analysis['tech_skill_misses'][:5],
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
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/supported-formats', methods=['GET'])
def get_supported_formats():
    return jsonify({
        'supported_formats': list(Config.ALLOWED_EXTENSIONS),
        'max_file_size_mb': Config.MAX_CONTENT_LENGTH // (1024 * 1024)
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

