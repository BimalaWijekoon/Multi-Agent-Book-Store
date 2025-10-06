"""
Communication module for the Bookstore Management System.

This module handles message passing, protocols, and communication mechanisms
between agents in the multi-agent simulation.
"""

from .message_bus import (
    Message,
    MessageBus,
    MessageType,
    MessageStatus,
    AgentType
)

__all__ = [
    'Message',
    'MessageBus',
    'MessageType',
    'MessageStatus',
    'AgentType'
]