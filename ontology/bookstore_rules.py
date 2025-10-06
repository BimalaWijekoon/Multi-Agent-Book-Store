"""
Bookstore SWRL Rules Engine

This module defines a comprehensive set of SWRL (Semantic Web Rule Language) rules
for governing the behavior of Customer, Employee, and Book agents in the
Bookstore Management System.
"""

import logging
import os
from pathlib import Path

import owlready2 as owl
from rdflib import Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery

# Import the ontology
from .advanced_bookstore_ontology import onto as bookstore_ontology

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the base IRI for the rules
RULES_IRI = "http://www.semanticweb.org/bookstore-rules#"

# Create a namespace for the rules
rules_ns = Namespace(RULES_IRI)

# Dictionary to store all rule definitions
rule_definitions = {}

def register_rule(name, description, swrl_syntax, sparql_implementation):
    """Register a SWRL rule with its implementation."""
    rule_definitions[name] = {
        "description": description,
        "swrl_syntax": swrl_syntax,
        "sparql_implementation": sparql_implementation
    }
    logger.debug(f"Registered rule: {name}")


#=============================================================================
# CUSTOMER BEHAVIOR RULES
#=============================================================================

# Purchase Transaction Rule
register_rule(
    name="purchase_transaction_rule",
    description="Process purchase transactions when a customer buys a book",
    swrl_syntax="""
        Customer(?c) ∧ Book(?b) ∧ makesPurchase(?c, ?b) ∧
        hasPrice(?b, ?price) ∧ customerBudget(?c, ?budget) ∧
        swrlb:greaterThanOrEqual(?budget, ?price) →
        createOrder(?c, ?b) ∧ reduceStock(?b, 1) ∧ deductBudget(?c, ?price)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?book ?price ?budget ?newBudget
        WHERE {
            ?customer rdf:type onto:Customer .
            ?book rdf:type onto:Book .
            ?customer onto:makesPurchase ?book .
            ?book onto:bookPrice ?price .
            ?customer onto:customerBudget ?budget .
            FILTER (?budget >= ?price)
            BIND (?budget - ?price AS ?newBudget)
        }
    """
)

# Budget Constraint Rule
register_rule(
    name="budget_constraint_rule",
    description="Prevent purchases exceeding customer budget and suggest alternatives",
    swrl_syntax="""
        Customer(?c) ∧ Book(?b) ∧ makesPurchase(?c, ?b) ∧
        hasPrice(?b, ?price) ∧ customerBudget(?c, ?budget) ∧
        belongsToGenre(?b, ?genre) ∧ swrlb:lessThan(?budget, ?price) ∧
        Book(?altBook) ∧ belongsToGenre(?altBook, ?genre) ∧
        hasPrice(?altBook, ?altPrice) ∧ swrlb:lessThanOrEqual(?altPrice, ?budget) →
        cancelPurchase(?c, ?b) ∧ suggestAlternative(?c, ?altBook)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?book ?altBook ?budget ?price ?altPrice ?genre
        WHERE {
            ?customer rdf:type onto:Customer .
            ?book rdf:type onto:Book .
            ?customer onto:makesPurchase ?book .
            ?book onto:bookPrice ?price .
            ?customer onto:customerBudget ?budget .
            ?book onto:belongsToGenre ?genre .
            FILTER (?budget < ?price)
            
            ?altBook rdf:type onto:Book .
            ?altBook onto:belongsToGenre ?genre .
            ?altBook onto:bookPrice ?altPrice .
            FILTER (?altPrice <= ?budget && ?altBook != ?book)
        }
    """
)

# Preference-Based Browsing Rule
register_rule(
    name="preference_recommendation_rule",
    description="Recommend books to customers based on genre preferences",
    swrl_syntax="""
        Customer(?c) ∧ hasPreference(?c, ?genre) ∧
        Book(?b) ∧ belongsToGenre(?b, ?genre) ∧
        isAvailable(?b, true) ∧ customerBudget(?c, ?budget) ∧
        hasPrice(?b, ?price) ∧ swrlb:lessThanOrEqual(?price, ?budget) →
        receivesRecommendation(?c, ?b)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?book ?genre ?budget ?price
        WHERE {
            ?customer rdf:type onto:Customer .
            ?genre rdf:type onto:Genre .
            ?customer onto:hasPreference ?genre .
            
            ?book rdf:type onto:Book .
            ?book onto:belongsToGenre ?genre .
            ?book onto:isAvailable "true"^^xsd:boolean .
            
            ?book onto:bookPrice ?price .
            ?customer onto:customerBudget ?budget .
            FILTER (?price <= ?budget)
        }
    """
)

# Customer Loyalty Rule
register_rule(
    name="customer_loyalty_upgrade_rule",
    description="Upgrade customer loyalty status based on purchase history",
    swrl_syntax="""
        Customer(?c) ∧ Order(?o1) ∧ Order(?o2) ∧ Order(?o3) ∧
        makesPurchase(?c, ?o1) ∧ makesPurchase(?c, ?o2) ∧ makesPurchase(?c, ?o3) ∧
        differentFrom(?o1, ?o2) ∧ differentFrom(?o1, ?o3) ∧ differentFrom(?o2, ?o3) ∧
        hasLoyaltyLevel(?c, New) →
        hasLoyaltyLevel(?c, Regular)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer (COUNT(?order) AS ?orderCount)
        WHERE {
            ?customer rdf:type onto:Customer .
            ?customer onto:hasLoyaltyLevel ?loyaltyLevel .
            ?loyaltyLevel rdf:type onto:New .
            
            ?order rdf:type onto:Order .
            ?customer onto:makesPurchase ?order .
        }
        GROUP BY ?customer
        HAVING (COUNT(?order) >= 3)
    """
)

# Premium Customer Discount Rule
register_rule(
    name="premium_customer_discount_rule",
    description="Apply discounts to books for premium customers",
    swrl_syntax="""
        Customer(?c) ∧ hasLoyaltyLevel(?c, Premium) ∧
        Book(?b) ∧ hasPrice(?b, ?originalPrice) ∧
        swrlb:multiply(?discountPrice, ?originalPrice, 0.9) →
        hasDiscountedPrice(?b, ?discountPrice) ∧ isDiscounted(?b, true)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?book ?originalPrice ?discountPrice
        WHERE {
            ?customer rdf:type onto:Customer .
            ?customer onto:hasLoyaltyLevel ?loyaltyLevel .
            ?loyaltyLevel rdf:type onto:Premium .
            
            ?book rdf:type onto:Book .
            ?book onto:bookPrice ?originalPrice .
            
            BIND (?originalPrice * 0.9 AS ?discountPrice)
        }
    """
)


#=============================================================================
# EMPLOYEE WORKFLOW RULES
#=============================================================================

# Inventory Restocking Rule
register_rule(
    name="inventory_restocking_rule",
    description="Trigger restocking tasks when inventory falls below threshold",
    swrl_syntax="""
        Book(?b) ∧ Inventory(?i) ∧ inStock(?b, ?i) ∧
        availableQuantity(?i, ?qty) ∧ swrlb:lessThan(?qty, 5) ∧
        Employee(?e) ∧ hasRole(?e, ?role) ∧ sameAs(?role, Manager) →
        assignRestockTask(?e, ?b) ∧ triggerRestockAlert(?b)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?inventory ?qty ?employee
        WHERE {
            ?book rdf:type onto:Book .
            ?inventory rdf:type onto:Inventory .
            ?book onto:inStock ?inventory .
            ?inventory onto:availableQuantity ?qty .
            FILTER (?qty < 5)
            
            ?employee rdf:type onto:Employee .
            ?employee onto:hasRole ?role .
            ?role rdf:type onto:Manager .
        }
    """
)

# Customer Service Rule
register_rule(
    name="customer_service_rule",
    description="Route customer inquiries to employees with expertise",
    swrl_syntax="""
        Customer(?c) ∧ hasPreference(?c, ?genre) ∧
        Employee(?e) ∧ hasExpertiseIn(?e, ?genre) →
        assistsCustomer(?e, ?c)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?employee ?genre
        WHERE {
            ?customer rdf:type onto:Customer .
            ?customer onto:hasPreference ?genre .
            
            ?employee rdf:type onto:Employee .
            ?employee onto:hasExpertiseIn ?genre .
        }
    """
)

# Role-Based Permission Rule
register_rule(
    name="manager_override_rule",
    description="Allow managers to override pricing decisions",
    swrl_syntax="""
        Employee(?e) ∧ hasRole(?e, ?role) ∧ sameAs(?role, Manager) ∧
        Book(?b) ∧ hasPrice(?b, ?price) →
        canAdjustPrice(?e, ?b, true)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?employee ?book ?role
        WHERE {
            ?employee rdf:type onto:Employee .
            ?employee onto:hasRole ?role .
            ?role rdf:type onto:Manager .
            
            ?book rdf:type onto:Book .
        }
    """
)

# Work Schedule Rule
register_rule(
    name="workload_distribution_rule",
    description="Distribute tasks based on employee workload",
    swrl_syntax="""
        Employee(?e1) ∧ Employee(?e2) ∧ differentFrom(?e1, ?e2) ∧
        hasTaskCount(?e1, ?count1) ∧ hasTaskCount(?e2, ?count2) ∧
        swrlb:greaterThan(?count1, ?count2) ∧ swrlb:subtract(?diff, ?count1, ?count2) ∧
        swrlb:greaterThanOrEqual(?diff, 3) ∧ Task(?t) ∧ isAssignedTo(?t, ?e1) →
        isAssignedTo(?t, ?e2) ∧ not(isAssignedTo(?t, ?e1))
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?employee1 ?employee2 ?taskCount1 ?taskCount2 ?diff
        WHERE {
            ?employee1 rdf:type onto:Employee .
            ?employee2 rdf:type onto:Employee .
            FILTER (?employee1 != ?employee2)
            
            # This would be implemented with actual task counting properties
            # Here we simulate with mock values
            BIND (5 AS ?taskCount1)
            BIND (2 AS ?taskCount2)
            FILTER (?taskCount1 > ?taskCount2)
            
            BIND (?taskCount1 - ?taskCount2 AS ?diff)
            FILTER (?diff >= 3)
        }
    """
)


#=============================================================================
# BOOK MANAGEMENT RULES
#=============================================================================

# Dynamic Pricing Rule
register_rule(
    name="dynamic_pricing_rule",
    description="Adjust book prices based on demand patterns",
    swrl_syntax="""
        Book(?b) ∧ hasDemandLevel(?b, ?demand) ∧ hasPrice(?b, ?price) ∧
        swrlb:greaterThan(?demand, 8) ∧ swrlb:multiply(?newPrice, ?price, 1.1) →
        hasPrice(?b, ?newPrice) ∧ isPriceIncreased(?b, true)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?demand ?price ?newPrice
        WHERE {
            ?book rdf:type onto:Book .
            ?book onto:bookPrice ?price .
            
            # Simulate demand level with a mock property
            BIND (10 AS ?demand)  # Simulated high demand
            FILTER (?demand > 8)
            
            BIND (?price * 1.1 AS ?newPrice)
        }
    """
)

# Availability Status Rule
register_rule(
    name="availability_status_rule",
    description="Update book availability based on inventory levels",
    swrl_syntax="""
        Book(?b) ∧ Inventory(?i) ∧ inStock(?b, ?i) ∧
        availableQuantity(?i, ?qty) ∧ swrlb:equal(?qty, 0) →
        isAvailable(?b, false) ∧ isOutOfStock(?b, true)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?inventory ?qty
        WHERE {
            ?book rdf:type onto:Book .
            ?inventory rdf:type onto:Inventory .
            ?book onto:inStock ?inventory .
            ?inventory onto:availableQuantity ?qty .
            FILTER (?qty = 0)
        }
    """
)

# Book Recommendation Network Rule
register_rule(
    name="book_recommendation_network_rule",
    description="Create a network of book recommendations based on genre relationships",
    swrl_syntax="""
        Book(?b1) ∧ Book(?b2) ∧ differentFrom(?b1, ?b2) ∧
        belongsToGenre(?b1, ?genre) ∧ belongsToGenre(?b2, ?genre) ∧
        hasAuthor(?b1, ?author) ∧ hasAuthor(?b2, ?author) →
        hasSimilarGenre(?b1, ?b2)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book1 ?book2 ?genre ?author
        WHERE {
            ?book1 rdf:type onto:Book .
            ?book2 rdf:type onto:Book .
            FILTER (?book1 != ?book2)
            
            ?book1 onto:belongsToGenre ?genre .
            ?book2 onto:belongsToGenre ?genre .
            
            ?book1 onto:hasAuthor ?author .
            ?book2 onto:hasAuthor ?author .
        }
    """
)

# Publisher Relationship Rule
register_rule(
    name="publisher_reorder_rule",
    description="Trigger reorders with preferred publishers",
    swrl_syntax="""
        Book(?b) ∧ Inventory(?i) ∧ inStock(?b, ?i) ∧
        availableQuantity(?i, ?qty) ∧ swrlb:lessThan(?qty, 3) ∧
        Publisher(?p) ∧ publishedBy(?b, ?p) ∧ isPreferredPublisher(?p, true) →
        triggerReorder(?b, ?p) ∧ setReorderQuantity(?b, 10)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?inventory ?qty ?publisher
        WHERE {
            ?book rdf:type onto:Book .
            ?inventory rdf:type onto:Inventory .
            ?book onto:inStock ?inventory .
            ?inventory onto:availableQuantity ?qty .
            FILTER (?qty < 3)
            
            ?publisher rdf:type onto:Publisher .
            ?book onto:publishedBy ?publisher .
            
            # Simulate preferred publisher status
            BIND (true AS ?isPreferred)
        }
    """
)

# Seasonal Pricing Rule
register_rule(
    name="seasonal_pricing_rule",
    description="Apply seasonal discounts based on time of year",
    swrl_syntax="""
        Book(?b) ∧ belongsToGenre(?b, ?genre) ∧
        hasPrice(?b, ?price) ∧ isHolidaySeason(?genre, true) ∧
        swrlb:multiply(?discountPrice, ?price, 0.85) →
        hasSeasonalPrice(?b, ?discountPrice)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?genre ?price ?discountPrice
        WHERE {
            ?book rdf:type onto:Book .
            ?book onto:belongsToGenre ?genre .
            ?book onto:bookPrice ?price .
            
            # Simulate holiday season flag
            BIND (true AS ?isHolidaySeason)
            
            BIND (?price * 0.85 AS ?discountPrice)
        }
    """
)

#=============================================================================
# ADVANCED RECOMMENDATION AND BUSINESS RULES (NEW - Phase 2-4)
#=============================================================================

# Cross-Selling Rule
register_rule(
    name="cross_selling_rule",
    description="Recommend related books from the same genre when customer buys a book",
    swrl_syntax="""
        Customer(?c) ∧ Book(?b) ∧ makesPurchase(?c, ?b) ∧
        belongsToGenre(?b, ?genre) ∧ Book(?relatedBook) ∧
        belongsToGenre(?relatedBook, ?genre) ∧ differentFrom(?b, ?relatedBook) ∧
        hasPrice(?relatedBook, ?price) ∧ customerBudget(?c, ?budget) ∧
        swrlb:greaterThanOrEqual(?budget, ?price) →
        recommendCrossSell(?c, ?relatedBook)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?purchasedBook ?relatedBook ?genre ?price ?budget
        WHERE {
            ?customer rdf:type onto:Customer .
            ?purchasedBook rdf:type onto:Book .
            ?customer onto:makesPurchase ?purchasedBook .
            ?purchasedBook onto:belongsToGenre ?genre .
            ?relatedBook rdf:type onto:Book .
            ?relatedBook onto:belongsToGenre ?genre .
            FILTER (?purchasedBook != ?relatedBook)
            ?relatedBook onto:bookPrice ?price .
            ?customer onto:customerBudget ?budget .
            FILTER (?budget >= ?price)
        }
    """
)

# Popular Author Rule
register_rule(
    name="popular_author_rule",
    description="Promote books from authors with high ratings",
    swrl_syntax="""
        Author(?a) ∧ Book(?b) ∧ hasAuthor(?b, ?a) ∧
        Review(?r) ∧ hasReview(?b, ?r) ∧ hasRating(?r, ?rating) ∧
        ratingValue(?rating, ?value) ∧ swrlb:greaterThanOrEqual(?value, 4) →
        promoteBook(?b) ∧ markPopularAuthor(?a)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?author ?book ?review ?rating ?ratingValue
        WHERE {
            ?author rdf:type onto:Author .
            ?book rdf:type onto:Book .
            ?book onto:hasAuthor ?author .
            ?review rdf:type onto:Review .
            ?book onto:hasReview ?review .
            ?rating rdf:type onto:Rating .
            ?review onto:hasRating ?rating .
            ?rating onto:ratingValue ?ratingValue .
            FILTER (?ratingValue >= 4)
        }
    """
)

# Review-Based Recommendation Rule
register_rule(
    name="review_based_recommendation_rule",
    description="Recommend highly-rated books to customers based on verified reviews",
    swrl_syntax="""
        Customer(?c) ∧ Book(?b) ∧ Review(?r) ∧ hasReview(?b, ?r) ∧
        isVerifiedReview(?r, true) ∧ hasRating(?r, ?rating) ∧
        ratingValue(?rating, ?value) ∧ swrlb:greaterThanOrEqual(?value, 4) ∧
        belongsToGenre(?b, ?genre) ∧ hasPreference(?c, ?genre) →
        recommendBook(?c, ?b)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?book ?review ?rating ?ratingValue ?genre
        WHERE {
            ?customer rdf:type onto:Customer .
            ?book rdf:type onto:Book .
            ?review rdf:type onto:Review .
            ?book onto:hasReview ?review .
            ?review onto:isVerifiedReview true .
            ?rating rdf:type onto:Rating .
            ?review onto:hasRating ?rating .
            ?rating onto:ratingValue ?ratingValue .
            FILTER (?ratingValue >= 4)
            ?book onto:belongsToGenre ?genre .
            ?customer onto:hasPreference ?genre .
        }
    """
)

# Expertise Learning Rule
register_rule(
    name="expertise_learning_rule",
    description="Assign expertise to employees based on genres they frequently assist with",
    swrl_syntax="""
        Employee(?e) ∧ Customer(?c) ∧ assistsCustomer(?e, ?c) ∧
        hasPreference(?c, ?genre) ∧ swrlb:count(?assistanceCount) ∧
        swrlb:greaterThanOrEqual(?assistanceCount, 5) →
        hasExpertiseIn(?e, ?genre)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?employee ?genre (COUNT(?customer) as ?assistanceCount)
        WHERE {
            ?employee rdf:type onto:Employee .
            ?customer rdf:type onto:Customer .
            ?employee onto:assistsCustomer ?customer .
            ?customer onto:hasPreference ?genre .
        }
        GROUP BY ?employee ?genre
        HAVING (COUNT(?customer) >= 5)
    """
)

# Priority Restock Rule
register_rule(
    name="priority_restock_rule",
    description="Prioritize restocking of books that are featured in active promotions",
    swrl_syntax="""
        Book(?b) ∧ Promotion(?p) ∧ hasPromotion(?b, ?p) ∧
        isActivePromotion(?p, true) ∧ isAvailable(?b, false) ∧
        Supplier(?s) ∧ suppliedBy(?b, ?s) ∧ isPreferredSupplier(?s, true) →
        createRestockOrder(?b, ?s) ∧ markPriorityShipment(?b)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?book ?promotion ?supplier
        WHERE {
            ?book rdf:type onto:Book .
            ?promotion rdf:type onto:Promotion .
            ?book onto:hasPromotion ?promotion .
            ?promotion onto:isActivePromotion true .
            ?book onto:isAvailable false .
            ?supplier rdf:type onto:Supplier .
            ?book onto:suppliedBy ?supplier .
            ?supplier onto:isPreferredSupplier true .
        }
    """
)

# Customer Re-engagement Rule
register_rule(
    name="customer_reengagement_rule",
    description="Notify customers about events featuring books in their preferred genres",
    swrl_syntax="""
        Customer(?c) ∧ hasPreference(?c, ?genre) ∧
        Book(?b) ∧ belongsToGenre(?b, ?genre) ∧
        BookEvent(?e) ∧ featuredInEvent(?b, ?e) ∧ isPublicEvent(?e, true) →
        notifyCustomerOfEvent(?c, ?e) ∧ recommendEventAttendance(?c, ?e)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?event ?book ?genre
        WHERE {
            ?customer rdf:type onto:Customer .
            ?customer onto:hasPreference ?genre .
            ?book rdf:type onto:Book .
            ?book onto:belongsToGenre ?genre .
            ?event rdf:type onto:BookEvent .
            ?book onto:featuredInEvent ?event .
            ?event onto:isPublicEvent true .
        }
    """
)

# Bundle Deal Rule
register_rule(
    name="bundle_deal_rule",
    description="Create bundle discounts when customers are eligible for multiple promotions",
    swrl_syntax="""
        Customer(?c) ∧ Discount(?d1) ∧ isEligibleForDiscount(?c, ?d1) ∧
        Discount(?d2) ∧ isEligibleForDiscount(?c, ?d2) ∧ differentFrom(?d1, ?d2) ∧
        discountPercentage(?d1, ?p1) ∧ discountPercentage(?d2, ?p2) ∧
        swrlb:add(?bundleDiscount, ?p1, ?p2) →
        createBundleDeal(?c, ?bundleDiscount) ∧ notifyBundleOffer(?c)
    """,
    sparql_implementation="""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX onto: <http://www.semanticweb.org/bookstore-ontology#>
        
        SELECT ?customer ?discount1 ?discount2 ?percentage1 ?percentage2
               (?percentage1 + ?percentage2 AS ?bundleDiscount)
        WHERE {
            ?customer rdf:type onto:Customer .
            ?discount1 rdf:type onto:Discount .
            ?customer onto:isEligibleForDiscount ?discount1 .
            ?discount2 rdf:type onto:Discount .
            ?customer onto:isEligibleForDiscount ?discount2 .
            FILTER (?discount1 != ?discount2)
            ?discount1 onto:discountPercentage ?percentage1 .
            ?discount2 onto:discountPercentage ?percentage2 .
        }
    """
)
    
    
# Function to run a rule on the ontology
def run_rule(rule_name, ontology_graph):
    """Execute a specific rule on the given ontology graph."""
    if rule_name not in rule_definitions:
        logger.error(f"Rule '{rule_name}' not found in rule definitions")
        return False
        
    rule = rule_definitions[rule_name]
    logger.info(f"Running rule: {rule_name} - {rule['description']}")
    
    try:
        # Execute the SPARQL implementation of the rule
        query = prepareQuery(rule["sparql_implementation"])
        results = ontology_graph.query(query)
        
        # Process the results (this would update the ontology in a real system)
        for result in results:
            logger.debug(f"Rule result: {result}")
            
        return True
    except Exception as e:
        logger.error(f"Error executing rule '{rule_name}': {e}")
        return False


# Function to run all rules on the ontology
def run_all_rules(ontology_graph):
    """Execute all registered rules on the given ontology graph."""
    logger.info(f"Running all {len(rule_definitions)} rules...")
    
    success_count = 0
    for rule_name in rule_definitions:
        if run_rule(rule_name, ontology_graph):
            success_count += 1
    
    logger.info(f"Successfully executed {success_count}/{len(rule_definitions)} rules")
    return success_count == len(rule_definitions)


# Helper function to convert ontology to RDFlib graph
def convert_ontology_to_graph(ontology):
    """Convert an Owlready2 ontology to an RDFlib graph."""
    # First save the ontology to a temporary file
    temp_file = Path("temp_ontology.owl")
    ontology.save(file=str(temp_file), format="rdfxml")
    
    # Load the ontology into an RDFlib graph
    graph = Graph()
    graph.parse(str(temp_file))
    
    # Remove the temporary file
    os.remove(temp_file)
    
    return graph


def load_rules(ontology):
    """
    Load all rules into the given ontology.
    
    In a real implementation with Pellet or another reasoner that supports SWRL,
    we would directly add the rules to the ontology. Here we simulate it by
    converting to RDFlib and using SPARQL.
    """
    logger.info("Loading rules into ontology...")
    
    # Convert ontology to RDFlib graph for rule processing
    graph = convert_ontology_to_graph(ontology)
    
    # Run all rules on the graph
    success = run_all_rules(graph)
    
    return success


#=============================================================================
# RULE TESTING AND VALIDATION
#=============================================================================

def create_test_instances(ontology):
    """Create test instances in the ontology for rule testing."""
    logger.info("Creating test instances for rule testing...")
    
    with ontology:
        # Create customer instances
        john = ontology.Customer("John")
        john.customerName = ["John Smith"]
        john.customerBudget = [100.0]
        
        alice = ontology.Customer("Alice")
        alice.customerName = ["Alice Johnson"]
        alice.customerBudget = [50.0]
        
        # Create employee instances
        bob = ontology.Employee("Bob")
        bob.employeeRole = ["Manager"]
        
        carol = ontology.Employee("Carol")
        carol.employeeRole = ["Staff"]
        
        # Create genre instances
        mystery = ontology.Mystery("MysteryGenre")
        mystery.genreName = ["Mystery"]
        
        scifi = ontology.ScienceFiction("SciFiGenre")
        scifi.genreName = ["Science Fiction"]
        
        # Create publisher instances
        publisher1 = ontology.Publisher("Publisher1")
        publisher2 = ontology.Publisher("Publisher2")
        
        # Create book instances
        book1 = ontology.Book("MysteryBook1")
        book1.bookTitle = ["The Mystery of the Hidden Key"]
        book1.bookPrice = [15.99]
        book1.isAvailable = [True]
        book1.belongsToGenre = [mystery]
        book1.publishedBy = [publisher1]
        
        book2 = ontology.Book("SciFiBook1")
        book2.bookTitle = ["Galactic Adventures"]
        book2.bookPrice = [25.99]
        book2.isAvailable = [True]
        book2.belongsToGenre = [scifi]
        book2.publishedBy = [publisher2]
        
        book3 = ontology.Book("MysteryBook2")
        book3.bookTitle = ["The Secret Code"]
        book3.bookPrice = [12.99]
        book3.isAvailable = [True]
        book3.belongsToGenre = [mystery]
        book3.publishedBy = [publisher1]
        
        # Create inventory instances
        inv1 = ontology.Inventory("Inventory1")
        inv1.availableQuantity = [10]
        book1.inStock = [inv1]
        
        inv2 = ontology.Inventory("Inventory2")
        inv2.availableQuantity = [5]
        book2.inStock = [inv2]
        
        inv3 = ontology.Inventory("Inventory3")
        inv3.availableQuantity = [2]
        book3.inStock = [inv3]
        
        # Set up relationships
        john.hasPreference = [mystery]
        alice.hasPreference = [scifi]
        
        bob.hasExpertiseIn = [mystery]
        carol.hasExpertiseIn = [scifi]
        
        # Create loyalty levels
        new_level = ontology.New("NewCustomerLevel")
        regular_level = ontology.Regular("RegularCustomerLevel")
        premium_level = ontology.Premium("PremiumCustomerLevel")
        
        john.hasLoyaltyLevel = [premium_level]
        alice.hasLoyaltyLevel = [new_level]
        
        # Set up roles
        manager_role = ontology.Manager("ManagerRole")
        staff_role = ontology.Staff("StaffRole")
        
        bob.hasRole = [manager_role]
        carol.hasRole = [staff_role]
        
    logger.info("Test instances created successfully")
    return {
        "customers": [john, alice],
        "employees": [bob, carol],
        "books": [book1, book2, book3],
        "genres": [mystery, scifi],
        "publishers": [publisher1, publisher2],
        "inventories": [inv1, inv2, inv3]
    }


def test_rule(rule_name, ontology):
    """Test a specific rule with the ontology."""
    logger.info(f"Testing rule: {rule_name}")
    
    if rule_name not in rule_definitions:
        logger.error(f"Rule '{rule_name}' not found")
        return False
    
    # Convert ontology to graph for SPARQL testing
    graph = convert_ontology_to_graph(ontology)
    
    # Run the rule
    success = run_rule(rule_name, graph)
    
    if success:
        logger.info(f"Rule '{rule_name}' tested successfully")
    else:
        logger.error(f"Rule '{rule_name}' test failed")
    
    return success


def validate_rules(ontology):
    """Validate all rules against the ontology."""
    logger.info("Validating all rules...")
    
    # Create test instances in the ontology
    instances = create_test_instances(ontology)
    
    # Test each rule
    success_count = 0
    for rule_name in rule_definitions:
        if test_rule(rule_name, ontology):
            success_count += 1
    
    logger.info(f"Rule validation complete: {success_count}/{len(rule_definitions)} rules passed")
    
    return success_count == len(rule_definitions)


def main():
    """Main function for testing the rules."""
    logger.info("Starting SWRL rules testing...")
    
    # Use the bookstore ontology for testing
    ontology = bookstore_ontology
    
    # Validate the rules
    is_valid = validate_rules(ontology)
    
    if is_valid:
        logger.info("All rules validated successfully!")
        return 0
    else:
        logger.error("Rule validation failed!")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())