"""
Omotenashi - Luxury Hospitality AI Concierge Package
====================================================

This package contains the core components of the Omotenashi AI concierge system.
"""

from .agent import OmotenaashiAgent, AgentResponse
from .tools import (
    property_info,
    get_recommendations, 
    make_reservation,
    book_spa,
    modify_checkin_checkout,
    ALL_TOOLS,
    KNOWLEDGE_BASE
)
from .cli import OmotenaashiCLI

__version__ = "0.1.0"
__all__ = [
    "OmotenaashiAgent",
    "AgentResponse",
    "property_info",
    "get_recommendations",
    "make_reservation", 
    "book_spa",
    "modify_checkin_checkout",
    "OmotenaashiCLI"
] 