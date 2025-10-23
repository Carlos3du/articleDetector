"""
Módulo de Análise Estrutural e Lexical

Este módulo implementa a detecção de parágrafos, quantificação,
extração de texto e análise de frequência de palavras.
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class TextAnalyzer:
    """
    Analisador de texto para extração estrutural e lexical.
    
    Implementa:
    - Detecção e contagem de parágrafos
    - Extração de texto
    - Análise de frequência de palavras
    """
    
    def __init__(self):
        """Inicializa o analisador de texto."""
        self._download_nltk_resources()
        
        # Carrega stop words para português e inglês
        try:
            self.stop_words_pt = set(stopwords.words('portuguese'))
            self.stop_words_en = set(stopwords.words('english'))
            self.stop_words = self.stop_words_pt.union(self.stop_words_en)
        except:
            print("Aviso: Não foi possível carregar stop words. Usando conjunto padrão.")
            self.stop_words = set()
        
        # Adiciona stop words comuns adicionais
        self.stop_words.update([
            'et', 'al', 'fig', 'figure', 'table', 'doi', 'http', 'https',
            'www', 'com', 'org', 'edu', 'vol', 'pp', 'eds', 'ed'
        ])
    
    def _download_nltk_resources(self):
        """Baixa recursos necessários do NLTK."""
        resources = ['punkt', 'stopwords', 'punkt_tab']
        for resource in resources:
            try:
                nltk.data.find(f'tokenizers/{resource}')
            except LookupError:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass
    
    def detect_paragraphs(self, text: str) -> List[str]:
        """
        Detecta e extrai parágrafos do texto.
        
        Um parágrafo é definido como um bloco de texto separado por
        duas ou mais quebras de linha ou por uma linha em branco.
        
        Args:
            text: Texto completo do documento
            
        Returns:
            Lista de parágrafos (strings)
        """
        if not text:
            return []
        
        # Remove espaços extras no início e fim
        text = text.strip()
        
        # Divide por múltiplas quebras de linha
        # Padrão: duas ou mais quebras de linha consecutivas
        paragraphs = re.split(r'\n\s*\n+', text)
        
        # Limpa cada parágrafo
        cleaned_paragraphs = []
        for para in paragraphs:
            # Remove quebras de linha simples dentro do parágrafo
            para = ' '.join(para.split())
            
            # Remove espaços extras
            para = para.strip()
            
            # Filtra parágrafos muito curtos (provavelmente cabeçalhos ou ruído)
            # Mantém parágrafos com pelo menos 3 palavras
            if len(para.split()) >= 3:
                cleaned_paragraphs.append(para)
        
        return cleaned_paragraphs
    
    def count_paragraphs(self, paragraphs: List[str]) -> int:
        """
        Quantifica o número de parágrafos.
        
        Args:
            paragraphs: Lista de parágrafos
            
        Returns:
            Número total de parágrafos
        """
        return len(paragraphs)
    
    def extract_body_text(self, paragraphs: List[str]) -> str:
        """
        Extrai o texto completo do corpo do documento.
        
        Args:
            paragraphs: Lista de parágrafos
            
        Returns:
            Texto completo concatenado
        """
        return '\n\n'.join(paragraphs)
    
    def count_words(self, text: str) -> int:
        """
        Conta o número total de palavras no texto.
        
        Args:
            text: Texto para análise
            
        Returns:
            Número total de palavras
        """
        if not text:
            return 0
        
        # Remove pontuação e divide em palavras
        words = re.findall(r'\b[a-zA-ZáéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]+\b', text.lower())
        return len(words)
    
    def tokenize_words(self, text: str) -> List[str]:
        """
        Tokeniza o texto em palavras, removendo pontuação e caracteres especiais.
        
        Args:
            text: Texto para tokenização
            
        Returns:
            Lista de palavras (tokens)
        """
        if not text:
            return []
        
        # Converte para minúsculas
        text_lower = text.lower()
        
        # Extrai apenas palavras (letras, incluindo acentuadas)
        words = re.findall(
            r'\b[a-zA-ZáéíóúàèìòùâêîôûãõçÁÉÍÓÚÀÈÌÒÙÂÊÎÔÛÃÕÇ]+\b',
            text_lower
        )
        
        return words
    
    def remove_stopwords(self, words: List[str]) -> List[str]:
        """
        Remove stop words da lista de palavras.
        
        Args:
            words: Lista de palavras
            
        Returns:
            Lista de palavras sem stop words
        """
        return [word for word in words if word not in self.stop_words and len(word) > 2]
    
    def calculate_word_frequency(
        self, 
        text: str, 
        top_n: int = 10,
        remove_stop_words: bool = True
    ) -> List[Tuple[str, int]]:
        """
        Calcula a frequência de palavras no texto.
        
        Args:
            text: Texto para análise
            top_n: Número de palavras mais frequentes a retornar
            remove_stop_words: Se True, remove stop words
            
        Returns:
            Lista de tuplas (palavra, frequência) ordenada por frequência
        """
        if not text:
            return []
        
        # Tokeniza palavras
        words = self.tokenize_words(text)
        
        # Remove stop words se solicitado
        if remove_stop_words:
            words = self.remove_stopwords(words)
        
        # Calcula frequências
        word_freq = Counter(words)
        
        # Retorna top N mais frequentes
        return word_freq.most_common(top_n)
    
    def analyze_text(self, text: str) -> Dict[str, any]:
        """
        Executa análise completa do texto.
        
        Args:
            text: Texto completo do documento
            
        Returns:
            Dicionário com todas as análises:
                - paragraphs: Lista de parágrafos
                - paragraph_count: Número de parágrafos
                - body_text: Texto do corpo
                - word_count: Contagem de palavras
                - top_words: Palavras mais frequentes
        """
        # Detecta parágrafos
        paragraphs = self.detect_paragraphs(text)
        paragraph_count = self.count_paragraphs(paragraphs)
        
        # Extrai texto do corpo
        body_text = self.extract_body_text(paragraphs)
        
        # Conta palavras
        word_count = self.count_words(body_text)
        
        # Calcula frequência de palavras
        top_words = self.calculate_word_frequency(body_text, top_n=10)
        
        return {
            'paragraphs': paragraphs,
            'paragraph_count': paragraph_count,
            'body_text': body_text,
            'word_count': word_count,
            'top_words': top_words
        }
    
    def generate_analysis_report(self, analysis: Dict[str, any]) -> str:
        """
        Gera relatório formatado da análise.
        
        Args:
            analysis: Dicionário com resultados da análise
            
        Returns:
            String com relatório formatado
        """
        report = []
        report.append("=" * 60)
        report.append("ANÁLISE ESTRUTURAL E LEXICAL")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Total de Parágrafos: {analysis['paragraph_count']}")
        report.append(f"Total de Palavras: {analysis['word_count']}")
        report.append("")
        
        report.append("-" * 60)
        report.append("PALAVRAS MAIS FREQUENTES (Top 10):")
        report.append("-" * 60)
        
        for idx, (word, freq) in enumerate(analysis['top_words'], 1):
            report.append(f"  {idx:2d}. {word:20s} - {freq:4d} ocorrências")
        
        report.append("")
        report.append("-" * 60)
        report.append("RESUMO DOS PARÁGRAFOS:")
        report.append("-" * 60)
        
        for idx, para in enumerate(analysis['paragraphs'][:5], 1):
            preview = para[:100] + "..." if len(para) > 100 else para
            report.append(f"\n  Parágrafo {idx}:")
            report.append(f"    {preview}")
        
        if len(analysis['paragraphs']) > 5:
            report.append(f"\n  ... e mais {len(analysis['paragraphs']) - 5} parágrafos")
        
        report.append("")
        report.append("=" * 60)
        
        return '\n'.join(report)


def test_analyzer():
    """Função de teste para o analisador."""
    analyzer = TextAnalyzer()
    
    # Texto de teste
    test_text = """
    Machine learning is a subset of artificial intelligence. It enables computers to learn from data.
    
    Deep learning is a specialized form of machine learning. It uses neural networks with multiple layers.
    
    Natural language processing helps computers understand human language. It combines linguistics and machine learning.
    
    Computer vision allows machines to interpret visual information. It uses deep learning techniques extensively.
    
    Data science combines statistics, programming, and domain knowledge. It extracts insights from data.
    """
    
    analysis = analyzer.analyze_text(test_text)
    report = analyzer.generate_analysis_report(analysis)
    print(report)


if __name__ == "__main__":
    test_analyzer()
