"""
Validador de Conformidade
"""

from typing import Dict
import re


class ComplianceValidator:
    """Valida conformidade de documentos."""
    
    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.min_words = 2000
        self.min_paragraphs = 5
    
    def check_compliance(self, analysis: Dict) -> Dict:
        """Verifica conformidade (FR 4.2): >2000 palavras E >5 parágrafos."""
        word_count = analysis.get('word_count', 0)
        paragraph_count = analysis.get('paragraph_count', 0)
        
        is_compliant = (word_count > self.min_words and 
                       paragraph_count > self.min_paragraphs)
        
        reasons = []
        if word_count <= self.min_words:
            reasons.append(f"Palavras: {word_count} (mínimo: {self.min_words})")
        if paragraph_count <= self.min_paragraphs:
            reasons.append(f"Parágrafos: {paragraph_count} (mínimo: {self.min_paragraphs})")
        
        return {
            'is_compliant': is_compliant,
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'requirements': {
                'min_words': self.min_words,
                'min_paragraphs': self.min_paragraphs
            },
            'reasons': reasons if not is_compliant else []
        }
    
    def generate_summary_with_llm(self, text: str) -> str:
        """Gera resumo simples (sem LLM)."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Pega primeiras 3 frases
        summary = '. '.join(sentences[:3])
        return summary + '.' if summary else 'Documento processado.'
    
    def create_analytical_summary(self, text: str, analysis: Dict, 
                                 compliance: Dict) -> Dict:
        """Cria resumo analítico."""
        summary_text = self.generate_summary_with_llm(text) if self.use_llm else ""
        
        return {
            'is_compliant': compliance['is_compliant'],
            'compliance_details': compliance,
            'analysis_summary': {
                'word_count': analysis['word_count'],
                'paragraph_count': analysis['paragraph_count'],
                'avg_words_per_paragraph': analysis.get('avg_words_per_paragraph', 0)
            },
            'summary': summary_text,
            'status': 'CONFORME' if compliance['is_compliant'] else 'NÃO CONFORME'
        }
