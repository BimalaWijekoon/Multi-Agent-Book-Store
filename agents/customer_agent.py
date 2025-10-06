"""
Customer Agent Implementation for Bookstore Management System.

This module implements the Customer agent behaviors that utilize the ontology,
SWRL rules, and message bus from previous phases.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Tuple

# Mesa framework imports
import mesa

# Import ontology and message bus components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from communication import MessageBus, MessageType, AgentType, Message
from ontology.advanced_bookstore_ontology import onto

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CustomerAgent(mesa.Agent):
    """
    CustomerAgent implements behaviors for bookstore customers.
    
    Core behaviors:
    - Preference-Based Browsing: Navigate bookstore based on ontology hasPreference properties
    - Budget-Aware Purchasing: Make buying decisions constrained by customerBudget
    - Recommendation Processing: Evaluate book suggestions from employee agents
    - Purchase History Tracking: Update ontology after successful transactions
    """
    
    def __init__(self, unique_id: str, model, message_bus: MessageBus, ontology_individual=None, name=None):
        """
        Initialize a new Customer agent.
        
        Args:
            unique_id: The agent's unique identifier
            model: The model instance the agent is part of
            message_bus: The message bus for communication
            ontology_individual: The ontology individual representing this customer
            name: Optional customer name (e.g., "Jennifer Martinez")
        """
        # Initialize Mesa agent correctly - model first, then other params
        mesa.Agent.__init__(self, model)
        # Override the auto-assigned unique_id with our custom one
        self.unique_id = unique_id
        self.message_bus = message_bus
        self.ontology_ref = ontology_individual
        self.pos = None  # Position in the grid
        
        # Initialize customer properties
        self.name = name or f"Customer {unique_id.split('_')[-1]}"  # Use provided name or generate generic
        self.preferred_genres = []
        # Random initial budget: Rs. 5000 to Rs. 20000 (realistic variation for Sri Lanka)
        self.initial_budget = round(random.uniform(5000.0, 20000.0), 2)
        self.current_budget = self.initial_budget  # Start with initial budget
        self.satisfaction_level = 5  # Scale of 1-10
        self.purchase_history = []
        self.is_active = True
        self.loyalty_level = None  # Will be assigned based on purchase history
        self.order_count = 0  # Track number of orders
        self.eligible_discounts = []  # Track eligible discount codes
        
        # Register with message bus
        self.message_bus.register_agent(self.unique_id, AgentType.CUSTOMER)
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(self.unique_id, [
            MessageType.PURCHASE_CONFIRMATION,
            MessageType.RECOMMENDATION_RESPONSE
        ])
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            self._assign_loyalty_level()  # Assign initial loyalty level
        
        logger.info(f"Customer agent {self.unique_id} ({self.name}) initialized with random budget Rs. {self.initial_budget:.2f}")
        
    def step(self):
        """
        Perform a single step of the agent.
        Required by the Mesa framework.
        """
        # Process any pending messages
        if hasattr(self, 'message_bus'):
            self.message_bus.process_messages()
        
        # Register with message bus
        self.message_bus.register_agent(self.unique_id, AgentType.CUSTOMER)
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(self.unique_id, [
            MessageType.PURCHASE_CONFIRMATION,
            MessageType.RECOMMENDATION_RESPONSE
        ])
        
        # Register targeted message handlers (with agent_id for direct routing)
        self.message_bus.register_handler(MessageType.PURCHASE_CONFIRMATION, self._handle_purchase_confirmation, self.unique_id)
        self.message_bus.register_handler(MessageType.RECOMMENDATION_RESPONSE, self._handle_recommendation, self.unique_id)
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            
        # Note: Initialization logging happens in __init__, not here
    
    def _sync_from_ontology(self):
        """Synchronize agent state from the ontology individual."""
        try:
            if hasattr(self.ontology_ref, "hasPreferredGenre"):
                self.preferred_genres = [str(genre) for genre in self.ontology_ref.hasPreferredGenre]
                
            # Sync initial budget from ontology if available, otherwise keep random initial budget
            if hasattr(self.ontology_ref, "hasCustomerBudget"):
                ontology_budget = float(self.ontology_ref.hasCustomerBudget)
                if ontology_budget > 0:  # Only update if ontology has valid budget
                    self.initial_budget = ontology_budget
                    self.current_budget = ontology_budget
                
            if hasattr(self.ontology_ref, "hasSatisfactionLevel"):
                self.satisfaction_level = int(self.ontology_ref.hasSatisfactionLevel)
                
            if hasattr(self.ontology_ref, "makesPurchase"):
                self.purchase_history = [str(purchase) for purchase in self.ontology_ref.makesPurchase]
                
            logger.debug(f"Customer {self.unique_id} synchronized from ontology")
        except Exception as e:
            logger.error(f"Error syncing from ontology: {e}")
    
    def _sync_to_ontology(self):
        """Update the ontology individual with current agent state."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                if hasattr(self.ontology_ref, "hasCustomerBudget"):
                    self.ontology_ref.hasCustomerBudget = self.current_budget
                if hasattr(self.ontology_ref, "hasSatisfactionLevel"):
                    self.ontology_ref.hasSatisfactionLevel = self.satisfaction_level
            logger.debug(f"Customer {self.unique_id} state updated in ontology")
        except Exception as e:
            logger.error(f"Error updating ontology: {e}")
    
    def browse_books(self, available_books: List[Dict[str, Any]]) -> Optional[str]:
        """
        Browse available books based on preferences and budget.
        STRICT: Only browse books within current budget.
        
        Args:
            available_books: List of book info dictionaries
            
        Returns:
            Selected book ID or None if no suitable book found
        """
        logger.info(f"Customer {self.unique_id} browsing books...")
        
        if not available_books:
            logger.info("No books available for browsing")
            return None
        
        # STRICT: Check if customer has any budget remaining
        if self.current_budget <= 0:
            logger.info(f"Customer {self.unique_id} has NO remaining budget (Rs. {self.current_budget:.2f})")
            return None
        
        # Filter books by budget FIRST (strict enforcement)
        affordable_books = [
            book for book in available_books 
            if book.get('price', float('inf')) <= self.current_budget
        ]
        
        if not affordable_books:
            logger.info(f"Customer {self.unique_id} cannot afford any books (budget: Rs. {self.current_budget:.2f})")
            return None
            
        # Filter books by preferred genres if any
        preferred_books = []
        if self.preferred_genres:
            preferred_books = [
                book for book in affordable_books
                if any(genre in book.get('genres', []) for genre in self.preferred_genres)
            ]
        
        # If no books match preferences, consider all affordable books
        target_books = preferred_books if preferred_books else affordable_books
        
        if not target_books:
            return None
            
        # Select a book based on preferences and price
        # Simple strategy: Choose the most affordable book in preferred genre
        selected_book = min(target_books, key=lambda b: b.get('price', float('inf')))
        logger.info(f"Customer {self.unique_id} selected book {selected_book.get('id')}")
        
        return selected_book.get('id')
    
    def purchase_book(self, book_id: str) -> bool:
        """
        Attempt to purchase a book by sending a purchase request.
        
        Args:
            book_id: The ID of the book to purchase
            
        Returns:
            True if purchase request sent successfully
        """
        if not book_id:
            return False
            
        logger.info(f"Customer {self.unique_id} requesting purchase of book {book_id}")
        
        # Send purchase request message
        content = {
            'book_id': book_id,
            'customer_budget': self.current_budget
        }
        
        message_id = self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=book_id,  # Assuming book_id is also the agent ID
            message_type=MessageType.PURCHASE_REQUEST,
            content=content
        )
        
        logger.debug(f"Sent purchase request {message_id}")
        return True
    
    def process_recommendations(self) -> Optional[str]:
        """
        Process any pending recommendations and make purchase decisions.
        
        Returns:
            Selected book ID or None if no recommendation accepted
        """
        # Process messages to handle any new recommendations
        self.message_bus.process_messages()
        
        # Get pending recommendation messages
        pending_messages = self.message_bus.get_pending_messages(self.unique_id)
        
        recommendation_messages = [
            msg for msg in pending_messages
            if msg.message_type == MessageType.RECOMMENDATION_RESPONSE
        ]
        
        if not recommendation_messages:
            logger.debug(f"No pending recommendations for customer {self.unique_id}")
            return None
            
        # Process each recommendation
        for msg in recommendation_messages:
            selected_book = self._evaluate_recommendation(msg.content)
            if selected_book:
                return selected_book
                
        return None
    
    def _evaluate_recommendation(self, recommendation_content: Dict[str, Any]) -> Optional[str]:
        """
        Evaluate a book recommendation.
        
        Args:
            recommendation_content: Dictionary with recommendation details
            
        Returns:
            Selected book ID or None if recommendation rejected
        """
        recommended_books = recommendation_content.get('book_recommendations', [])
        if not recommended_books:
            return None
            
        # Filter books by budget
        affordable_books = [
            book for book in recommended_books
            if book.get('price', float('inf')) <= self.current_budget
        ]
        
        if not affordable_books:
            logger.info(f"Customer {self.unique_id} found no affordable recommendations")
            return None
            
        # Select book with highest match to preferences
        selected_book = None
        best_match_score = -1
        
        for book in affordable_books:
            # Calculate preference match score (0-10)
            match_score = 0
            book_genres = book.get('genre', [])
            
            # Add points for each matching genre
            for genre in self.preferred_genres:
                if genre in book_genres:
                    match_score += 3
                    
            # Add points for lower price (normalized to 0-5 range)
            price = book.get('price', 0)
            if price > 0:
                price_score = max(0, 5 - min(5, price / 10))
                match_score += price_score
                
            if match_score > best_match_score:
                best_match_score = match_score
                selected_book = book
        
        if selected_book and best_match_score > 5:  # Only accept good matches
            logger.info(f"Customer {self.unique_id} accepted recommendation for book {selected_book.get('id')}")
            return selected_book.get('id')
            
        return None
    
    def _handle_purchase_confirmation(self, message: Message) -> None:
        """
        Handle purchase confirmation messages.
        
        Args:
            message: The purchase confirmation message
        """
        book_id = message.content.get('book_id')
        price = message.content.get('price', 0.0)
        available = message.content.get('available', False)
        
        logger.info(f"Customer {self.unique_id} received purchase confirmation for {book_id}")
        
        if not available:
            logger.info(f"Book {book_id} is not available")
            return
            
        if price > self.current_budget:
            logger.info(f"Book {book_id} price Rs. {price} exceeds budget Rs. {self.current_budget}")
            return
            
        # Process the purchase
        self.current_budget -= price
        self.purchase_history.append(book_id)
        self.satisfaction_level = min(10, self.satisfaction_level + 1)
        
        logger.info(f"Customer {self.unique_id} purchased {book_id} for Rs. {price}")
        logger.info(f"New budget: Rs. {self.current_budget}")
        
        # Send payment message
        payment_content = {
            'book_id': book_id,
            'amount': price
        }
        
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=book_id,
            message_type=MessageType.PAYMENT_PROCESS,
            content=payment_content
        )
        
        # Update ontology
        self._update_purchase_in_ontology(book_id)
    
    def _handle_recommendation(self, message: Message) -> None:
        """
        Handle recommendation messages.
        
        Args:
            message: The recommendation message
        """
        logger.info(f"Customer {self.unique_id} received recommendation from {message.sender_id}")
        
        # The actual processing happens in process_recommendations and _evaluate_recommendation
        # This just acknowledges receipt
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=message.sender_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={'original_message_id': message.id}
        )
    
    def _update_purchase_in_ontology(self, book_id: str) -> None:
        """
        Update the ontology to reflect a purchase.
        Creates Order, Transaction, and potentially Review/Rating instances.
        
        Args:
            book_id: The ID of the purchased book
        """
        if not self.ontology_ref:
            return
            
        try:
            # Find book in ontology
            book_individual = None
            for book in onto.Book.instances():
                if hasattr(book, "hasID") and book.hasID == book_id:
                    book_individual = book
                    break
                elif str(book.name) == book_id:
                    book_individual = book
                    break
                    
            if not book_individual:
                logger.warning(f"Could not find book {book_id} in ontology")
                return
            
            # Get book price
            book_price = book_individual.hasPrice[0] if hasattr(book_individual, 'hasPrice') and book_individual.hasPrice else 0.0
                
            # Update customer's purchase relationship
            with onto:
                # Create Order instance (NEW!)
                self.order_count += 1
                order_id = f"Order_{self.unique_id}_{self.order_count}"
                order = onto.Order(order_id)
                logger.info(f"Created Order: {order_id}")
                
                # Link customer to order
                if hasattr(self.ontology_ref, "makesPurchase"):
                    self.ontology_ref.makesPurchase.append(order)
                
                # Create Transaction instance (NEW!)
                transaction_id = f"Trans_{order_id}"
                transaction = onto.Transaction(transaction_id)
                logger.info(f"Created Transaction: {transaction_id}")
                
                # Update customer budget
                if hasattr(self.ontology_ref, "customerBudget"):
                    self.ontology_ref.customerBudget = [self.current_budget]
                if hasattr(self.ontology_ref, "hasBudget"):
                    self.ontology_ref.hasBudget = [self.current_budget]
                
                # Update loyalty level based on purchase history
                self._update_loyalty_level()
                
                # Randomly write a review (30% chance)
                if random.random() < 0.3:
                    self._write_review(book_individual)
                    
            logger.info(f"Updated ontology with purchase of {book_id} (Order: {order_id})")
        except Exception as e:
            logger.error(f"Error updating purchase in ontology: {e}")
    
    def step(self) -> None:
        """
        Perform one simulation step for the customer agent.
        This is typically called by the simulation framework.
        """
        # Process any pending messages
        self.message_bus.process_messages()
        
        # Sync with ontology at end of step
        self._sync_to_ontology()
    
    def request_assistance(self, request_type: str, details: Dict[str, Any]) -> None:
        """
        Request assistance from an employee.
        
        Args:
            request_type: Type of assistance needed
            details: Additional details about the request
        """
        content = {
            'request_type': request_type,
            'details': details
        }
        
        # Send to any employee (broadcast to employee type)
        self.message_bus.broadcast_message(
            sender_id=self.unique_id,
            message_type=MessageType.ASSISTANCE_REQUEST,
            content=content,
            target_agent_type=AgentType.EMPLOYEE
        )
        
        logger.info(f"Customer {self.unique_id} requested {request_type} assistance")
    
    def inquire_about_genre(self, genre: str) -> None:
        """
        Send a genre inquiry message.
        
        Args:
            genre: The genre to inquire about
        """
        content = {'genre': genre}
        
        # Send to any employee or book (broadcast)
        self.message_bus.broadcast_message(
            sender_id=self.unique_id,
            message_type=MessageType.GENRE_INQUIRY,
            content=content
        )
        
        logger.info(f"Customer {self.unique_id} inquired about {genre} genre")
    
    def _assign_loyalty_level(self) -> None:
        """Assign initial loyalty level to customer (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                # Assign New loyalty level by default
                new_level = onto.New(f"NewLevel_{self.unique_id}")
                if hasattr(self.ontology_ref, "hasLoyaltyLevel"):
                    self.ontology_ref.hasLoyaltyLevel = [new_level]
                    self.loyalty_level = "New"
                    logger.info(f"Assigned New loyalty level to {self.unique_id}")
        except Exception as e:
            logger.error(f"Error assigning loyalty level: {e}")
    
    def _update_loyalty_level(self) -> None:
        """Update loyalty level based on purchase count (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                # Upgrade loyalty level based on purchases
                if self.order_count >= 5 and self.loyalty_level != "Premium":
                    premium_level = onto.Premium(f"PremiumLevel_{self.unique_id}")
                    if hasattr(self.ontology_ref, "hasLoyaltyLevel"):
                        self.ontology_ref.hasLoyaltyLevel = [premium_level]
                        self.loyalty_level = "Premium"
                        logger.info(f"Upgraded {self.unique_id} to Premium loyalty level")
                elif self.order_count >= 2 and self.loyalty_level == "New":
                    regular_level = onto.Regular(f"RegularLevel_{self.unique_id}")
                    if hasattr(self.ontology_ref, "hasLoyaltyLevel"):
                        self.ontology_ref.hasLoyaltyLevel = [regular_level]
                        self.loyalty_level = "Regular"
                        logger.info(f"Upgraded {self.unique_id} to Regular loyalty level")
        except Exception as e:
            logger.error(f"Error updating loyalty level: {e}")
    
    def _write_review(self, book_individual) -> None:
        """Write a review and rating for a book (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                # Create Review instance
                review_id = f"Review_{self.unique_id}_{book_individual.name}"
                review = onto.Review(review_id)
                
                # Set review properties
                review_texts = [
                    "Excellent book, highly recommend!",
                    "Great read, very engaging.",
                    "Good book, worth the price.",
                    "Interesting story and characters.",
                    "Amazing book, couldn't put it down!"
                ]
                review.reviewText = [random.choice(review_texts)]
                review.reviewDate = ["2025-10-05"]  # Current date
                review.isVerifiedReview = [True]  # Verified purchase
                
                # Create Rating instance
                rating_id = f"Rating_{review_id}"
                rating = onto.Rating(rating_id)
                rating.ratingValue = [random.randint(3, 5)]  # 3-5 stars
                
                # Link review to rating
                review.hasRating = [rating]
                
                # Link customer to review
                if hasattr(self.ontology_ref, "writesReview"):
                    self.ontology_ref.writesReview.append(review)
                
                # Link book to review
                if hasattr(book_individual, "hasReview"):
                    book_individual.hasReview.append(review)
                
                logger.info(f"{self.unique_id} wrote review for {book_individual.name} with {rating.ratingValue[0]} stars")
        except Exception as e:
            logger.error(f"Error writing review: {e}")
    
    def enroll_in_program(self, program_name: str) -> None:
        """Enroll customer in a reading program (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find or create reading program
            program = None
            for prog in onto.ReadingProgram.instances():
                if hasattr(prog, "programName") and prog.programName and prog.programName[0] == program_name:
                    program = prog
                    break
            
            if program and hasattr(self.ontology_ref, "enrollsInProgram"):
                with onto:
                    self.ontology_ref.enrollsInProgram.append(program)
                    logger.info(f"{self.unique_id} enrolled in program: {program_name}")
        except Exception as e:
            logger.error(f"Error enrolling in program: {e}")
    
    def attend_event(self, event_name: str) -> None:
        """Register customer attendance for a bookstore event (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find event
            event = None
            for evt in onto.BookEvent.instances():
                if hasattr(evt, "eventName") and evt.eventName and evt.eventName[0] == event_name:
                    event = evt
                    break
            
            if event and hasattr(self.ontology_ref, "attendsEvent"):
                with onto:
                    self.ontology_ref.attendsEvent.append(event)
                    logger.info(f"{self.unique_id} registered for event: {event_name}")
        except Exception as e:
            logger.error(f"Error attending event: {e}")
    
    def check_eligible_discounts(self) -> List[str]:
        """Check which discounts customer is eligible for (NEW!)."""
        if not self.ontology_ref:
            return []
            
        eligible = []
        try:
            # Check ontology for eligible discounts
            if hasattr(self.ontology_ref, "isEligibleForDiscount"):
                for discount in self.ontology_ref.isEligibleForDiscount:
                    if hasattr(discount, "discountCode") and discount.discountCode:
                        eligible.append(discount.discountCode[0])
            
            self.eligible_discounts = eligible
            logger.info(f"{self.unique_id} eligible for discounts: {eligible}")
        except Exception as e:
            logger.error(f"Error checking discounts: {e}")
        
        return eligible


def test_agent_behavior():
    """Test the customer agent's core behaviors."""
    # Initialize message bus
    message_bus = MessageBus()
    
    # Create test customer
    customer = CustomerAgent("customer1", message_bus)
    
    # Create test book data
    test_books = [
        {
            'id': 'book1',
            'title': 'Mystery Novel',
            'author': 'Author One',
            'price': 24.99,
            'genres': ['Mystery', 'Thriller']
        },
        {
            'id': 'book2',
            'title': 'Fantasy Epic',
            'author': 'Author Two',
            'price': 19.99,
            'genres': ['Fantasy', 'Adventure']
        },
        {
            'id': 'book3',
            'title': 'Science Book',
            'author': 'Author Three',
            'price': 120.0,  # Too expensive
            'genres': ['Science', 'Education']
        }
    ]
    
    # Set customer preferences
    customer.preferred_genres = ['Fantasy', 'Adventure']
    
    # Test browsing behavior
    selected_book = customer.browse_books(test_books)
    print(f"Customer selected book: {selected_book}")
    
    # Test purchase behavior
    if selected_book:
        customer.purchase_book(selected_book)
    
    # Test recommendation processing
    print("Testing recommendation processing...")
    message_bus.send_message(
        sender_id="employee1",
        receiver_id="customer1",
        message_type=MessageType.RECOMMENDATION_RESPONSE,
        content={
            'book_recommendations': [
                {
                    'id': 'book4',
                    'title': 'Fantasy Quest',
                    'author': 'Author Four',
                    'price': 22.99,
                    'genre': ['Fantasy', 'Adventure']
                }
            ]
        }
    )
    
    # Process messages
    message_bus.process_messages()
    
    # Test assistance request
    customer.request_assistance(
        request_type="find_book",
        details={"title_keywords": "dragon", "author_keywords": "tolkien"}
    )
    
    # Test genre inquiry
    customer.inquire_about_genre("Science Fiction")
    
    print("Customer agent testing complete!")


if __name__ == "__main__":
    test_agent_behavior()
