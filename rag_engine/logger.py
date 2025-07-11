"""
Sistema de logging unificado para RAG Engine.
"""
import logging
import sys

def setup_logger(name: str = "rag_engine", level: int = logging.INFO):
    """
    Configura el logger para RAG Engine.
    
    Args:
        name: Nombre del logger
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formato simple y claro
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

# Logger por defecto
logger = setup_logger()

def set_debug_mode(enabled: bool = True):
    """Activa/desactiva el modo debug."""
    level = logging.DEBUG if enabled else logging.INFO
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
    
    if enabled:
        logger.debug("Modo DEBUG activado")
    else:
        logger.info("Modo DEBUG desactivado")
