"""
Employee Agent Implementation for Bookstore Management System.

This module implements the Employee agent behaviors that utilize the ontology,
SWRL rules, and message bus from previous phases.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

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


class EmployeeAgent(mesa.Agent):
    """
    EmployeeAgent implements behaviors for bookstore employees.
    
    Core behaviors:
    - Role-Based Task Management: Execute tasks based on employee role
    - Inventory Monitoring: Track stock levels and trigger restocking
    - Customer Assistance: Respond to inquiries with expertise-based recommendations
    - Workflow Coordination: Collaborate with other employees
    """
    
    def __init__(self, unique_id: str, model, message_bus: MessageBus, ontology_individual=None, name=None):
        """
        Initialize a new Employee agent.
        
        Args:
            unique_id: The agent's unique identifier
            model: The model instance the agent is part of
            message_bus: The message bus for communication
            ontology_individual: The ontology individual representing this employee
            name: Optional employee name (e.g., "Ms. Sarah Chen")
        """
        # Initialize Mesa agent correctly - model first, then other params
        mesa.Agent.__init__(self, model)
        # Override the auto-assigned unique_id with our custom one
        self.unique_id = unique_id
        self.message_bus = message_bus
        self.ontology_ref = ontology_individual
        self.pos = None  # Position in the grid
        
        # Initialize employee properties
        self.name = name or f"Employee {unique_id.split('_')[-1]}"  # Use provided name or generate generic
        self.role = "Associate"  # Default role
        self.expertise_areas = []
        self.current_tasks = []
        self.workload = 0  # Scale of 0-10
        self.tasks_completed = {}  # Dictionary to track completed tasks
        self.role_instance = None  # NEW: Reference to EmployeeRole instance
        self.managed_inventory = []  # NEW: List of Inventory instances managed
        self.tracked_shipments = []  # NEW: List of Shipment instances tracked
        self.managed_promotions = []  # NEW: List of Promotion instances managed
        self.organized_events = []  # NEW: List of BookEvent instances organized
        
        # Register with message bus
        self.message_bus.register_agent(self.unique_id, AgentType.EMPLOYEE)
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(self.unique_id, [
            MessageType.RESTOCK_ALERT,
            MessageType.ASSISTANCE_REQUEST,
            MessageType.GENRE_INQUIRY,
            MessageType.STOCK_INQUIRY
        ])
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            self._assign_role()  # NEW: Assign proper EmployeeRole
        
    def step(self):
        """
        Perform a single step of the agent.
        Required by the Mesa framework.
        """
        # Process any pending messages
        if hasattr(self, 'message_bus'):
            self.message_bus.process_messages()
            
        # Handle workload-based tasks
        if self.workload > 0:
            # Process work items
            self.workload -= 1
        
        # Register with message bus
        self.message_bus.register_agent(self.unique_id, AgentType.EMPLOYEE)
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(self.unique_id, [
            MessageType.RESTOCK_ALERT,
            MessageType.ASSISTANCE_REQUEST,
            MessageType.GENRE_INQUIRY,
            MessageType.STOCK_INQUIRY
        ])
        
        # Register targeted message handlers (with agent_id for direct routing)
        self.message_bus.register_handler(MessageType.RESTOCK_ALERT, self._handle_restock_alert, self.unique_id)
        self.message_bus.register_handler(MessageType.ASSISTANCE_REQUEST, self._handle_assistance_request, self.unique_id)
        self.message_bus.register_handler(MessageType.GENRE_INQUIRY, self._handle_genre_inquiry, self.unique_id)
        self.message_bus.register_handler(MessageType.STOCK_INQUIRY, self._handle_stock_inquiry, self.unique_id)
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            
        logger.info(f"Employee agent {self.unique_id} initialized with role {self.role}")
    
    def _sync_from_ontology(self):
        """Synchronize agent state from the ontology individual."""
        try:
            if hasattr(self.ontology_ref, "hasRole"):
                self.role = str(self.ontology_ref.hasRole)
                
            if hasattr(self.ontology_ref, "hasExpertise"):
                self.expertise_areas = [str(expertise) for expertise in self.ontology_ref.hasExpertise]
                
            if hasattr(self.ontology_ref, "hasWorkload"):
                self.workload = int(self.ontology_ref.hasWorkload)
                
            logger.debug(f"Employee {self.unique_id} synchronized from ontology")
        except Exception as e:
            logger.error(f"Error syncing from ontology: {e}")
    
    def _sync_to_ontology(self):
        """Update the ontology individual with current agent state."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                if hasattr(self.ontology_ref, "hasWorkload"):
                    self.ontology_ref.hasWorkload = self.workload
            logger.debug(f"Employee {self.unique_id} state updated in ontology")
        except Exception as e:
            logger.error(f"Error updating ontology: {e}")
    
    def monitor_inventory(self, book_inventory: Dict[str, int]) -> List[str]:
        """
        Monitor inventory levels and trigger restocking when needed.
        
        Args:
            book_inventory: Dictionary of book IDs to stock levels
            
        Returns:
            List of book IDs that need restocking
        """
        logger.info(f"Employee {self.unique_id} monitoring inventory...")
        
        restock_needed = []
        threshold = 3  # Minimum stock threshold
        
        for book_id, stock_level in book_inventory.items():
            if stock_level < threshold:
                logger.info(f"Low stock alert for book {book_id}: {stock_level} remaining")
                restock_needed.append(book_id)
                
                # Send restock confirmation
                self.message_bus.send_message(
                    sender_id=self.unique_id,
                    receiver_id=book_id,
                    message_type=MessageType.RESTOCK_CONFIRMATION,
                    content={
                        'book_id': book_id,
                        'restock_amount': 10  # Standard restock amount
                    }
                )
                
                # For manager role, send supplier notification
                if self.role == "Manager":
                    self.message_bus.send_message(
                        sender_id=self.unique_id,
                        receiver_id="system",
                        message_type=MessageType.SUPPLIER_NOTIFICATION,
                        content={
                            'book_id': book_id,
                            'quantity': 20,  # Order more from supplier
                            'priority': 'high' if stock_level == 0 else 'medium'
                        }
                    )
        
        return restock_needed
    
    def assist_customers(self) -> int:
        """
        Process assistance requests from customers.
        
        Returns:
            Number of requests processed
        """
        # Process pending messages
        self.message_bus.process_messages()
        
        # Get pending assistance requests
        pending_messages = self.message_bus.get_pending_messages(self.unique_id)
        
        assistance_requests = [
            msg for msg in pending_messages
            if msg.message_type == MessageType.ASSISTANCE_REQUEST
        ]
        
        if not assistance_requests:
            return 0
        
        processed_count = 0
        for msg in assistance_requests:
            request_type = msg.content.get('request_type', '')
            details = msg.content.get('details', {})
            
            if request_type == 'find_book':
                self._handle_find_book_request(msg.sender_id, details)
                processed_count += 1
            elif request_type == 'recommendation':
                self._handle_recommendation_request(msg.sender_id, details)
                processed_count += 1
            else:
                logger.warning(f"Unknown assistance request type: {request_type}")
        
        # Update workload based on requests processed
        self.workload = min(10, self.workload + processed_count)
        self._sync_to_ontology()
        
        return processed_count
    
    def _handle_find_book_request(self, customer_id: str, details: Dict[str, Any]) -> None:
        """
        Handle a request to find a specific book.
        
        Args:
            customer_id: ID of the customer making the request
            details: Search details (title keywords, author, etc.)
        """
        # In a real implementation, this would search the ontology
        # Here we'll simulate finding books based on the request
        
        title_keywords = details.get('title_keywords', '').lower()
        author_keywords = details.get('author_keywords', '').lower()
        
        recommended_books = []
        
        # If we have an ontology reference, search it for matching books
        if onto is not None:
            for book in onto.Book.instances():
                title = str(book.hasTitle).lower() if hasattr(book, "hasTitle") else ""
                author = str(book.hasAuthor).lower() if hasattr(book, "hasAuthor") else ""
                book_id = str(book.hasID) if hasattr(book, "hasID") else ""
                price = float(book.hasPrice) if hasattr(book, "hasPrice") else 0.0
                
                if (title_keywords in title or not title_keywords) and \
                   (author_keywords in author or not author_keywords):
                    # Extract genres
                    genres = []
                    if hasattr(book, "hasGenre"):
                        genres = [str(genre) for genre in book.hasGenre]
                    
                    recommended_books.append({
                        'id': book_id,
                        'title': title,
                        'author': author,
                        'price': price,
                        'genre': genres
                    })
        
        # If no books found or no ontology, create a simulated response
        if not recommended_books:
            # Simulate finding a book - in real system would query ontology
            if "dragon" in title_keywords.lower():
                recommended_books.append({
                    'id': 'book123',
                    'title': 'Dragon Quest',
                    'author': 'J.R.R. Tolkien',
                    'price': 24.99,
                    'genre': ['Fantasy', 'Adventure']
                })
        
        # Send recommendation response
        if recommended_books:
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=customer_id,
                message_type=MessageType.RECOMMENDATION_RESPONSE,
                content={'book_recommendations': recommended_books}
            )
            
            logger.info(f"Employee {self.unique_id} sent book recommendations to {customer_id}")
        else:
            # Send empty recommendation (no matches)
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=customer_id,
                message_type=MessageType.RECOMMENDATION_RESPONSE,
                content={'book_recommendations': []}
            )
            
            logger.info(f"Employee {self.unique_id} found no matching books for {customer_id}")
    
    def _handle_recommendation_request(self, customer_id: str, details: Dict[str, Any]) -> None:
        """
        Handle a request for book recommendations.
        
        Args:
            customer_id: ID of the customer making the request
            details: Preference details (genres, budget, etc.)
        """
        preferred_genres = details.get('genres', [])
        max_budget = details.get('max_budget', float('inf'))
        
        # Get recommendations from ontology if possible
        recommendations = []
        
        if self.message_bus.ontology is not None:
            recommendations = self.message_bus.get_ontology_recommendations(
                customer_id, 
                genre=preferred_genres[0] if preferred_genres else None
            )
        
        # If ontology recommendations not available, create simulated ones
        if not recommendations:
            # Create dummy recommendations based on requested genres
            for genre in preferred_genres:
                recommendations.append({
                    'id': f"book_{genre.lower()}_1",
                    'title': f"Best {genre} Book",
                    'author': "Famous Author",
                    'price': 19.99,
                    'genre': [genre]
                })
        
        # Filter by budget
        if max_budget < float('inf'):
            recommendations = [book for book in recommendations if book.get('price', 0) <= max_budget]
        
        # Send recommendations
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=customer_id,
            message_type=MessageType.RECOMMENDATION_RESPONSE,
            content={'book_recommendations': recommendations}
        )
        
        logger.info(f"Employee {self.unique_id} sent {len(recommendations)} recommendations to {customer_id}")
    
    def _handle_restock_alert(self, message: Message) -> None:
        """
        Handle restock alert messages.
        
        Args:
            message: The restock alert message
        """
        book_id = message.content.get('book_id', '')
        current_stock = message.content.get('current_stock', 0)
        minimum_threshold = message.content.get('minimum_threshold', 3)
        
        logger.info(f"Employee {self.unique_id} received restock alert for {book_id}")
        
        if current_stock < minimum_threshold:
            restock_amount = 10  # Standard restock amount
            
            # Send restock confirmation
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=message.sender_id,
                message_type=MessageType.RESTOCK_CONFIRMATION,
                content={
                    'book_id': book_id,
                    'restock_amount': restock_amount
                }
            )
            
            logger.info(f"Employee {self.unique_id} confirmed restock of {restock_amount} for {book_id}")
            
            # Add task to workload
            self.current_tasks.append(f"Restock {book_id}")
            self.workload = min(10, self.workload + 1)
            
            # Update ontology
            self._sync_to_ontology()
    
    def _handle_assistance_request(self, message: Message) -> None:
        """
        Handle customer assistance request messages.
        
        Args:
            message: The assistance request message
        """
        request_type = message.content.get('request_type', '')
        details = message.content.get('details', {})
        
        logger.info(f"Employee {self.unique_id} received assistance request: {request_type}")
        
        # Process request based on type
        if request_type == 'find_book':
            self._handle_find_book_request(message.sender_id, details)
        elif request_type == 'recommendation':
            self._handle_recommendation_request(message.sender_id, details)
        else:
            # Generic response for unknown request types
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=message.sender_id,
                message_type=MessageType.ACKNOWLEDGEMENT,
                content={'message': f"Received your {request_type} request, processing..."}
            )
        
        # Update workload
        self.workload = min(10, self.workload + 1)
        self._sync_to_ontology()
    
    def _handle_genre_inquiry(self, message: Message) -> None:
        """
        Handle genre inquiry messages.
        
        Args:
            message: The genre inquiry message
        """
        genre = message.content.get('genre', '')
        
        logger.info(f"Employee {self.unique_id} received inquiry about {genre} genre")
        
        # Check if employee has expertise in this genre
        if genre in self.expertise_areas:
            # Get recommendations from ontology if possible
            recommendations = []
            
            if self.message_bus.ontology is not None:
                recommendations = self.message_bus.get_ontology_recommendations(
                    message.sender_id, 
                    genre=genre
                )
            
            # If ontology recommendations not available, create simulated ones
            if not recommendations:
                # Create dummy recommendations for the genre
                recommendations = [
                    {
                        'id': f"book_{genre.lower()}_classic",
                        'title': f"{genre} Classic",
                        'author': "Famous Author",
                        'price': 15.99,
                        'genre': [genre]
                    },
                    {
                        'id': f"book_{genre.lower()}_new",
                        'title': f"New {genre} Title",
                        'author': "Rising Author",
                        'price': 24.99,
                        'genre': [genre]
                    }
                ]
            
            # Send recommendations
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=message.sender_id,
                message_type=MessageType.RECOMMENDATION_RESPONSE,
                content={'book_recommendations': recommendations}
            )
            
            logger.info(f"Employee {self.unique_id} sent {len(recommendations)} {genre} recommendations")
        else:
            # Forward to appropriate colleague if available
            # For now, just send a generic response
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=message.sender_id,
                message_type=MessageType.ACKNOWLEDGEMENT,
                content={'message': f"We'll find an expert on {genre} to assist you"}
            )
    
    def _handle_stock_inquiry(self, message: Message) -> None:
        """
        Handle stock inquiry messages.
        
        Args:
            message: The stock inquiry message
        """
        book_id = message.content.get('book_id', '')
        
        logger.info(f"Employee {self.unique_id} received stock inquiry for {book_id}")
        
        # In a real system, would check actual inventory
        # Here we'll simulate a random stock level
        available = random.randint(0, 10)
        
        # Send response
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=message.sender_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={
                'book_id': book_id,
                'available': available,
                'message': f"We have {available} copies in stock"
            }
        )
        
        logger.info(f"Employee {self.unique_id} reported {available} copies of {book_id} in stock")
    
    def adjust_prices(self, pricing_data: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adjust book prices based on market data.
        Only managers can perform this operation.
        
        Args:
            pricing_data: Dictionary of book IDs to pricing info
            
        Returns:
            List of price updates made
        """
        if self.role != "Manager":
            logger.warning(f"Employee {self.unique_id} does not have permission to adjust prices")
            return []
        
        logger.info(f"Manager {self.unique_id} adjusting book prices...")
        
        price_updates = []
        
        for book_id, data in pricing_data.items():
            current_price = data.get('current_price', 0)
            demand_factor = data.get('demand_factor', 1.0)  # 1.0 is neutral
            competitor_price = data.get('competitor_price', current_price)
            
            # Apply pricing algorithm
            new_price = current_price
            
            # Adjust for demand (increase price for high demand, decrease for low)
            if demand_factor > 1.2:
                new_price *= 1.05  # Increase by 5%
            elif demand_factor < 0.8:
                new_price *= 0.95  # Decrease by 5%
            
            # Adjust for competitor pricing
            if competitor_price < current_price * 0.9:
                # Competitor significantly cheaper
                new_price = min(new_price, competitor_price * 1.05)
            
            # Round to nearest 99 cents
            new_price = round(new_price * 100) / 100
            new_price = (int(new_price) - 0.01) + 1.0
            
            if abs(new_price - current_price) > 0.01:
                # Price has changed significantly, update it
                price_updates.append({
                    'book_id': book_id,
                    'old_price': current_price,
                    'new_price': new_price
                })
                
                # Send price update message
                self.message_bus.send_message(
                    sender_id=self.unique_id,
                    receiver_id=book_id,
                    message_type=MessageType.PRICE_UPDATE,
                    content={
                        'book_id': book_id,
                        'old_price': current_price,
                        'new_price': new_price
                    }
                )
                
                logger.info(f"Updated price for {book_id}: Rs. {current_price} -> Rs. {new_price}")
        
        return price_updates
    
    def step(self) -> None:
        """
        Perform one simulation step for the employee agent.
        This is typically called by the simulation framework.
        """
        # Process any pending messages
        self.message_bus.process_messages()
        
        # Handle assistance requests
        self.assist_customers()
        
        # Reduce workload over time
        if self.workload > 0:
            self.workload -= 0.2
            self.workload = max(0, self.workload)
        
        # Sync with ontology at end of step
        self._sync_to_ontology()
    
    def _assign_role(self) -> None:
        """Assign proper EmployeeRole hierarchy to employee (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Randomly assign role based on distribution
            role_choice = random.random()
            
            with onto:
                if role_choice < 0.1:  # 10% Managers
                    role_instance = onto.Manager(f"ManagerRole_{self.unique_id}")
                    self.role = "Manager"
                elif role_choice < 0.3:  # 20% Supervisors
                    role_instance = onto.Supervisor(f"SupervisorRole_{self.unique_id}")
                    self.role = "Supervisor"
                elif role_choice < 0.8:  # 50% Staff
                    role_instance = onto.Staff(f"StaffRole_{self.unique_id}")
                    self.role = "Staff"
                else:  # 20% Interns
                    role_instance = onto.Intern(f"InternRole_{self.unique_id}")
                    self.role = "Intern"
                
                # Link employee to role
                if hasattr(self.ontology_ref, "hasRole"):
                    self.ontology_ref.hasRole = [role_instance]
                    self.role_instance = role_instance
                    logger.info(f"Assigned {self.role} role to {self.unique_id}")
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
    
    def manage_inventory_ontology(self, book_agent) -> None:
        """Link employee to Inventory management in ontology (NEW!)."""
        if not self.ontology_ref or not hasattr(book_agent, 'inventory_ref') or not book_agent.inventory_ref:
            return
            
        try:
            with onto:
                if hasattr(self.ontology_ref, "managesInventory"):
                    if book_agent.inventory_ref not in self.ontology_ref.managesInventory:
                        self.ontology_ref.managesInventory.append(book_agent.inventory_ref)
                        self.managed_inventory.append(book_agent.inventory_ref)
                        logger.info(f"{self.unique_id} now manages inventory {book_agent.inventory_ref.name}")
        except Exception as e:
            logger.error(f"Error managing inventory: {e}")
    
    def track_shipment(self, shipment_ref) -> None:
        """Track a Shipment in ontology (NEW!)."""
        if not self.ontology_ref or not shipment_ref:
            return
            
        try:
            with onto:
                if hasattr(self.ontology_ref, "tracksShipment"):
                    if shipment_ref not in self.ontology_ref.tracksShipment:
                        self.ontology_ref.tracksShipment.append(shipment_ref)
                        self.tracked_shipments.append(shipment_ref)
                        logger.info(f"{self.unique_id} now tracking shipment {shipment_ref.name}")
        except Exception as e:
            logger.error(f"Error tracking shipment: {e}")
    
    def manage_promotion(self, promotion_name: str, discount_pct: float) -> None:
        """Create and manage a Promotion (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find or create promotion
            promotion = None
            for promo in onto.Promotion.instances():
                if hasattr(promo, "promotionName") and promo.promotionName and promo.promotionName[0] == promotion_name:
                    promotion = promo
                    break
            
            # Create new promotion if not found
            if not promotion:
                with onto:
                    promo_id = f"Promo_{promotion_name.replace(' ', '')}"
                    promotion = onto.Promotion(promo_id)
                    promotion.promotionName = [promotion_name]
                    promotion.promotionStartDate = ["2025-10-01"]
                    promotion.promotionEndDate = ["2025-12-31"]
                    promotion.isActivePromotion = [True]
                    logger.info(f"Created Promotion: {promotion_name}")
            
            # Link employee to promotion management
            with onto:
                if hasattr(self.ontology_ref, "managesPromotion"):
                    if promotion not in self.ontology_ref.managesPromotion:
                        self.ontology_ref.managesPromotion.append(promotion)
                        self.managed_promotions.append(promotion)
                        logger.info(f"{self.unique_id} now managing promotion {promotion_name}")
        except Exception as e:
            logger.error(f"Error managing promotion: {e}")
    
    def organize_event(self, event_name: str, event_date: str, description: str) -> None:
        """Organize a BookEvent (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find or create event
            event = None
            for evt in onto.BookEvent.instances():
                if hasattr(evt, "eventName") and evt.eventName and evt.eventName[0] == event_name:
                    event = evt
                    break
            
            # Create new event if not found
            if not event:
                with onto:
                    event_id = f"Event_{event_name.replace(' ', '')}"
                    event = onto.BookEvent(event_id)
                    event.eventName = [event_name]
                    event.eventDate = [event_date]
                    event.eventDescription = [description]
                    event.isPublicEvent = [True]
                    logger.info(f"Created BookEvent: {event_name}")
            
            # Link employee to event organization
            with onto:
                if hasattr(self.ontology_ref, "organizesEvent"):
                    if event not in self.ontology_ref.organizesEvent:
                        self.ontology_ref.organizesEvent.append(event)
                        self.organized_events.append(event)
                        logger.info(f"{self.unique_id} now organizing event {event_name}")
        except Exception as e:
            logger.error(f"Error organizing event: {e}")


def test_agent_behavior():
    """Test the employee agent's core behaviors."""
    # Initialize message bus
    message_bus = MessageBus()
    
    # Create test employee
    employee = EmployeeAgent("employee1", message_bus)
    employee.role = "Manager"
    employee.expertise_areas = ["Mystery", "Science Fiction"]
    
    # Test inventory monitoring
    test_inventory = {
        'book1': 10,  # Good stock
        'book2': 2,   # Low stock, should trigger restock
        'book3': 0    # Out of stock, should trigger restock
    }
    
    print("Testing inventory monitoring...")
    restock_needed = employee.monitor_inventory(test_inventory)
    print(f"Books needing restock: {restock_needed}")
    
    # Test customer assistance
    print("\nTesting customer assistance...")
    message_bus.send_message(
        sender_id="customer1",
        receiver_id="employee1",
        message_type=MessageType.ASSISTANCE_REQUEST,
        content={
            'request_type': 'find_book',
            'details': {"title_keywords": "dragon", "author_keywords": ""}
        }
    )
    
    # Process messages
    processed = employee.assist_customers()
    print(f"Processed {processed} assistance requests")
    
    # Test price adjustment
    print("\nTesting price adjustment...")
    pricing_data = {
        'book1': {'current_price': 24.99, 'demand_factor': 1.5, 'competitor_price': 26.99},
        'book2': {'current_price': 19.99, 'demand_factor': 0.7, 'competitor_price': 17.99},
        'book3': {'current_price': 29.99, 'demand_factor': 1.0, 'competitor_price': 24.99}
    }
    
    price_updates = employee.adjust_prices(pricing_data)
    print(f"Made {len(price_updates)} price updates")
    
    print("\nEmployee agent testing complete!")


if __name__ == "__main__":
    test_agent_behavior()
