"""
Advanced Bookstore Ontology for Multi-Agent System

This module defines a comprehensive ontology for a bookstore management system
with three primary agent types (Customer, Employee, Book) and their relationships.
The ontology is built using Owlready2 and generates an OWL file for validation.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import owlready2 as owl


# Define the base IRI for the ontology
BASE_IRI = "http://www.semanticweb.org/bookstore-ontology#"

# Create a new ontology
onto = owl.get_ontology(BASE_IRI)


# Generate the file path for the OWL file output
def get_owl_file_path():
    """Generate a path for the OWL file in the project directory."""
    project_root = Path(__file__).parent.parent
    owl_dir = project_root / "ontology" / "owl_files"
    os.makedirs(owl_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return owl_dir / f"bookstore_ontology_{timestamp}.owl"


# Initialize the ontology with our namespace
with onto:
    #-------------------------------------------------------------------------
    # PRIMARY AGENT CLASSES
    #-------------------------------------------------------------------------
    
    class Customer(owl.Thing):
        """
        Represents individual buyers with preferences, budgets, and purchase history.
        """
        comment = ["A person who purchases books from the bookstore"]
    
    class Employee(owl.Thing):
        """
        Represents staff members with roles, responsibilities, and work schedules.
        """
        comment = ["A person who works at the bookstore"]
    
    class Book(owl.Thing):
        """
        Represents inventory items with metadata, pricing, and availability status.
        """
        comment = ["A book available for sale in the bookstore"]
    
    #-------------------------------------------------------------------------
    # SUPPORTING CLASSES
    #-------------------------------------------------------------------------
    
    class Order(owl.Thing):
        """
        Transaction records linking customers to book purchases.
        """
        comment = ["A record of a purchase transaction made by a customer"]
    
    class Inventory(owl.Thing):
        """
        Stock management and quantity tracking.
        """
        comment = ["A record of book quantities in stock"]
    
    class Genre(owl.Thing):
        """
        Book categorization system.
        """
        comment = ["A category of books"]
    
    class Publisher(owl.Thing):
        """
        Book source and supplier information.
        """
        comment = ["A company that publishes books"]
    
    class Author(owl.Thing):
        """
        Book writer and creator.
        """
        comment = ["A person who writes books"]
    
    class Bookstore(owl.Thing):
        """
        Physical or virtual bookstore location.
        """
        comment = ["A bookstore location where employees work"]
    
    class Transaction(owl.Thing):
        """
        Financial exchange records.
        """
        comment = ["A record of a financial exchange"]
    
    class Review(owl.Thing):
        """
        Customer book reviews and feedback.
        """
        comment = ["A customer review of a book"]
    
    class Rating(owl.Thing):
        """
        Numerical rating system (1-5 stars).
        """
        comment = ["A rating given to a book"]
    
    class Promotion(owl.Thing):
        """
        Marketing promotions and campaigns.
        """
        comment = ["A promotional campaign for books"]
    
    class Discount(owl.Thing):
        """
        Price reduction offers and deals.
        """
        comment = ["A discount applicable to purchases"]
    
    class Supplier(owl.Thing):
        """
        Book suppliers and distributors.
        """
        comment = ["A supplier that provides books to the store"]
    
    class Shipment(owl.Thing):
        """
        Delivery and shipment tracking.
        """
        comment = ["A shipment of books to the store"]
    
    class BookEvent(owl.Thing):
        """
        Store events like book signings and readings.
        """
        comment = ["An event held at the bookstore"]
    
    class ReadingProgram(owl.Thing):
        """
        Book clubs and reading challenges.
        """
        comment = ["A structured reading program or book club"]
    
    #-------------------------------------------------------------------------
    # OBJECT PROPERTIES - CUSTOMER RELATED
    #-------------------------------------------------------------------------
    
    class hasPreference(owl.ObjectProperty):
        """Links customers to preferred genres."""
        domain = [Customer]
        range = [Genre]
    
    class makesPurchase(owl.ObjectProperty):
        """Connects customers to their orders."""
        domain = [Customer]
        range = [Order]
    
    # hasBudget moved to Data Properties section as DataProperty
    
    class receivesRecommendation(owl.ObjectProperty):
        """Links customers to suggested books."""
        domain = [Customer]
        range = [Book]
    
    class writesReview(owl.ObjectProperty):
        """Customer creates a book review."""
        domain = [Customer]
        range = [Review]
    
    class hasReview(owl.ObjectProperty):
        """Book receives customer review."""
        domain = [Book]
        range = [Review]
    
    class hasRating(owl.ObjectProperty):
        """Review includes a rating."""
        domain = [Review]
        range = [Rating]
    
    class isEligibleForDiscount(owl.ObjectProperty):
        """Customer qualifies for discount."""
        domain = [Customer]
        range = [Discount]
    
    class enrollsInProgram(owl.ObjectProperty):
        """Customer joins reading program."""
        domain = [Customer]
        range = [ReadingProgram]
    
    class attendsEvent(owl.ObjectProperty):
        """Customer participates in event."""
        domain = [Customer]
        range = [BookEvent]
    
    #-------------------------------------------------------------------------
    # OBJECT PROPERTIES - EMPLOYEE RELATED
    #-------------------------------------------------------------------------
    
    class worksAt(owl.ObjectProperty):
        """Associates employees with bookstore locations."""
        domain = [Employee]
        range = [Bookstore]
    
    class managesInventory(owl.ObjectProperty):
        """Links employees to inventory responsibilities."""
        domain = [Employee]
        range = [Inventory]
    
    class assistsCustomer(owl.ObjectProperty):
        """Connects employees to customer service interactions."""
        domain = [Employee]
        range = [Customer]
    
    class hasRole(owl.ObjectProperty):
        """Defines employee job functions and permissions."""
        domain = [Employee]
        # range will be set to [EmployeeRole] after EmployeeRole is defined
    
    class organizesEvent(owl.ObjectProperty):
        """Employee organizes bookstore event."""
        domain = [Employee]
        range = [BookEvent]
    
    class tracksShipment(owl.ObjectProperty):
        """Employee monitors delivery status."""
        domain = [Employee]
        range = [Shipment]
    
    class managesPromotion(owl.ObjectProperty):
        """Employee manages promotional campaign."""
        domain = [Employee]
        range = [Promotion]
    
    #-------------------------------------------------------------------------
    # OBJECT PROPERTIES - BOOK RELATED
    #-------------------------------------------------------------------------
    
    class hasAuthor(owl.ObjectProperty):
        """Links books to their writers."""
        domain = [Book]
        range = [Author]
    
    class belongsToGenre(owl.ObjectProperty):
        """Categorizes books by type."""
        domain = [Book]
        range = [Genre]
    
    class publishedBy(owl.ObjectProperty):
        """Connects books to their publishers."""
        domain = [Book]
        range = [Publisher]
    
    # hasPrice moved to Data Properties section as DataProperty
    
    class inStock(owl.ObjectProperty):
        """Links books to inventory quantities."""
        domain = [Book]
        range = [Inventory]
    
    class hasPromotion(owl.ObjectProperty):
        """Book is included in promotion."""
        domain = [Book]
        range = [Promotion]
    
    class featuredInEvent(owl.ObjectProperty):
        """Book featured in event."""
        domain = [Book]
        range = [BookEvent]
    
    class featuredInProgram(owl.ObjectProperty):
        """Book featured in reading program."""
        domain = [Book]
        range = [ReadingProgram]
    
    class suppliedBy(owl.ObjectProperty):
        """Book supplied by distributor."""
        domain = [Book]
        range = [Supplier]
    
    class inShipment(owl.ObjectProperty):
        """Book included in shipment."""
        domain = [Book]
        range = [Shipment]
    
    #-------------------------------------------------------------------------
    # DATA PROPERTIES - NUMERICAL
    #-------------------------------------------------------------------------
    
    class availableQuantity(owl.DataProperty):
        """Current stock levels for inventory management."""
        domain = [Inventory]
        range = [int]
    
    class customerBudget(owl.DataProperty):
        """Spending limits for purchase decisions."""
        domain = [Customer]
        range = [float]
    
    class hasBudget(owl.DataProperty):
        """Customer spending limit (alias for customerBudget)."""
        domain = [Customer]
        range = [float]
    
    class hasPrice(owl.DataProperty):
        """Book monetary value (alias for bookPrice)."""
        domain = [Book]
        range = [float]
    
    class bookPrice(owl.DataProperty):
        """Pricing information for transaction processing."""
        domain = [Book]
        range = [float]
    
    class employeeSalary(owl.DataProperty):
        """Compensation data for role assignments."""
        domain = [Employee]
        range = [float]
    
    #-------------------------------------------------------------------------
    # DATA PROPERTIES - STRING
    #-------------------------------------------------------------------------
    
    class customerName(owl.DataProperty):
        """Identity information for personalization."""
        domain = [Customer]
        range = [str]
    
    class bookTitle(owl.DataProperty):
        """Identification for inventory tracking."""
        domain = [Book]
        range = [str]
    
    class employeeRole(owl.DataProperty):
        """Job function definitions for task assignment."""
        domain = [Employee]
        range = [str]
    
    class genreName(owl.DataProperty):
        """Category labels for recommendation systems."""
        domain = [Genre]
        range = [str]
    
    class authorName(owl.DataProperty):
        """Author's full name."""
        domain = [Author]
        range = [str]
    
    class authorBiography(owl.DataProperty):
        """Author's background and description."""
        domain = [Author]
        range = [str]
    
    class authorNationality(owl.DataProperty):
        """Author's country of origin."""
        domain = [Author]
        range = [str]
    
    class bookstoreName(owl.DataProperty):
        """Bookstore location name."""
        domain = [Bookstore]
        range = [str]
    
    class bookstoreAddress(owl.DataProperty):
        """Bookstore physical address."""
        domain = [Bookstore]
        range = [str]
    
    # Review & Rating Properties
    class reviewText(owl.DataProperty):
        """Review content and feedback."""
        domain = [Review]
        range = [str]
    
    class reviewDate(owl.DataProperty):
        """Date when review was written."""
        domain = [Review]
        range = [str]
    
    class ratingValue(owl.DataProperty):
        """Numeric rating (1-5 stars)."""
        domain = [Rating]
        range = [int]
    
    # Promotion & Discount Properties
    class promotionName(owl.DataProperty):
        """Promotion campaign name."""
        domain = [Promotion]
        range = [str]
    
    class promotionStartDate(owl.DataProperty):
        """Promotion start date."""
        domain = [Promotion]
        range = [str]
    
    class promotionEndDate(owl.DataProperty):
        """Promotion end date."""
        domain = [Promotion]
        range = [str]
    
    class discountPercentage(owl.DataProperty):
        """Discount percentage (0-100)."""
        domain = [Discount]
        range = [float]
    
    class discountCode(owl.DataProperty):
        """Unique discount code."""
        domain = [Discount]
        range = [str]
    
    # Supplier & Shipment Properties
    class supplierName(owl.DataProperty):
        """Supplier company name."""
        domain = [Supplier]
        range = [str]
    
    class supplierContact(owl.DataProperty):
        """Supplier contact information."""
        domain = [Supplier]
        range = [str]
    
    class shipmentStatus(owl.DataProperty):
        """Current shipment status."""
        domain = [Shipment]
        range = [str]
    
    class estimatedDelivery(owl.DataProperty):
        """Expected delivery date."""
        domain = [Shipment]
        range = [str]
    
    class shipmentQuantity(owl.DataProperty):
        """Number of items in shipment."""
        domain = [Shipment]
        range = [int]
    
    # Event & Program Properties
    class eventName(owl.DataProperty):
        """Event title."""
        domain = [BookEvent]
        range = [str]
    
    class eventDate(owl.DataProperty):
        """Event scheduled date."""
        domain = [BookEvent]
        range = [str]
    
    class eventDescription(owl.DataProperty):
        """Event details."""
        domain = [BookEvent]
        range = [str]
    
    class programName(owl.DataProperty):
        """Reading program name."""
        domain = [ReadingProgram]
        range = [str]
    
    class programDescription(owl.DataProperty):
        """Program details."""
        domain = [ReadingProgram]
        range = [str]
    
    class programDuration(owl.DataProperty):
        """Program length in weeks."""
        domain = [ReadingProgram]
        range = [int]
    
    #-------------------------------------------------------------------------
    # DATA PROPERTIES - BOOLEAN
    #-------------------------------------------------------------------------
    
    class isAvailable(owl.DataProperty):
        """Stock status for purchase validation."""
        domain = [Book]
        range = [bool]
    
    class isOnSale(owl.DataProperty):
        """Promotional status for pricing logic."""
        domain = [Book]
        range = [bool]
    
    class isPreferred(owl.DataProperty):
        """Genre is marked as preferred by system."""
        domain = [Genre]
        range = [bool]
    
    class isPreferredSupplier(owl.DataProperty):
        """Supplier has preferred status."""
        domain = [Supplier]
        range = [bool]
    
    class isVerifiedReview(owl.DataProperty):
        """Review is verified purchase."""
        domain = [Review]
        range = [bool]
    
    class isActivePromotion(owl.DataProperty):
        """Promotion is currently active."""
        domain = [Promotion]
        range = [bool]
    
    class isPublicEvent(owl.DataProperty):
        """Event is open to public."""
        domain = [BookEvent]
        range = [bool]
    
    #-------------------------------------------------------------------------
    # HIERARCHICAL STRUCTURES - EMPLOYEE ROLES
    #-------------------------------------------------------------------------
    
    class EmployeeRole(owl.Thing):
        """Base class for employee role hierarchy."""
        comment = ["A role that an employee can have"]
    
    class Manager(EmployeeRole):
        """Top level employee role."""
        comment = ["A manager role with highest authority"]
    
    class Supervisor(EmployeeRole):
        """Mid-level employee role, reports to Manager."""
        comment = ["A supervisor role reporting to managers"]
        is_a = [EmployeeRole]
    
    class Staff(EmployeeRole):
        """Regular employee role, reports to Supervisor."""
        comment = ["A regular staff role reporting to supervisors"]
        is_a = [EmployeeRole]
    
    class Intern(EmployeeRole):
        """Entry-level employee role, reports to Staff."""
        comment = ["An intern role reporting to regular staff"]
        is_a = [EmployeeRole]
    
    # Define the hierarchy relationship
    Manager.is_a.append(EmployeeRole)
    Supervisor.is_a.append(EmployeeRole)
    Staff.is_a.append(EmployeeRole)
    Intern.is_a.append(EmployeeRole)
    
    # Now that EmployeeRole is defined, set the range for hasRole
    hasRole.range = [EmployeeRole]
    
    # Define the hierarchy relationship using subclass relationships
    with onto:
        owl.AllDisjoint([Manager, Supervisor, Staff, Intern])
        
        # Create properties for reporting relationship
        class reportsTo(owl.ObjectProperty):
            domain = [EmployeeRole]
            range = [EmployeeRole]
            
        # Set up the reporting hierarchy
        Supervisor.is_a.append(reportsTo.some(Manager))
        Staff.is_a.append(reportsTo.some(Supervisor))
        Intern.is_a.append(reportsTo.some(Staff))
    
    #-------------------------------------------------------------------------
    # HIERARCHICAL STRUCTURES - GENRE TAXONOMY
    #-------------------------------------------------------------------------
    
    # Base fiction class
    class Fiction(Genre):
        """Fiction genre category."""
        comment = ["Books that are works of fiction"]
        is_a = [Genre]
    
    # Fiction subgenres
    class Mystery(Fiction):
        """Mystery fiction genre."""
        comment = ["Fiction books with mystery elements"]
        is_a = [Fiction]
    
    class DetectiveFiction(Mystery):
        """Detective fiction subgenre of Mystery."""
        comment = ["Mystery books focusing on detective work"]
        is_a = [Mystery]
    
    class Fantasy(Fiction):
        """Fantasy fiction genre."""
        comment = ["Fiction books with fantasy elements"]
        is_a = [Fiction]
    
    class ScienceFiction(Fiction):
        """Science fiction genre."""
        comment = ["Fiction books with scientific elements"]
        is_a = [Fiction]
    
    # Base non-fiction class
    class NonFiction(Genre):
        """Non-fiction genre category."""
        comment = ["Books that are works of non-fiction"]
        is_a = [Genre]
    
    # Non-fiction subgenres
    class Biography(NonFiction):
        """Biography genre."""
        comment = ["Non-fiction books about people's lives"]
        is_a = [NonFiction]
    
    class SelfHelp(NonFiction):
        """Self-help genre."""
        comment = ["Non-fiction books for personal improvement"]
        is_a = [NonFiction]
    
    class History(NonFiction):
        """History genre."""
        comment = ["Non-fiction books about historical events"]
        is_a = [NonFiction]
    
    #-------------------------------------------------------------------------
    # HIERARCHICAL STRUCTURES - CUSTOMER LOYALTY LEVELS
    #-------------------------------------------------------------------------
    
    class LoyaltyLevel(owl.Thing):
        """Base class for customer loyalty levels."""
        comment = ["A level of customer loyalty"]
    
    class Premium(LoyaltyLevel):
        """Premium customer loyalty level."""
        comment = ["Premium loyalty level with highest benefits"]
        is_a = [LoyaltyLevel]
    
    class Regular(LoyaltyLevel):
        """Regular customer loyalty level."""
        comment = ["Regular loyalty level with standard benefits"]
        is_a = [LoyaltyLevel]
    
    class New(LoyaltyLevel):
        """New customer loyalty level."""
        comment = ["New customer with basic benefits"]
        is_a = [LoyaltyLevel]
    
    # Add a property to connect customers to loyalty levels
    class hasLoyaltyLevel(owl.ObjectProperty):
        """Associates customers with their loyalty level."""
        domain = [Customer]
        range = [LoyaltyLevel]
    
    #-------------------------------------------------------------------------
    # COMPLEX RELATIONSHIPS
    #-------------------------------------------------------------------------
    
    # Book recommendation network based on genre similarities
    class hasSimilarGenre(owl.ObjectProperty):
        """Connects books with similar genres for recommendations."""
        domain = [Book]
        range = [Book]
        # Symmetric property - if book A is similar to book B, then B is similar to A
        characteristics = [owl.SymmetricProperty]
    
    # Customer behavior patterns linking purchase history to preferences
    class hasShownInterestIn(owl.ObjectProperty):
        """Links customers to genres they've shown interest in through purchases."""
        domain = [Customer]
        range = [Genre]
    
    # Employee expertise areas matching customer inquiry types
    class hasExpertiseIn(owl.ObjectProperty):
        """Associates employees with genre expertise."""
        domain = [Employee]
        range = [Genre]
    
    class worksWithSupplier(owl.ObjectProperty):
        """Publisher works with supplier."""
        domain = [Publisher]
        range = [Supplier]
    
    class hasCollaborator(owl.ObjectProperty):
        """Author collaborates with another author."""
        domain = [Author]
        range = [Author]
        characteristics = [owl.SymmetricProperty]


# Create instances for testing and validation
def create_test_instances():
    """Create test instances to validate the ontology."""
    # Customer instances
    john = onto.Customer("John")
    john.customerName = ["John Smith"]
    john.customerBudget = [100.0]
    john.hasBudget = [100.0]  # Using new DataProperty
    
    # Employee instances
    alice = onto.Employee("Alice")
    alice.customerName = ["Alice Johnson"]
    alice.employeeRole = ["Manager"]
    
    # Create a Manager role instance
    manager_role = onto.Manager("ManagerRole1")
    alice.hasRole = [manager_role]  # Using updated hasRole
    
    # Create a Bookstore instance
    main_store = onto.Bookstore("MainStore")
    main_store.bookstoreName = ["Downtown Bookstore"]
    main_store.bookstoreAddress = ["123 Main Street"]
    alice.worksAt = [main_store]  # Using updated worksAt
    
    # Create an Author instance
    author1 = onto.Author("AuthorJaneSmith")
    author1.authorName = ["Jane Smith"]
    author1.authorBiography = ["Award-winning mystery author"]
    author1.authorNationality = ["USA"]
    
    # Create a Supplier instance
    supplier1 = onto.Supplier("SupplierABC")
    supplier1.supplierName = ["ABC Book Distributors"]
    supplier1.supplierContact = ["contact@abcbooks.com"]
    supplier1.isPreferredSupplier = [True]
    
    # Book instances
    book1 = onto.Book("MysteryBook1")
    book1.bookTitle = ["The Mystery of the Hidden Key"]
    book1.bookPrice = [15.99]
    book1.hasPrice = [15.99]  # Using new DataProperty
    book1.isAvailable = [True]
    book1.hasAuthor = [author1]  # Using updated hasAuthor
    book1.suppliedBy = [supplier1]
    
    # Genre instances
    mystery = onto.Mystery("MysteryGenre")
    mystery.genreName = ["Mystery"]
    mystery.isPreferred = [True]  # Now properly used!
    
    # Publisher instance
    publisher = onto.Publisher("PublisherA")
    publisher.worksWithSupplier = [supplier1]
    
    # Review & Rating instances
    review1 = onto.Review("Review1")
    review1.reviewText = ["Excellent mystery novel with great plot twists!"]
    review1.reviewDate = ["2025-10-01"]
    review1.isVerifiedReview = [True]
    
    rating1 = onto.Rating("Rating1")
    rating1.ratingValue = [5]
    
    john.writesReview = [review1]
    book1.hasReview = [review1]
    review1.hasRating = [rating1]
    
    # Promotion & Discount instances
    fall_promo = onto.Promotion("FallPromotion")
    fall_promo.promotionName = ["Fall Reading Sale"]
    fall_promo.promotionStartDate = ["2025-09-01"]
    fall_promo.promotionEndDate = ["2025-11-30"]
    fall_promo.isActivePromotion = [True]
    
    discount1 = onto.Discount("Discount10")
    discount1.discountPercentage = [10.0]
    discount1.discountCode = ["FALL10"]
    
    book1.hasPromotion = [fall_promo]
    john.isEligibleForDiscount = [discount1]
    alice.managesPromotion = [fall_promo]
    
    # Shipment instance
    shipment1 = onto.Shipment("Shipment001")
    shipment1.shipmentStatus = ["In Transit"]
    shipment1.estimatedDelivery = ["2025-10-10"]
    shipment1.shipmentQuantity = [50]
    
    book1.inShipment = [shipment1]
    alice.tracksShipment = [shipment1]
    
    # BookEvent instance
    event1 = onto.BookEvent("AuthorMeet2025")
    event1.eventName = ["Meet the Author: Jane Smith"]
    event1.eventDate = ["2025-10-15"]
    event1.eventDescription = ["Join us for an exclusive author reading and Q&A session"]
    event1.isPublicEvent = [True]
    
    book1.featuredInEvent = [event1]
    john.attendsEvent = [event1]
    alice.organizesEvent = [event1]
    
    # ReadingProgram instance
    program1 = onto.ReadingProgram("MysteryClub")
    program1.programName = ["Mystery Lovers Book Club"]
    program1.programDescription = ["Monthly mystery book discussions"]
    program1.programDuration = [12]  # 12 weeks
    
    book1.featuredInProgram = [program1]
    john.enrollsInProgram = [program1]
    
    # Connect instances via object properties
    john.hasPreference = [mystery]
    book1.belongsToGenre = [mystery]
    book1.publishedBy = [publisher]
    alice.assistsCustomer = [john]
    alice.hasExpertiseIn = [mystery]
    
    # Set loyalty level
    premium = onto.Premium("PremiumLevel")
    john.hasLoyaltyLevel = [premium]
    
    return {
        "customer": john,
        "employee": alice,
        "book": book1,
        "genre": mystery,
        "publisher": publisher,
        "author": author1,
        "bookstore": main_store,
        "manager_role": manager_role,
        "supplier": supplier1,
        "review": review1,
        "rating": rating1,
        "promotion": fall_promo,
        "discount": discount1,
        "shipment": shipment1,
        "event": event1,
        "program": program1
    }


def validate_ontology():
    """Validate the ontology for consistency and report any issues."""
    try:
        # Simple validation - check that all classes are defined
        class_count = len(list(onto.classes()))
        print(f"Ontology contains {class_count} classes.")
        
        # Create a few test instances to check property constraints
        instances = create_test_instances()
        print(f"Created test instances: {', '.join(instances.keys())}")
        
        print("Ontology validation successful: Basic validation checks passed.")
        return True
    except Exception as e:
        print(f"Ontology validation failed: {e}")
        return False


def save_ontology_to_owl():
    """Save the ontology to an OWL file."""
    # Generate file path
    owl_file_path = get_owl_file_path()
    
    # Save the ontology
    onto.save(file=str(owl_file_path), format="rdfxml")
    
    print(f"Ontology saved to: {owl_file_path}")
    return owl_file_path


def main():
    """Main function to execute when the script is run directly."""
    # Create test instances
    instances = create_test_instances()
    print("Created test instances to validate the ontology.")
    
    # Validate the ontology
    is_valid = validate_ontology()
    
    if is_valid:
        # Save the ontology to an OWL file
        owl_file_path = save_ontology_to_owl()
        print(f"Ontology validation successful and saved to {owl_file_path}")
        return 0
    else:
        print("Ontology validation failed. Please check the errors above.")
        return 1


# Execute main function when the script is run directly
if __name__ == "__main__":
    sys.exit(main())