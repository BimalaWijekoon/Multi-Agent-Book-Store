"""
Book Agent Implementation for Bookstore Management System.

This module implements the Book agent behaviors that utilize the ontology,
SWRL rules, and message bus from previous phases.
"""

import random
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime

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


class BookAgent(mesa.Agent):
    """
    BookAgent implements behaviors for books in the bookstore.
    
    Core behaviors:
    - Dynamic State Management: Maintain pricing, inventory, and availability
    - Market-Responsive Pricing: Adjust prices based on demand
    - Transaction Processing: Handle purchases and update stock
    - Recommendation Network: Participate in book suggestion algorithms
    """
    
    def __init__(self, unique_id: str, model, message_bus: MessageBus, ontology_individual=None):
        """
        Initialize a new Book agent.
        
        Args:
            unique_id: The agent's unique identifier
            model: The model instance the agent is part of
            message_bus: The message bus for communication
            ontology_individual: The ontology individual representing this book
        """
        # Initialize Mesa agent correctly - model first, then other params
        mesa.Agent.__init__(self, model)
        # Override the auto-assigned unique_id with our custom one
        self.unique_id = unique_id
        self.message_bus = message_bus
        self.pos = None  # Position in the grid
        self.ontology_ref = ontology_individual
        
        # Initialize book properties
        self.title = "Unknown Title"
        self.author = "Unknown Author"
        self.genre = "Fiction"  # Default genre
        self.genres = []
        self.price = 19.99  # Default price
        self.current_price = 19.99  # Default price
        self.stock_level = 10  # Default stock
        self.demand_level = 5  # Scale of 0-10
        self.purchase_count = 0
        self.related_books = []  # IDs of related books
        self.publisher = "Unknown Publisher"
        self.rating = 4.0  # Default rating
        self.revenue = 0.0
        self.sold_count = 0
        self.inventory_ref = None  # NEW: Reference to Inventory instance
        self.supplier_ref = None  # NEW: Reference to Supplier instance
        self.shipment_ref = None  # NEW: Reference to Shipment instance
        self.promotion_ref = None  # NEW: Reference to active Promotion
        self.review_count = 0  # NEW: Track number of reviews
        
        # Register with message bus
        self.message_bus.register_agent(self.unique_id, AgentType.BOOK)
        
        # Subscribe to relevant message types
        self.message_bus.subscribe(self.unique_id, [
            MessageType.PURCHASE_REQUEST,
            MessageType.PAYMENT_PROCESS,
            MessageType.RESTOCK_CONFIRMATION,
            MessageType.STOCK_INQUIRY,
            MessageType.GENRE_INQUIRY,
            MessageType.PRICE_UPDATE
        ])
        
        # Register message handlers
        self.message_bus.register_handler(MessageType.PURCHASE_REQUEST, self._handle_purchase_request)
        self.message_bus.register_handler(MessageType.PAYMENT_PROCESS, self._handle_payment_process)
        self.message_bus.register_handler(MessageType.RESTOCK_CONFIRMATION, self._handle_restock_confirmation)
        self.message_bus.register_handler(MessageType.STOCK_INQUIRY, self._handle_stock_inquiry)
        self.message_bus.register_handler(MessageType.GENRE_INQUIRY, self._handle_genre_inquiry)
        self.message_bus.register_handler(MessageType.PRICE_UPDATE, self._handle_price_update)
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            self._create_inventory()  # NEW: Create Inventory instance
            self._assign_supplier()   # NEW: Assign a Supplier
        
    def step(self):
        """
        Perform a single step of the agent.
        Required by the Mesa framework.
        """
        # Process any pending messages
        if hasattr(self, 'message_bus'):
            self.message_bus.process_messages()
        
        # Periodically adjust pricing (with some randomness)
        if random.random() < 0.2:  # 20% chance each step
            self.adjust_pricing()
        
        # Sync with ontology at end of step if available
        if hasattr(self, 'ontology_ref') and hasattr(self, '_sync_to_ontology'):
            self._sync_to_ontology()
        
        # Register targeted message handlers (with agent_id for direct routing)
        self.message_bus.register_handler(MessageType.PURCHASE_REQUEST, self._handle_purchase_request, self.unique_id)
        self.message_bus.register_handler(MessageType.PAYMENT_PROCESS, self._handle_payment_process, self.unique_id)
        self.message_bus.register_handler(MessageType.RESTOCK_CONFIRMATION, self._handle_restock_confirmation, self.unique_id)
        self.message_bus.register_handler(MessageType.STOCK_INQUIRY, self._handle_stock_inquiry, self.unique_id)
        self.message_bus.register_handler(MessageType.GENRE_INQUIRY, self._handle_genre_inquiry, self.unique_id)
        self.message_bus.register_handler(MessageType.PRICE_UPDATE, self._handle_price_update, self.unique_id)
        
        # Sync with ontology if available
        if self.ontology_ref:
            self._sync_from_ontology()
            
        logger.info(f"Book agent {self.unique_id} initialized: {self.title} by {self.author}")
    
    def _sync_from_ontology(self):
        """Synchronize agent state from the ontology individual."""
        try:
            if hasattr(self.ontology_ref, "hasTitle"):
                self.title = str(self.ontology_ref.hasTitle)
                
            if hasattr(self.ontology_ref, "hasAuthor"):
                self.author = str(self.ontology_ref.hasAuthor)
                
            if hasattr(self.ontology_ref, "hasGenre"):
                self.genres = [str(genre) for genre in self.ontology_ref.hasGenre]
                
            if hasattr(self.ontology_ref, "hasPrice"):
                self.current_price = float(self.ontology_ref.hasPrice)
                
            if hasattr(self.ontology_ref, "hasStock"):
                self.stock_level = int(self.ontology_ref.hasStock)
                
            if hasattr(self.ontology_ref, "hasDemand"):
                self.demand_level = int(self.ontology_ref.hasDemand)
                
            if hasattr(self.ontology_ref, "hasPurchaseCount"):
                self.purchase_count = int(self.ontology_ref.hasPurchaseCount)
                
            if hasattr(self.ontology_ref, "isRelatedTo"):
                self.related_books = [
                    str(book.hasID) if hasattr(book, "hasID") else str(book)
                    for book in self.ontology_ref.isRelatedTo
                ]
                
            logger.debug(f"Book {self.unique_id} synchronized from ontology")
        except Exception as e:
            logger.error(f"Error syncing from ontology: {e}")
    
    def _sync_to_ontology(self):
        """Update the ontology individual with current agent state."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                if hasattr(self.ontology_ref, "hasPrice"):
                    self.ontology_ref.hasPrice = self.current_price
                if hasattr(self.ontology_ref, "hasStock"):
                    self.ontology_ref.hasStock = self.stock_level
                if hasattr(self.ontology_ref, "hasDemand"):
                    self.ontology_ref.hasDemand = self.demand_level
                if hasattr(self.ontology_ref, "hasPurchaseCount"):
                    self.ontology_ref.hasPurchaseCount = self.purchase_count
            logger.debug(f"Book {self.unique_id} state updated in ontology")
        except Exception as e:
            logger.error(f"Error updating ontology: {e}")
    
    def process_purchase_request(self, customer_id: str, customer_budget: float) -> bool:
        """
        Process a purchase request from a customer and COMPLETE THE SALE.
        
        Args:
            customer_id: The ID of the customer making the request
            customer_budget: The customer's budget
            
        Returns:
            True if purchase was completed successfully
        """
        logger.info(f"Processing purchase request from {customer_id} for {self.title}")
        
        # Check if book is in stock
        if self.stock_level <= 0:
            logger.info(f"Book {self.unique_id} out of stock")
            return False
        
        # Check if customer can afford the book
        if customer_budget < self.current_price:
            logger.info(f"Customer {customer_id} cannot afford {self.title} (Rs. {self.current_price})")
            return False
        
        # ACTUALLY COMPLETE THE SALE
        # 1. Decrement stock
        self.stock_level -= 1
        
        # 2. Add to revenue
        self.revenue += self.current_price
        
        # 3. Increment sold count
        self.sold_count += 1
        
        # 4. Increment purchase count
        self.purchase_count += 1
        
        # 5. Increase demand
        self.demand_level = min(10, self.demand_level + 1)
        
        # 6. Sync to ontology
        self._sync_to_ontology()
        
        logger.info(f"âœ“ SALE COMPLETED: {self.title} sold to {customer_id} for Rs. {self.current_price:.2f}. Stock: {self.stock_level}, Revenue: Rs. {self.revenue:.2f}, Sold: {self.sold_count}")
        
        # Send purchase confirmation with sale details
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=customer_id,
            message_type=MessageType.PURCHASE_CONFIRMATION,
            content={
                'book_id': self.unique_id,
                'title': self.title,
                'price': self.current_price,
                'available': True,
                'sale_completed': True,
                'new_stock': self.stock_level
            }
        )
        
        logger.info(f"Sent purchase confirmation to {customer_id} for {self.title}")
        return True
    
    def adjust_pricing(self) -> bool:
        """
        Adjust the book's price based on demand and stock.
        
        Returns:
            True if price was adjusted
        """
        logger.info(f"Adjusting price for {self.title}")
        
        # Store original price
        original_price = self.current_price
        
        # Adjust price based on demand level (0-10)
        demand_factor = 1.0
        if self.demand_level > 7:
            demand_factor = 1.1  # High demand: increase price
        elif self.demand_level < 3:
            demand_factor = 0.9  # Low demand: decrease price
        
        # Adjust price based on stock level
        stock_factor = 1.0
        if self.stock_level < 3 and self.stock_level > 0:
            stock_factor = 1.05  # Low stock: increase price
        elif self.stock_level > 20:
            stock_factor = 0.95  # High stock: decrease price
        
        # Calculate new price
        new_price = self.current_price * demand_factor * stock_factor
        
        # Apply constraints: never more than 30% change, minimum Rs. 300
        max_increase = self.current_price * 1.3
        min_decrease = self.current_price * 0.7
        new_price = max(min(new_price, max_increase), min_decrease)
        new_price = max(new_price, 300.0)  # Minimum Rs. 300
        
        # Round to nearest 99 cents
        new_price = round(new_price * 100) / 100
        new_price = (int(new_price) - 0.01) + 1.0
        
        # Update price if significantly different
        if abs(new_price - self.current_price) > 0.5:
            logger.info(f"Price for {self.title} adjusted: Rs. {self.current_price:.2f} -> Rs. {new_price:.2f}")
            
            # Store old price for notification
            old_price = self.current_price
            
            # Update price
            self.current_price = new_price
            
            # Sync to ontology
            self._sync_to_ontology()
            
            # Notify about price change
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id="system",
                message_type=MessageType.PRICE_UPDATE,
                content={
                    'book_id': self.unique_id,
                    'old_price': old_price,
                    'new_price': new_price
                }
            )
            
            return True
        
        logger.debug(f"Price for {self.title} unchanged at Rs. {self.current_price:.2f}")
        return False
    
    def update_inventory(self, quantity_change: int) -> int:
        """
        Update the book's inventory level.
        
        Args:
            quantity_change: The amount to change the stock by
            
        Returns:
            New stock level
        """
        logger.info(f"Updating inventory for {self.title} by {quantity_change}")
        
        # Update stock level
        self.stock_level += quantity_change
        self.stock_level = max(0, self.stock_level)  # Cannot go below 0
        
        # Sync to ontology
        self._sync_to_ontology()
        
        # Check if restock needed
        if self.stock_level < 3:
            # Send restock alert
            self.message_bus.broadcast_message(
                sender_id=self.unique_id,
                message_type=MessageType.RESTOCK_ALERT,
                content={
                    'book_id': self.unique_id,
                    'current_stock': self.stock_level,
                    'minimum_threshold': 3
                },
                target_agent_type=AgentType.EMPLOYEE
            )
            
            logger.info(f"Sent restock alert for {self.title} (stock: {self.stock_level})")
        
        logger.info(f"New stock level for {self.title}: {self.stock_level}")
        return self.stock_level
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommendations for related books.
        
        Returns:
            List of recommended book information
        """
        recommendations = []
        
        # Check ontology for related books
        if self.ontology_ref and onto is not None:
            try:
                # Find related books in ontology
                related_books = []
                
                if hasattr(self.ontology_ref, "isRelatedTo"):
                    related_books = list(self.ontology_ref.isRelatedTo)
                
                # Get books with matching genres
                if hasattr(self.ontology_ref, "hasGenre"):
                    genres = list(self.ontology_ref.hasGenre)
                    
                    for book in onto.Book.instances():
                        if book == self.ontology_ref:
                            continue  # Skip self
                            
                        if hasattr(book, "hasGenre"):
                            book_genres = list(book.hasGenre)
                            
                            # Check for genre overlap
                            common_genres = set(genres).intersection(set(book_genres))
                            if common_genres:
                                related_books.append(book)
                
                # Convert to recommendation format
                for book in related_books:
                    if book == self.ontology_ref:
                        continue  # Skip self
                        
                    book_info = {
                        'id': book.hasID if hasattr(book, "hasID") else str(book),
                        'title': book.hasTitle if hasattr(book, "hasTitle") else "Unknown",
                        'author': book.hasAuthor if hasattr(book, "hasAuthor") else "Unknown",
                        'price': book.hasPrice if hasattr(book, "hasPrice") else 0.0,
                        'genres': [str(genre) for genre in book.hasGenre] if hasattr(book, "hasGenre") else []
                    }
                    
                    recommendations.append(book_info)
            except Exception as e:
                logger.error(f"Error getting related books from ontology: {e}")
        
        # If no recommendations from ontology, create simulated ones
        if not recommendations:
            # Create dummy recommendations
            dummy_recommendations = [
                {
                    'id': f"related_to_{self.unique_id}_1",
                    'title': f"Related to {self.title} - Volume 1",
                    'author': self.author,
                    'price': self.current_price + 2.0,
                    'genres': self.genres
                },
                {
                    'id': f"related_to_{self.unique_id}_2",
                    'title': f"Related to {self.title} - Volume 2",
                    'author': self.author,
                    'price': self.current_price + 4.0,
                    'genres': self.genres
                }
            ]
            recommendations.extend(dummy_recommendations)
        
        return recommendations
    
    def _handle_purchase_request(self, message: Message) -> None:
        """
        Handle purchase request messages.
        
        Args:
            message: The purchase request message
        """
        customer_id = message.sender_id
        book_id = message.content.get('book_id', '')
        customer_budget = message.content.get('customer_budget', 0.0)
        
        # Verify this is for the right book
        if book_id != self.unique_id and book_id != "":
            logger.warning(f"Book {self.unique_id} received purchase request for {book_id}")
            return
        
        logger.info(f"Book {self.unique_id} received purchase request from {customer_id}")
        
        # Process the purchase request
        self.process_purchase_request(customer_id, customer_budget)
        
        # Increase demand level slightly for each request
        self.demand_level = min(10, self.demand_level + 0.5)
        self._sync_to_ontology()
    
    def _handle_payment_process(self, message: Message) -> None:
        """
        Handle payment process messages.
        
        Args:
            message: The payment process message
        """
        customer_id = message.sender_id
        book_id = message.content.get('book_id', '')
        amount = message.content.get('amount', 0.0)
        
        # Verify this is for the right book
        if book_id != self.unique_id and book_id != "":
            logger.warning(f"Book {self.unique_id} received payment for {book_id}")
            return
            
        logger.info(f"Book {self.unique_id} received payment of Rs. {amount} from {customer_id}")
        
        # Process the payment
        # Update stock level
        self.update_inventory(-1)
        
        # Update purchase count
        self.purchase_count += 1
        
        # Increase demand level
        self.demand_level = min(10, self.demand_level + 1)
        
        # Sync to ontology
        self._sync_to_ontology()
        
        # Send acknowledgement
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=customer_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={
                'message': f"Thank you for purchasing {self.title}",
                'original_message_id': message.id
            }
        )
        
        # Send inventory update notification
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id="system",
            message_type=MessageType.INVENTORY_UPDATE,
            content={
                'book_id': self.unique_id,
                'quantity_change': -1
            }
        )
        
        logger.info(f"Book {self.unique_id} processed payment, new stock: {self.stock_level}")
    
    def _handle_restock_confirmation(self, message: Message) -> None:
        """
        Handle restock confirmation messages.
        
        Args:
            message: The restock confirmation message
        """
        employee_id = message.sender_id
        book_id = message.content.get('book_id', '')
        restock_amount = message.content.get('restock_amount', 0)
        
        # Verify this is for the right book
        if book_id != self.unique_id and book_id != "":
            logger.warning(f"Book {self.unique_id} received restock confirmation for {book_id}")
            return
            
        logger.info(f"Book {self.unique_id} received restock confirmation for {restock_amount} units")
        
        # Update inventory
        self.update_inventory(restock_amount)
        
        # Decrease demand level slightly due to increased availability
        self.demand_level = max(0, self.demand_level - 1)
        
        # Sync to ontology
        self._sync_to_ontology()
        
        # Send acknowledgement
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=employee_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={
                'message': f"Restocked {self.title} with {restock_amount} units",
                'original_message_id': message.id
            }
        )
    
    def _handle_stock_inquiry(self, message: Message) -> None:
        """
        Handle stock inquiry messages.
        
        Args:
            message: The stock inquiry message
        """
        inquirer_id = message.sender_id
        book_id = message.content.get('book_id', '')
        
        # Verify this is for the right book
        if book_id != self.unique_id and book_id != "":
            logger.warning(f"Book {self.unique_id} received stock inquiry for {book_id}")
            return
            
        logger.info(f"Book {self.unique_id} received stock inquiry from {inquirer_id}")
        
        # Send response with current stock
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=inquirer_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={
                'book_id': self.unique_id,
                'title': self.title,
                'stock': self.stock_level,
                'price': self.current_price,
                'message': f"Current stock for {self.title}: {self.stock_level} units at Rs. {self.current_price:.2f}"
            }
        )
        
        logger.info(f"Book {self.unique_id} responded to stock inquiry")
    
    def _handle_genre_inquiry(self, message: Message) -> None:
        """
        Handle genre inquiry messages.
        
        Args:
            message: The genre inquiry message
        """
        inquirer_id = message.sender_id
        genre = message.content.get('genre', '')
        
        logger.info(f"Book {self.unique_id} received genre inquiry for {genre}")
        
        # Check if this book matches the genre
        if genre.lower() in [g.lower() for g in self.genres]:
            # This book matches the requested genre
            logger.info(f"Book {self.unique_id} matches genre {genre}")
            
            # Send recommendation for this book
            self.message_bus.send_message(
                sender_id=self.unique_id,
                receiver_id=inquirer_id,
                message_type=MessageType.RECOMMENDATION_RESPONSE,
                content={
                    'book_recommendations': [
                        {
                            'id': self.unique_id,
                            'title': self.title,
                            'author': self.author,
                            'price': self.current_price,
                            'genre': self.genres
                        }
                    ]
                }
            )
            
            # Send recommendations for related books
            related_recommendations = self.get_recommendations()
            if related_recommendations:
                self.message_bus.send_message(
                    sender_id=self.unique_id,
                    receiver_id=inquirer_id,
                    message_type=MessageType.RECOMMENDATION_RESPONSE,
                    content={'book_recommendations': related_recommendations}
                )
        else:
            # This book doesn't match the requested genre
            logger.debug(f"Book {self.unique_id} does not match genre {genre}")
    
    def _handle_price_update(self, message: Message) -> None:
        """
        Handle price update messages.
        
        Args:
            message: The price update message
        """
        book_id = message.content.get('book_id', '')
        old_price = message.content.get('old_price', 0.0)
        new_price = message.content.get('new_price', 0.0)
        
        # Verify this is for the right book
        if book_id != self.unique_id and book_id != "":
            logger.debug(f"Book {self.unique_id} received price update for {book_id}")
            return
            
        logger.info(f"Book {self.unique_id} received price update: Rs. {old_price:.2f} -> Rs. {new_price:.2f}")
        
        # Update price
        self.current_price = new_price
        
        # Sync to ontology
        self._sync_to_ontology()
        
        # Send acknowledgement
        self.message_bus.send_message(
            sender_id=self.unique_id,
            receiver_id=message.sender_id,
            message_type=MessageType.ACKNOWLEDGEMENT,
            content={
                'message': f"Price updated for {self.title}",
                'original_message_id': message.id
            }
        )
    
    def step(self) -> None:
        """
        Perform one simulation step for the book agent.
        This is typically called by the simulation framework.
        """
        # Process any pending messages
        self.message_bus.process_messages()
        
        # Periodically adjust pricing (with some randomness)
        if random.random() < 0.2:  # 20% chance each step
            self.adjust_pricing()
        
        # Sync with ontology at end of step
        self._sync_to_ontology()
    
    def _create_inventory(self) -> None:
        """Create Inventory instance for this book (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            with onto:
                # Create Inventory instance
                inventory_id = f"Inventory_{self.unique_id}"
                inventory = onto.Inventory(inventory_id)
                inventory.availableQuantity = [self.stock_level]
                
                # Link book to inventory
                if hasattr(self.ontology_ref, "inStock"):
                    self.ontology_ref.inStock.append(inventory)
                    self.inventory_ref = inventory
                    logger.info(f"Created Inventory for {self.unique_id} with {self.stock_level} units")
        except Exception as e:
            logger.error(f"Error creating inventory: {e}")
    
    def _assign_supplier(self) -> None:
        """Assign a Supplier to this book (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find existing supplier or create new one
            supplier = None
            supplier_names = ["ABC Books", "BookWorld Distributors", "Global Publishing Supply"]
            
            # Try to find existing supplier first
            for supp in onto.Supplier.instances():
                if hasattr(supp, "supplierName") and supp.supplierName:
                    supplier = supp
                    break
            
            # If no supplier exists, create one
            if not supplier:
                with onto:
                    supplier_name = random.choice(supplier_names)
                    supplier_id = f"Supplier_{supplier_name.replace(' ', '')}"
                    supplier = onto.Supplier(supplier_id)
                    supplier.supplierName = [supplier_name]
                    supplier.supplierContact = [f"contact@{supplier_name.lower().replace(' ', '')}.com"]
                    supplier.isPreferredSupplier = [random.choice([True, False])]
                    logger.info(f"Created Supplier: {supplier_name}")
            
            # Link book to supplier
            with onto:
                if hasattr(self.ontology_ref, "suppliedBy"):
                    self.ontology_ref.suppliedBy.append(supplier)
                    self.supplier_ref = supplier
                    logger.info(f"Linked {self.unique_id} to supplier {supplier.name}")
        except Exception as e:
            logger.error(f"Error assigning supplier: {e}")
    
    def create_shipment(self, quantity: int = None) -> None:
        """Create a Shipment for restocking this book (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            qty = quantity if quantity else max(10, self.stock_level)
            
            with onto:
                # Create Shipment instance
                shipment_id = f"Shipment_{self.unique_id}_{random.randint(1000, 9999)}"
                shipment = onto.Shipment(shipment_id)
                shipment.shipmentStatus = ["In Transit"]
                shipment.estimatedDelivery = ["2025-10-15"]  # 10 days from now
                shipment.shipmentQuantity = [qty]
                
                # Link book to shipment
                if hasattr(self.ontology_ref, "inShipment"):
                    self.ontology_ref.inShipment.append(shipment)
                    self.shipment_ref = shipment
                    logger.info(f"Created Shipment {shipment_id} with {qty} units for {self.unique_id}")
        except Exception as e:
            logger.error(f"Error creating shipment: {e}")
    
    def add_to_promotion(self, promotion_name: str, discount_pct: float) -> None:
        """Add this book to a promotion (NEW!)."""
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
            
            # Link book to promotion
            with onto:
                if hasattr(self.ontology_ref, "hasPromotion"):
                    self.ontology_ref.hasPromotion.append(promotion)
                    self.promotion_ref = promotion
                    logger.info(f"Added {self.unique_id} to promotion {promotion_name}")
        except Exception as e:
            logger.error(f"Error adding to promotion: {e}")
    
    def feature_in_event(self, event_name: str) -> None:
        """Feature this book in a bookstore event (NEW!)."""
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
                    event.eventDate = ["2025-10-20"]
                    event.eventDescription = [f"Special event featuring {self.title}"]
                    event.isPublicEvent = [True]
                    logger.info(f"Created BookEvent: {event_name}")
            
            # Link book to event
            with onto:
                if hasattr(self.ontology_ref, "featuredInEvent"):
                    self.ontology_ref.featuredInEvent.append(event)
                    logger.info(f"Featured {self.unique_id} in event {event_name}")
        except Exception as e:
            logger.error(f"Error featuring in event: {e}")
    
    def add_to_reading_program(self, program_name: str) -> None:
        """Add this book to a reading program (NEW!)."""
        if not self.ontology_ref:
            return
            
        try:
            # Find or create program
            program = None
            for prog in onto.ReadingProgram.instances():
                if hasattr(prog, "programName") and prog.programName and prog.programName[0] == program_name:
                    program = prog
                    break
            
            # Create new program if not found
            if not program:
                with onto:
                    program_id = f"Program_{program_name.replace(' ', '')}"
                    program = onto.ReadingProgram(program_id)
                    program.programName = [program_name]
                    program.programDescription = [f"Reading program featuring {self.genre} books"]
                    program.programDuration = [12]  # 12 weeks
                    logger.info(f"Created ReadingProgram: {program_name}")
            
            # Link book to program
            with onto:
                if hasattr(self.ontology_ref, "featuredInProgram"):
                    self.ontology_ref.featuredInProgram.append(program)
                    logger.info(f"Added {self.unique_id} to program {program_name}")
        except Exception as e:
            logger.error(f"Error adding to reading program: {e}")


def test_agent_behavior():
    """Test the book agent's core behaviors."""
    # Initialize message bus
    message_bus = MessageBus()
    
    # Create test book
    book = BookAgent("book1", None, message_bus)  # Pass None for model parameter
    book.title = "Test Book"
    book.author = "Test Author"
    book.genres = ["Fantasy", "Adventure"]
    book.current_price = 24.99
    book.stock_level = 10
    
    # Test purchase request processing
    print("Testing purchase request processing...")
    message_bus.send_message(
        sender_id="customer1",
        receiver_id="book1",
        message_type=MessageType.PURCHASE_REQUEST,
        content={
            'book_id': 'book1',
            'customer_budget': 30.0
        }
    )
    
    # Process messages
    message_bus.process_messages()
    
    # Test inventory update
    print("\nTesting inventory update...")
    new_stock = book.update_inventory(-2)
    print(f"New stock level: {new_stock}")
    
    # Test price adjustment
    print("\nTesting price adjustment...")
    book.demand_level = 8  # High demand
    price_adjusted = book.adjust_pricing()
    print(f"Price adjusted: {price_adjusted}, New price: Rs. {book.current_price:.2f}")
    
    # Test stock inquiry
    print("\nTesting stock inquiry...")
    message_bus.send_message(
        sender_id="customer1",
        receiver_id="book1",
        message_type=MessageType.STOCK_INQUIRY,
        content={'book_id': 'book1'}
    )
    
    # Process messages
    message_bus.process_messages()
    
    # Test payment processing
    print("\nTesting payment processing...")
    message_bus.send_message(
        sender_id="customer1",
        receiver_id="book1",
        message_type=MessageType.PAYMENT_PROCESS,
        content={
            'book_id': 'book1',
            'amount': book.current_price
        }
    )
    
    # Process messages
    message_bus.process_messages()
    
    # Get recommendations
    print("\nTesting recommendations...")
    recommendations = book.get_recommendations()
    print(f"Found {len(recommendations)} related book recommendations")
    
    print("\nBook agent testing complete!")


if __name__ == "__main__":
    test_agent_behavior()
