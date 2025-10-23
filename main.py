"""
Sistema de Processamento de Artigos Científicos
Pipeline: Segmentação → Classificação → Análise → Validação + Resumo LLM
"""

import sys
import os
import argparse
from typing import Dict
import json

from segmentation import DocumentSegmentation
from classifier import ScientificArticleClassifier
from text_analyzer import TextAnalyzer
from compliance_validator import ComplianceValidator


class ScientificDocumentProcessor:
    """Processador principal - integra todos os módulos."""
    
    def __init__(self, use_llm: bool = True):
        print("Inicializando sistema...")
        self.segmenter = DocumentSegmentation()
        self.classifier = ScientificArticleClassifier()
        self.analyzer = TextAnalyzer()
        self.validator = ComplianceValidator(use_llm=use_llm)
        print("✓ Sistema pronto\n")
    
    def process_document(self, file_path: str, verbose: bool = True) -> Dict[str, any]:
        """Executa pipeline completo."""
        results = {'success': False, 'file_path': file_path, 'error': None}
        
        try:
            # ETAPA 1: SEGMENTAÇÃO (NFR 2.1)
            if verbose:
                print("=" * 70)
                print("ETAPA 1: SEGMENTAÇÃO (Requisito Obrigatório 1 - NFR 2.1)")
                print("=" * 70)
            
            segmentation_result = self.segmenter.process_document(file_path)
            extracted_text = segmentation_result['text']
            
            if verbose:
                print(f"✓ Segmentação concluída")
                print(f"  Páginas: {segmentation_result['num_pages']}")
                print(f"  Regiões texto: {segmentation_result['num_text_regions']}")
                print(f"  Regiões imagem: {segmentation_result['num_image_regions']}")
            
            results['segmentation'] = segmentation_result
            
            # ETAPA 2: CLASSIFICAÇÃO
            if verbose:
                print("\n" + "=" * 70)
                print("ETAPA 2: CLASSIFICAÇÃO")
                print("=" * 70)
            
            classification_result = self.classifier.classify(extracted_text)
            is_scientific = classification_result['is_scientific']
            confidence = classification_result['confidence']
            features = classification_result['features']
            
            if verbose:
                print(f"Confiança: {confidence*100:.1f}%")
            
            results['classification'] = {
                'is_scientific': is_scientific,
                'confidence': confidence,
                'features': features
            }
            
            # CAMINHO NEGATIVO: Não é artigo científico
            if not is_scientific:
                error_msg = "Não é um documento válido (Artigo Científico)"
                results['error'] = error_msg
                
                if verbose:
                    # Detecta tipo de arquivo
                    file_ext = os.path.splitext(file_path)[1].lower()
                    file_type = "PDF" if file_ext == '.pdf' else "Imagem"
                    file_icon = "📄" if file_ext == '.pdf' else "🖼️"
                    
                    print(f"\n{'='*70}")
                    print("RESUMO FINAL")
                    print(f"{'='*70}")
                    print(f"\n{file_icon} Arquivo: {os.path.basename(file_path)}")
                    print(f"   Tipo: {file_type}")
                    print(f"❌ Classificação: NÃO é Artigo Científico (Confiança: {confidence*100:.1f}%)")
                    print(f"\n⚠️  O documento não atende aos critérios de artigo científico.")
                    print(f"   Processamento interrompido.")
                    print(f"\n{'='*70}")
                
                return results
            
            if verbose:
                print("✓ Documento validado como Artigo Científico")
            
            # ETAPA 3: ANÁLISE ESTRUTURAL E LEXICAL
            if verbose:
                print("\n" + "=" * 70)
                print("ETAPA 3: ANÁLISE ESTRUTURAL E LEXICAL")
                print("=" * 70)
            
            analysis_result = self.analyzer.analyze_text(extracted_text)
            
            if verbose:
                print(f"Parágrafos: {analysis_result['paragraph_count']}")
                print(f"Palavras: {analysis_result['word_count']}")
                print(f"Top 10 palavras: {', '.join([w[0] for w in analysis_result['top_words'][:5]])}...")
            
            results['analysis'] = analysis_result
            
            # ETAPA 4: VALIDAÇÃO E RESUMO LLM (Requisito Obrigatório 2)
            if verbose:
                print("\n" + "=" * 70)
                print("ETAPA 4: VALIDAÇÃO E RESUMO")
                print("=" * 70)
            
            # Verifica conformidade
            compliance = self.validator.check_compliance(analysis_result)
            
            # Cria resumo analítico
            analytical_summary = self.validator.create_analytical_summary(
                text=extracted_text,
                analysis=analysis_result,
                compliance=compliance
            )
            
            if verbose:
                # Detecta tipo de arquivo
                file_ext = os.path.splitext(file_path)[1].lower()
                file_type = "PDF" if file_ext == '.pdf' else "Imagem"
                file_icon = "📄" if file_ext == '.pdf' else "🖼️"
                
                print(f"\n{'='*70}")
                print("RESUMO FINAL")
                print(f"{'='*70}")
                print(f"\n{file_icon} Arquivo: {os.path.basename(file_path)}")
                print(f"   Tipo: {file_type}")
                print(f"✓ Classificação: Artigo Científico (Confiança: {confidence*100:.1f}%)")
                print(f"\n📊 Análise Estrutural:")
                print(f"  • Palavras: {analysis_result['word_count']} (Mínimo: 2000)")
                print(f"  • Parágrafos: {analysis_result['paragraph_count']} (Mínimo: 5)")
                
                # Status de conformidade
                print(f"\n🔍 Conformidade:")
                if compliance['is_compliant']:
                    print(f"  ✅ CONFORME - Documento atende aos requisitos")
                else:
                    print(f"  ❌ NÃO CONFORME - Documento não atende aos requisitos:")
                    for reason in compliance['reasons']:
                        print(f"     • {reason}")
                
                print(f"\n💡 Resumo do Conteúdo:")
                print(f"  {analytical_summary['summary'][:300]}...")
                print(f"\n{'='*70}")
            
            results['summary'] = analytical_summary
            results['success'] = True
            
            return results
            
        except FileNotFoundError:
            error_msg = f"Arquivo não encontrado: {file_path}"
            results['error'] = error_msg
            if verbose:
                print(f"\n✗ ERRO: {error_msg}")
            return results
            
        except Exception as e:
            error_msg = f"Erro: {str(e)}"
            results['error'] = error_msg
            if verbose:
                print(f"\n✗ ERRO: {error_msg}")
            return results
    
    def save_results(self, results: Dict[str, any], output_path: str):
        """Salva resultados em JSON."""
        clean_results = results.copy()
        if 'segmentation' in clean_results:
            clean_results['segmentation'] = {
                'num_pages': clean_results['segmentation']['num_pages'],
                'num_text_regions': clean_results['segmentation']['num_text_regions'],
                'num_image_regions': clean_results['segmentation']['num_image_regions'],
                'text_length': len(clean_results['segmentation']['text'])
            }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(clean_results, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Resultados salvos: {output_path}")


def main():
    """CLI principal."""
    parser = argparse.ArgumentParser(description='Sistema de Processamento de Artigos Científicos')
    parser.add_argument('file', help='Arquivo do documento (PDF, JPG, PNG)')
    parser.add_argument('--output', '-o', help='Salvar resultados em JSON')
    parser.add_argument('--no-llm', action='store_true', help='Desabilita LLM')
    parser.add_argument('--quiet', '-q', action='store_true', help='Modo silencioso')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file):
        print(f"✗ Arquivo não encontrado: {args.file}")
        sys.exit(1)
    
    processor = ScientificDocumentProcessor(use_llm=not args.no_llm)
    results = processor.process_document(args.file, verbose=not args.quiet)
    
    if args.output:
        processor.save_results(results, args.output)
    
    if results['success']:
        sys.exit(0 if results['summary']['is_compliant'] else 2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
