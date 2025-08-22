"""
Analysis Engine Service

This module handles the AI-powered analysis of resumes against job descriptions.
"""

import re
import logging
from typing import Dict, List, Set, Tuple
import spacy
from collections import Counter

logger = logging.getLogger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.error("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
    nlp = None


class AnalysisEngine:
    """Handles AI-powered analysis of resumes against job descriptions."""
    
    def __init__(self):
        if nlp is None:
            raise Exception("spaCy model not available. Please install en_core_web_sm.")
        self.nlp = nlp
    
    def extract_keywords(self, text: str, min_length: int = 2) -> Set[str]:
        """
        Extract meaningful keywords from text using NLP.
        
        Args:
            text: Input text to analyze
            min_length: Minimum length of keywords to extract
            
        Returns:
            Set of extracted keywords
        """
        doc = self.nlp(text.lower())
        keywords = set()
        
        for token in doc:
            # Extract nouns, proper nouns, and adjectives
            if (token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) >= min_length and
                token.text.isalpha()):
                keywords.add(token.lemma_)
        
        # Also extract named entities (skills, technologies, etc.)
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'WORK_OF_ART', 'LANGUAGE'] and len(ent.text) >= min_length:
                keywords.add(ent.text.lower())
        
        return keywords
    
    def extract_technical_skills(self, text: str) -> Set[str]:
        """
        Extract technical skills and technologies from text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Set of technical skills found
        """
        # Common technical skills and technologies
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
        """
        Calculate keyword match between resume and job description.
        
        Args:
            resume_text: Text content of the resume
            job_description: Text content of the job description
            
        Returns:
            Dictionary containing match analysis results
        """
        # Extract keywords from both texts
        job_keywords = self.extract_keywords(job_description)
        resume_keywords = self.extract_keywords(resume_text)
        
        # Extract technical skills
        job_tech_skills = self.extract_technical_skills(job_description)
        resume_tech_skills = self.extract_technical_skills(resume_text)
        
        # Find matches and misses
        keyword_matches = job_keywords.intersection(resume_keywords)
        keyword_misses = job_keywords - resume_keywords
        
        tech_skill_matches = job_tech_skills.intersection(resume_tech_skills)
        tech_skill_misses = job_tech_skills - resume_tech_skills
        
        # Calculate scores
        total_job_keywords = len(job_keywords)
        total_job_tech_skills = len(job_tech_skills)
        
        keyword_score = len(keyword_matches) / total_job_keywords if total_job_keywords > 0 else 0
        tech_skill_score = len(tech_skill_matches) / total_job_tech_skills if total_job_tech_skills > 0 else 1
        
        # Overall match score (weighted average)
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
        """
        Analyze the structure and quality of the resume.
        
        Args:
            resume_text: Text content of the resume
            
        Returns:
            Dictionary containing structure analysis results
        """
        lines = resume_text.split('\n')
        total_lines = len([line for line in lines if line.strip()])
        
        # Check for common resume sections
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
        
        # Analyze action verbs (strong vs weak)
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
        """
        Generate actionable recommendations based on analysis results.
        
        Args:
            analysis_result: Results from keyword matching analysis
            structure_analysis: Results from structure analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Score-based recommendations
        if analysis_result['overall_score'] < 50:
            recommendations.append("Your resume has a low match score. Consider adding more relevant keywords and skills from the job description.")
        
        if analysis_result['tech_skill_score'] < 70:
            recommendations.append("Add more technical skills mentioned in the job description to strengthen your profile.")
        
        # Missing keywords recommendations
        if analysis_result['keyword_misses']:
            top_misses = analysis_result['keyword_misses'][:5]
            recommendations.append(f"Consider incorporating these important keywords: {', '.join(top_misses)}")
        
        # Missing technical skills recommendations
        if analysis_result['tech_skill_misses']:
            top_tech_misses = analysis_result['tech_skill_misses'][:3]
            recommendations.append(f"Consider highlighting experience with: {', '.join(top_tech_misses)}")
        
        # Structure recommendations
        if structure_analysis['sections_count'] < 4:
            recommendations.append("Your resume might be missing important sections. Consider adding sections like Skills, Projects, or Certifications.")
        
        if structure_analysis['strong_verbs_count'] < 5:
            recommendations.append("Use more action verbs (like 'developed', 'implemented', 'managed') to make your experience more impactful.")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Your resume looks well-matched to the job description! Consider fine-tuning the language to match the company's tone.")
        
        return recommendations[:5]  # Limit to top 5 recommendations

