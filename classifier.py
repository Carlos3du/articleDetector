"""
Classificador de Artigos Científicos
"""

import re
from typing import Dict, List


class ScientificArticleClassifier:
    """Classifica se documento é artigo científico."""
    
    def __init__(self):
        self.scientific_keywords = [
            'abstract', 'resumo', 'introduction', 'introdução',
            'methodology', 'metodologia', 'results', 'resultados',
            'discussion', 'discussão', 'conclusion', 'conclusão',
            'references', 'referências', 'bibliografia',
            'hypothesis', 'hipótese', 'experiment', 'experimento',
            'analysis', 'análise', 'study', 'estudo',
            'research', 'pesquisa', 'method', 'método',
            'et al', 'figure', 'figura', 'table', 'tabela',
            'doi', 'issn', 'journal', 'revista'
        ]
        
        self.citation_patterns = [
            r'\([A-Z][a-z]+,?\s+\d{4}\)',  # (Author, 2020)
            r'\[[0-9,\s-]+\]',              # [1], [1-3]
            r'et\s+al\.?,?\s+\d{4}',        # et al. 2020
        ]
    
    def extract_features(self, text: str) -> Dict:
        """Extrai features do texto."""
        text_lower = text.lower()
        
        # Conta keywords
        keyword_count = sum(1 for kw in self.scientific_keywords 
                          if kw in text_lower)
        
        # Detecta citações
        citation_count = sum(len(re.findall(pattern, text)) 
                           for pattern in self.citation_patterns)
        
        # Detecta DOI/ISSN
        has_doi = bool(re.search(r'doi:\s*10\.\d+', text_lower))
        has_issn = bool(re.search(r'issn[:\s]+\d{4}-?\d{3}[\dxX]', text_lower))
        
        # Detecta seções
        sections = ['abstract', 'introduction', 'method', 'result', 'conclusion', 'reference']
        section_count = sum(1 for section in sections if section in text_lower)
        
        return {
            'keyword_count': keyword_count,
            'citation_count': citation_count,
            'has_doi': has_doi,
            'has_issn': has_issn,
            'section_count': section_count
        }
    
    def calculate_confidence_score(self, features: Dict) -> float:
        """Calcula score de confiança (0-1)."""
        score = 0.0
        
        # Keywords (max 0.3)
        score += min(features['keyword_count'] * 0.015, 0.3)
        
        # Citations (max 0.3)
        score += min(features['citation_count'] * 0.02, 0.3)
        
        # DOI/ISSN (0.1 cada)
        if features['has_doi']:
            score += 0.1
        if features['has_issn']:
            score += 0.1
        
        # Sections (max 0.2)
        score += min(features['section_count'] * 0.04, 0.2)
        
        return min(score, 1.0)
    
    def classify(self, text: str) -> Dict:
        """Classifica o documento."""
        if not text or len(text.strip()) < 100:
            return {
                'is_scientific': False,
                'confidence': 0.0,
                'reason': 'Texto muito curto',
                'features': {}
            }
        
        features = self.extract_features(text)
        confidence = self.calculate_confidence_score(features)
        
        # Threshold: 0.3
        is_scientific = confidence >= 0.3
        
        return {
            'is_scientific': is_scientific,
            'confidence': confidence,
            'features': features,
            'reason': 'Artigo Científico' if is_scientific else 'Não é artigo científico'
        }
