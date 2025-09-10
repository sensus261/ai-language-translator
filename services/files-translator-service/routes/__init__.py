"""Initialize routes package."""

from .basic_routes import basic_bp
from .xml_routes import xml_bp

__all__ = ['basic_bp', 'xml_bp']
