"""
Ontology module for the Bookstore Management System.

This module handles the creation, management, and interaction with the knowledge
representation framework using OWL ontologies through Owlready2 and SWRL rules.
"""

from .advanced_bookstore_ontology import onto as bookstore_ontology
from .advanced_bookstore_ontology import save_ontology_to_owl, validate_ontology
from .bookstore_rules import load_rules, validate_rules

__all__ = [
    'bookstore_ontology', 
    'save_ontology_to_owl', 
    'validate_ontology', 
    'load_rules',
    'validate_rules'
]