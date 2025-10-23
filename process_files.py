"""
Processamento em lote de documentos
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
from main import ScientificDocumentProcessor


def find_documents(directory: str = "./files") -> list:
    """Encontra todos os documentos suportados."""
    supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    path = Path(directory)
    
    if not path.exists():
        return []
    
    documents = [str(f) for f in path.iterdir() 
                 if f.is_file() and f.suffix.lower() in supported_extensions]
    
    return sorted(documents)


def process_batch(documents: list, use_llm: bool = False, save_json: bool = True):
    """Processa lote de documentos."""
    if not documents:
        print("❌ Nenhum documento encontrado!")
        return
    
    print(f"\n{'='*70}")
    print(f"PROCESSAMENTO EM LOTE - {len(documents)} documentos")
    print(f"{'='*70}\n")
    
    processor = ScientificDocumentProcessor(use_llm=use_llm)
    
    results_summary = {
        'timestamp': datetime.now().isoformat(),
        'total': len(documents),
        'results': []
    }
    
    success = compliant = non_compliant = errors = 0
    
    for idx, doc_path in enumerate(documents, 1):
        print(f"\n{'='*70}")
        print(f"[{idx}/{len(documents)}] {os.path.basename(doc_path)}")
        print(f"{'='*70}")
        
        try:
            result = processor.process_document(doc_path, verbose=True)
            
            if result['success']:
                success += 1
                if result['summary']['is_compliant']:
                    compliant += 1
                else:
                    non_compliant += 1
            else:
                errors += 1
            
            results_summary['results'].append({
                'file': os.path.basename(doc_path),
                'success': result['success'],
                'is_scientific': result.get('classification', {}).get('is_scientific', False),
                'is_compliant': result.get('summary', {}).get('is_compliant', False),
                'word_count': result.get('analysis', {}).get('word_count', 0),
                'paragraph_count': result.get('analysis', {}).get('paragraph_count', 0),
                'error': result.get('error')
            })
            
            if save_json and result['success']:
                output_name = f"output_{os.path.splitext(os.path.basename(doc_path))[0]}.json"
                processor.save_results(result, output_name)
            
        except Exception as e:
            print(f"\n❌ ERRO: {str(e)}")
            errors += 1
    
    # Resumo final
    print(f"\n\n{'='*70}")
    print("RESUMO FINAL")
    print(f"{'='*70}")
    print(f"Total: {len(documents)}")
    print(f"✓ Sucesso: {success} (Conformes: {compliant}, Não conformes: {non_compliant})")
    print(f"✗ Erros: {errors}")
    
    if save_json:
        with open("batch_summary.json", 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Resumo salvo: batch_summary.json")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Processa documentos em lote')
    parser.add_argument('--directory', '-d', default='./files', help='Pasta com documentos')
    parser.add_argument('--use-llm', action='store_true', help='Usa LLM para resumo')
    parser.add_argument('--no-save', action='store_true', help='Não salva JSONs')
    
    args = parser.parse_args()
    
    documents = find_documents(args.directory)
    
    if not documents:
        print(f"❌ Nenhum documento em '{args.directory}'")
        print("Formatos: PDF, JPG, PNG")
        sys.exit(1)
    
    print(f"Encontrados {len(documents)} documentos:")
    for doc in documents:
        print(f"  • {os.path.basename(doc)}")
    
    process_batch(documents, use_llm=args.use_llm, save_json=not args.no_save)


if __name__ == "__main__":
    main()
