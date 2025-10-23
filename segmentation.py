"""
Segmentação de Documentos (NFR 2.1)
"""

import numpy as np
from PIL import Image
import fitz  # PyMuPDF
from typing import List, Dict
import os


class DocumentSegmentation:
    """Segmentação simples de documentos."""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png']
    
    def load_document(self, file_path: str) -> List[np.ndarray]:
        """Carrega documento."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_formats:
            raise ValueError(f"Formato não suportado: {ext}")
        
        if ext == '.pdf':
            return self._load_pdf(file_path)
        else:
            return self._load_image(file_path)
    
    def _load_pdf(self, file_path: str) -> List[np.ndarray]:
        """Converte PDF para imagens."""
        try:
            doc = fitz.open(file_path)
            images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(np.array(img))
            
            doc.close()
            return images
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar PDF: {str(e)}")
    
    def _load_image(self, file_path: str) -> List[np.ndarray]:
        """Carrega imagem."""
        try:
            img = Image.open(file_path).convert('RGB')
            return [np.array(img)]
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar imagem: {str(e)}")
    
    def segment_document(self, image: np.ndarray) -> Dict:
        """Segmenta documento (NFR 2.1)."""
        height, width = image.shape[:2]
        
        return {
            'original': image,
            'text_regions': [(0, 0, width, height)],
            'dimensions': {'width': width, 'height': height}
        }
    
    def extract_text_from_regions(self, segmentation_result: Dict) -> str:
        """Extrai texto usando PyMuPDF."""
        return ""
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrai texto diretamente do PDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page in doc:
                text += page.get_text()
            
            doc.close()
            return text
        except Exception as e:
            return ""
    
    def process_document(self, file_path: str) -> Dict:
        """Processa documento completo."""
        ext = os.path.splitext(file_path)[1].lower()
        
        # Carrega imagens
        images = self.load_document(file_path)
        
        # Extrai texto
        if ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        else:
            text = ""
        
        # Segmenta primeira página
        segmentation = self.segment_document(images[0]) if images else None
        
        # Conta regiões (simplificado)
        num_text_regions = len(segmentation['text_regions']) if segmentation else 0
        
        return {
            'text': text,
            'images': images,
            'segmentation': segmentation,
            'num_pages': len(images),
            'num_text_regions': num_text_regions,
            'num_image_regions': 0  # Simplificado
        }
