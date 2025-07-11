"""
Module for splitting text into smaller chunks using different strategies.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# @docs: README_IA.md#chunking-agentic-avanzado-con-metadatos-enriquecidos-en-desarrollo
@dataclass
class ChunkMetadata:
    """Metadatos enriquecidos para un chunk de texto."""
    index: int
    char_start_index: int
    char_end_index: int
    semantic_title: Optional[str] = None
    summary: Optional[str] = None
    prev_chunk_id: Optional[Any] = None
    next_chunk_id: Optional[Any] = None
    semantic_overlap: Optional[str] = None
    # Campo para metadatos adicionales que puedan surgir
    additional_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Chunk:
    """Representa un chunk de texto con su contenido y metadatos."""
    content: str
    metadata: ChunkMetadata

    def __str__(self) -> str:
        return f"Chunk(index={self.metadata.index}, chars={self.metadata.char_start_index}-{self.metadata.char_end_index}, content='{self.content[:80]}...')"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto Chunk a un diccionario serializable."""
        return {
            "content": self.content,
            "metadata": self.metadata.__dict__
        }

try:
    from .config import CHUNK_SIZE, CHUNK_OVERLAP
except ImportError:
    from config import CHUNK_SIZE, CHUNK_OVERLAP

# ============================================================================
# ESTRATEGIAS DE CHUNKING (Strategy Pattern)
# ============================================================================

class ChunkingStrategy(ABC):
    """Clase base abstracta para estrategias de chunking."""
    
    @abstractmethod
    def chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        """Método abstracto para dividir el texto en Chunks enriquecidos."""
        pass

class CharacterChunkingStrategy(ChunkingStrategy):
    """Estrategia de chunking por caracteres (implementación original)."""
    
    def chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        if chunk_size <= 0:
            metadata = ChunkMetadata(index=0, char_start_index=0, char_end_index=len(text))
            return [Chunk(content=text, metadata=metadata)]

        result_chunks = []
        text_len = len(text)
        char_index = 0
        chunk_idx = 0

        while char_index < text_len:
            end_index = min(char_index + chunk_size, text_len)
            chunk_content = text[char_index:end_index]
            
            metadata = ChunkMetadata(
                index=chunk_idx,
                char_start_index=char_index,
                char_end_index=end_index - 1  # Inclusivo: último carácter incluido
            )
        
            logger.debug(f"CharacterChunking: Chunk {chunk_idx}, chars {char_index}-{end_index-1}, length={len(chunk_content)}")
            result_chunks.append(Chunk(content=chunk_content, metadata=metadata))
            
            char_index += chunk_size - chunk_overlap
            chunk_idx += 1
        
        logger.info(f"CharacterChunking: Generados {len(result_chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")
        return result_chunks

class WordChunkingStrategy(ChunkingStrategy):
    """Estrategia de chunking por palabras."""
    
    def chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        if chunk_size <= 0:
            metadata = ChunkMetadata(index=0, char_start_index=0, char_end_index=len(text))
            return [Chunk(content=text, metadata=metadata)]

        words = re.split(r'(\s+)', text) # Mantener espacios como elementos separados
        if not any(s.strip() for s in words): return []

        # Crear una lista de tuplas (palabra, longitud) para facilitar el manejo
        word_map = []
        current_pos = 0
        for word in words:
            word_map.append((word, current_pos))
            current_pos += len(word)

        result_chunks: List[Chunk] = []
        chunk_index = 0
        word_idx = 0

        while word_idx < len(word_map):
            start_word_idx = word_idx
            start_char_pos = word_map[start_word_idx][1]
            current_char_count = 0
            end_word_idx = word_idx

            # Construir el chunk hasta alcanzar chunk_size
            for i in range(start_word_idx, len(word_map)):
                word_content, _ = word_map[i]
                if current_char_count + len(word_content) > chunk_size and i > start_word_idx:
                    break
                current_char_count += len(word_content)
                end_word_idx = i + 1
            
            chunk_words = [word_map[i][0] for i in range(start_word_idx, end_word_idx)]
            chunk_content = "".join(chunk_words)
            end_char_pos = start_char_pos + len(chunk_content)

            metadata = ChunkMetadata(
                index=chunk_index,
                char_start_index=start_char_pos,
                char_end_index=end_char_pos  # Inclusivo: último carácter incluido
            )
        
            logger.debug(f"WordChunking: Chunk {chunk_index}, chars {start_char_pos}-{end_char_pos}, length={len(chunk_content)}, words={len(chunk_words)}")
            result_chunks.append(Chunk(content=chunk_content, metadata=metadata))
            chunk_index += 1

            # Calcular solapamiento
            if end_word_idx >= len(word_map):
                break

            overlap_char_count = 0
            overlap_word_count = 0
            for i in range(end_word_idx - 1, start_word_idx -1, -1):
                word_content, _ = word_map[i]
                if overlap_char_count + len(word_content) > chunk_overlap:
                    break
                overlap_char_count += len(word_content)
                overlap_word_count += 1

            word_idx = max(start_word_idx + 1, end_word_idx - overlap_word_count)

        logger.info(f"WordChunking: Generados {len(result_chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")
        return result_chunks

class SemanticChunkingStrategy(ChunkingStrategy):
    """Estrategia de chunking semántico basado en estructura natural del texto."""
    
    def chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        if chunk_size <= 0:
            metadata = ChunkMetadata(index=0, char_start_index=0, char_end_index=len(text) - 1)
            return [Chunk(content=text, metadata=metadata)]

        # 1. Dividir en unidades semánticas naturales
        semantic_units = self._split_into_semantic_units(text)
        logger.debug(f"SemanticChunking: Dividido en {len(semantic_units)} unidades semánticas")
        
        # 2. Agrupar unidades hasta alcanzar tamaño óptimo
        chunks = self._group_semantic_units(semantic_units, chunk_size, chunk_overlap, text)
        
        logger.info(f"SemanticChunking: Generados {len(chunks)} chunks (chunk_size={chunk_size}, overlap={chunk_overlap})")
        return chunks
    
    def _split_into_semantic_units(self, text: str) -> List[str]:
        """Divide el texto en unidades semánticas (párrafos, frases, etc.)."""
        units = []
        
        # Dividir por párrafos (doble salto de línea)
        paragraphs = re.split(r'\n\s*\n', text.strip())
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Si el párrafo es muy largo, dividir por frases
            if len(paragraph) > 800:  # Umbral para dividir párrafos largos
                sentences = self._split_into_sentences(paragraph)
                units.extend(sentences)
            else:
                units.append(paragraph.strip())
        
        return [unit for unit in units if unit.strip()]
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Divide un texto en frases usando puntuación fuerte."""
        # Patrones para detectar fin de frase
        sentence_endings = r'[.!?]+\s+'
        sentences = re.split(sentence_endings, text)
        
        # Reconstruir frases con su puntuación
        result = []
        parts = re.findall(r'[^.!?]*[.!?]+|[^.!?]+$', text)
        
        for part in parts:
            if part.strip():
                result.append(part.strip())
        
        return result
    
    def _group_semantic_units(self, units: List[str], target_size: int, overlap: int, original_text: str) -> List[Chunk]:
        """Agrupa unidades semánticas hasta alcanzar el tamaño objetivo."""
        if not units:
            return []
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for unit in units:
            unit_size = len(unit)
            
            # Si añadir esta unidad excede el tamaño objetivo y ya tenemos contenido
            if current_size + unit_size > target_size and current_chunk:
                # Finalizar chunk actual
                chunk_text = '\n\n'.join(current_chunk)
                
                # Calcular posición real en el texto original
                start_pos = original_text.find(current_chunk[0])
                end_pos = start_pos + len(chunk_text) - 1
                
                metadata = ChunkMetadata(
                    index=len(chunks),
                    char_start_index=start_pos,
                    char_end_index=end_pos
                )
                
                logger.debug(f"SemanticChunking: Chunk {len(chunks)}, chars {start_pos}-{end_pos}, length={len(chunk_text)}")
                chunks.append(Chunk(content=chunk_text, metadata=metadata))
                
                # Preparar siguiente chunk con overlap
                if overlap > 0 and current_chunk:
                    overlap_units = self._get_overlap_units(current_chunk, overlap)
                    current_chunk = overlap_units
                    current_size = sum(len(u) for u in overlap_units)
                else:
                    current_chunk = []
                    current_size = 0
            
            # Añadir la unidad actual
            current_chunk.append(unit)
            current_size += unit_size
        
        # Añadir el último chunk si tiene contenido
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            
            # Calcular posición real en el texto original
            start_pos = original_text.find(current_chunk[0])
            end_pos = start_pos + len(chunk_text) - 1
            
            metadata = ChunkMetadata(
                index=len(chunks),
                char_start_index=start_pos,
                char_end_index=end_pos
            )
            
            logger.debug(f"SemanticChunking: Chunk {len(chunks)}, chars {start_pos}-{end_pos}, length={len(chunk_text)}")
            chunks.append(Chunk(content=chunk_text, metadata=metadata))
        
        return chunks
    
    def _get_overlap_units(self, units: List[str], overlap_size: int) -> List[str]:
        """Obtiene las últimas unidades que caben en el tamaño de overlap."""
        overlap_units = []
        current_size = 0
        
        # Empezar desde el final y añadir unidades hasta alcanzar el overlap
        for unit in reversed(units):
            if current_size + len(unit) <= overlap_size:
                overlap_units.insert(0, unit)
                current_size += len(unit)
            else:
                break
        
        return overlap_units

class AgenticChunkingStrategy(ChunkingStrategy):
    """Estrategia de chunking agentic usando LLMs (Gemini API y LLM local)."""
    
    def __init__(self, 
                 llm_chunking_function: Optional[Callable[[str, int, int], List[Chunk]]] = None,
                 provider: str = "auto",
                 prefer_local: bool = True,
                 **provider_kwargs):
        """
        Inicializa la estrategia de chunking agentic.
        
        Args:
            llm_chunking_function: Función personalizada de chunking (opcional)
            provider: "gemini", "local", o "auto" para selección automática
            prefer_local: Si True, prefiere LLM local sobre Gemini (solo para "auto")
            **provider_kwargs: Argumentos adicionales para el proveedor específico
        """
        self.llm_chunking_function = llm_chunking_function
        self.provider = provider
        self.prefer_local = prefer_local
        self.provider_kwargs = provider_kwargs
        self._agentic_function = None
        
    def _get_agentic_function(self) -> Callable[[str, int, int], List[Chunk]]:
        """Obtiene la función de chunking agentic configurada."""
        if self._agentic_function is None:
            try:
                from .agentic_chunking import create_agentic_chunking_function
                self._agentic_function = create_agentic_chunking_function(
                    provider=self.provider,
                    prefer_local=self.prefer_local,
                    **self.provider_kwargs
                )
            except ImportError as e:
                print(f"Error: No se pudo importar el módulo de chunking agentic: {e}")
                raise
        return self._agentic_function
    
    def chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        """Realiza chunking agentic usando LLMs con fallback a chunking semántico."""
        
        logger.info(f"AgenticChunking: Iniciando con proveedor '{self.provider}' (prefer_local={self.prefer_local})")
        
        # Usar función personalizada si está disponible
        if self.llm_chunking_function:
            logger.info("AgenticChunking: Usando función personalizada")
            try:
                result = self.llm_chunking_function(text, chunk_size, chunk_overlap)
                if isinstance(result, list) and all(isinstance(c, Chunk) for c in result):
                    logger.info(f"AgenticChunking: Exitoso con función personalizada - {len(result)} chunks")
                    return result
                else:
                    logger.warning("AgenticChunking: La función personalizada no devolvió List[Chunk]. Usando método automático")
            except Exception as e:
                logger.warning(f"AgenticChunking: Error en función personalizada: {e}. Usando método automático")
        
        # Usar función automática del módulo agentic_chunking
        try:
            logger.info(f"AgenticChunking: Intentando con proveedor {self.provider}")
            agentic_func = self._get_agentic_function()
            result = agentic_func(text, chunk_size, chunk_overlap)
            logger.info(f"AgenticChunking: Exitoso con {self.provider} - {len(result)} chunks")
            return result
            
        except Exception as e:
            logger.warning(f"AgenticChunking: Error con {self.provider}: {e}")
            logger.info("AgenticChunking: Usando chunking semántico como fallback")
        
        # Fallback a chunking semántico
        semantic_strategy = SemanticChunkingStrategy()
        result = semantic_strategy.chunk(text, chunk_size, chunk_overlap)
        logger.info(f"AgenticChunking: Fallback semántico completado - {len(result)} chunks")
        return result

# ============================================================================
# CHUNKER PRINCIPAL CON STRATEGY PATTERN
# ============================================================================

class TextChunker:
    """Clase principal para realizar el chunking de texto."""
    def __init__(self, 
                 strategy: str = 'semantic', 
                 llm_chunking_function: Optional[Callable[..., List[Chunk]]] = None,
                 agentic_provider: str = "auto",
                 prefer_local: bool = True,
                 **agentic_kwargs):
        """
        Inicializa el TextChunker.
        
        Args:
            strategy: Estrategia de chunking ('character', 'word', 'semantic', 'agentic')
            llm_chunking_function: Función personalizada de chunking LLM
            agentic_provider: Proveedor para chunking agentic ('gemini', 'local', 'auto')
            prefer_local: Si prefiere LLM local sobre Gemini (solo para 'auto')
            **agentic_kwargs: Argumentos adicionales para el proveedor agentic
        """
        self.llm_chunking_function = llm_chunking_function
        self.agentic_provider = agentic_provider
        self.prefer_local = prefer_local
        self.agentic_kwargs = agentic_kwargs
        self._strategy: ChunkingStrategy = None # type: ignore
        self.set_strategy(strategy)

    def set_strategy(self, strategy: str):
        """Establece la estrategia de chunking a utilizar."""
        if strategy in ('character', 'caracteres'):
            self._strategy = CharacterChunkingStrategy()
        elif strategy in ('word', 'palabras'):
            self._strategy = WordChunkingStrategy()
        elif strategy in ('semantic', 'semantico'):
            self._strategy = SemanticChunkingStrategy()
        elif strategy == 'agentic':
            self._strategy = AgenticChunkingStrategy(
                llm_chunking_function=self.llm_chunking_function,
                provider=self.agentic_provider,
                prefer_local=self.prefer_local,
                **self.agentic_kwargs
            )
        else:
            raise ValueError(f"Estrategia '{strategy}' no soportada.")
        self.strategy_name = strategy

    def set_agentic_function(self, llm_function: Callable[..., List[Chunk]]):
        """Establece la función de chunking para la estrategia agentic."""
        self.llm_chunking_function = llm_function
        if self.strategy_name == 'agentic':
            # Re-instanciar la estrategia para asegurar que usa la nueva función
            self._strategy = AgenticChunkingStrategy(
                llm_chunking_function=llm_function,
                provider=self.agentic_provider,
                prefer_local=self.prefer_local,
                **self.agentic_kwargs
            )
    
    def configure_agentic(self, 
                         provider: str = "auto", 
                         prefer_local: bool = True, 
                         **kwargs):
        """
        Configura los parámetros para chunking agentic.
        
        Args:
            provider: 'gemini', 'local', o 'auto'
            prefer_local: Si prefiere LLM local (solo para 'auto')
            **kwargs: Argumentos específicos del proveedor (api_key, api_url, etc.)
        """
        self.agentic_provider = provider
        self.prefer_local = prefer_local
        self.agentic_kwargs.update(kwargs)
        
        # Si ya estamos usando estrategia agentic, re-configurar
        if self.strategy_name == 'agentic':
            self.set_strategy('agentic')

    def chunk(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Chunk]:
        """Realiza el chunking del texto usando la estrategia seleccionada."""
        return self._strategy.chunk(text, chunk_size, chunk_overlap)

    def get_current_strategy(self) -> str:
        """Retorna la estrategia actual."""
        return self.strategy_name

# ============================================================================
# FUNCIÓN DE CONVENIENCIA
# ============================================================================

def chunk_text(text: str, 
               strategy: str = 'semantic', 
               chunk_size: int = 1000, 
               chunk_overlap: int = 200, 
               llm_chunking_function: Optional[Callable[..., List[Chunk]]] = None,
               agentic_provider: str = "auto",
               prefer_local: bool = True,
               **agentic_kwargs) -> List[Chunk]:
    """
    Función de conveniencia para chunking rápido con soporte completo para chunking agentic.
    
    Args:
        text: Texto a dividir en chunks
        strategy: Estrategia de chunking ('character', 'word', 'semantic', 'agentic')
        chunk_size: Tamaño aproximado de cada chunk
        chunk_overlap: Overlap entre chunks
        llm_chunking_function: Función personalizada de chunking LLM
        agentic_provider: Proveedor para chunking agentic ('gemini', 'local', 'auto')
        prefer_local: Si prefiere LLM local sobre Gemini (solo para 'auto')
        **agentic_kwargs: Argumentos adicionales para el proveedor agentic
        
    Returns:
        Lista de objetos Chunk con metadatos enriquecidos
        
    Examples:
        # Chunking semántico básico
        chunks = chunk_text(text, strategy='semantic')
        
        # Chunking agentic con LLM local
        chunks = chunk_text(text, strategy='agentic', agentic_provider='local')
        
        # Chunking agentic con Gemini
        chunks = chunk_text(text, strategy='agentic', agentic_provider='gemini', api_key='tu_api_key')
        
        # Chunking agentic automático (intenta local primero, luego Gemini)
        chunks = chunk_text(text, strategy='agentic', agentic_provider='auto', prefer_local=True)
    """
    chunker = TextChunker(
        strategy=strategy, 
        llm_chunking_function=llm_chunking_function,
        agentic_provider=agentic_provider,
        prefer_local=prefer_local,
        **agentic_kwargs
    )
    return chunker.chunk(text, chunk_size, chunk_overlap)
