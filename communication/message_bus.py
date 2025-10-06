"""
Message Bus Communication System for Bookstore Management System

This module provides a sophisticated message-passing infrastructure for communication
between Customer, Employee, and Book agents. It integrates with the ontology properties
and SWRL rules from previous phases.
"""

import time
import uuid
import logging
import heapq
import importlib.util
import os
from enum import Enum
from typing import Dict, List, Any, Callable, Optional, Set, Tuple
from queue import PriorityQueue
from dataclasses import dataclass, field

# Dynamically import the ontology - this allows the message_bus to work even if ontology isn't available
ontology_spec = importlib.util.find_spec("ontology.advanced_bookstore_ontology")
if ontology_spec:
    bookstore_ontology = importlib.util.module_from_spec(ontology_spec)
    ontology_spec.loader.exec_module(bookstore_ontology)
else:
    bookstore_ontology = None
    
# Import the rules engine if available
rules_spec = importlib.util.find_spec("ontology.bookstore_rules")
if rules_spec:
    bookstore_rules = importlib.util.module_from_spec(rules_spec)
    rules_spec.loader.exec_module(bookstore_rules)
else:
    bookstore_rules = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Enum defining all possible message types in the system."""
    
    # Purchase-related messages
    PURCHASE_REQUEST = "purchase_request"
    PURCHASE_CONFIRMATION = "purchase_confirmation"
    PAYMENT_PROCESS = "payment_process"
    INVENTORY_UPDATE = "inventory_update"
    
    # Inventory management messages
    RESTOCK_ALERT = "restock_alert"
    RESTOCK_CONFIRMATION = "restock_confirmation"
    STOCK_INQUIRY = "stock_inquiry"
    SUPPLIER_NOTIFICATION = "supplier_notification"
    
    # Customer service messages
    ASSISTANCE_REQUEST = "assistance_request"
    RECOMMENDATION_RESPONSE = "recommendation_response"
    GENRE_INQUIRY = "genre_inquiry"
    PRICE_UPDATE = "price_update"
    
    # System messages
    BROADCAST = "broadcast"
    ERROR = "error"
    ACKNOWLEDGEMENT = "acknowledgement"


class MessageStatus(Enum):
    """Enum defining possible message statuses."""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    EXPIRED = "expired"
    FAILED = "failed"


class AgentType(Enum):
    """Enum defining agent types that match ontology classes."""
    CUSTOMER = "Customer"
    EMPLOYEE = "Employee"
    BOOK = "Book"
    SYSTEM = "System"


class Message:
    """
    Core message class for agent communication.
    
    This class represents a message sent between agents in the bookstore system.
    Messages have a sender, receiver, type, content, and other metadata.
    """
    
    def __init__(
        self, 
        sender_id: str, 
        receiver_id: str, 
        message_type: MessageType,
        content: Dict[str, Any],
        timestamp: Optional[float] = None,
        priority: int = 5,  # Priority from 1 (highest) to 10 (lowest)
        expiry: Optional[float] = None  # Time in seconds until message expires
    ):
        """
        Initialize a new message.
        
        Args:
            sender_id: The ID of the sending agent
            receiver_id: The ID of the receiving agent
            message_type: Type of message from MessageType enum
            content: Dictionary containing message data
            timestamp: Time the message was created (default: current time)
            priority: Message priority (1=highest, 10=lowest)
            expiry: Time in seconds until message expires (None=never expires)
        """
        self.id = str(uuid.uuid4())  # Generate unique message ID
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.content = content
        self.timestamp = timestamp or time.time()
        self.status = MessageStatus.PENDING
        self.priority = priority
        self.expiry = expiry and (self.timestamp + expiry)
        self.response_to = content.get('response_to')  # Optional ID of message being responded to
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.expiry is None:
            return False
        return time.time() > self.expiry
    
    def __lt__(self, other):
        """
        Compare messages for priority queue.
        Messages with lower priority value come first (higher priority).
        """
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp
    
    def __repr__(self):
        return (f"Message(id={self.id}, type={self.message_type}, "
                f"sender={self.sender_id}, receiver={self.receiver_id}, "
                f"status={self.status})")


class MessageBus:
    """
    Central communication system for agent message passing.
    
    Handles message queuing, routing, validation, and delivery between agents.
    Integrates with the ontology and SWRL rules system.
    """
    
    def __init__(self):
        """Initialize the message bus system."""
        self.message_queue = PriorityQueue()
        self.message_history: Dict[str, Message] = {}
        self.subscribers: Dict[MessageType, Set[str]] = {
            msg_type: set() for msg_type in MessageType
        }
        self.agent_registry: Dict[str, AgentType] = {}
        self.handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        # Agent-specific handlers: maps agent_id -> message_type -> handler
        self.agent_handlers: Dict[str, Dict[MessageType, Callable]] = {}
        self.pending_responses: Dict[str, str] = {}  # Maps response_to to original message
        
        logger.info("Message Bus initialized with targeted routing")
    
    def register_agent(self, agent_id: str, agent_type: AgentType):
        """
        Register an agent with the message bus.
        
        Args:
            agent_id: The unique ID of the agent
            agent_type: The type of the agent from AgentType enum
        """
        self.agent_registry[agent_id] = agent_type
        logger.debug(f"Registered agent {agent_id} of type {agent_type.value}")
        
    def is_registered(self, agent_id: str) -> bool:
        """
        Check if an agent is registered with the message bus.
        
        Args:
            agent_id: The ID of the agent to check
            
        Returns:
            True if the agent is registered, False otherwise
        """
        return agent_id in self.agent_registry
    
    def subscribe(self, agent_id: str, message_types):
        """
        Subscribe an agent to receive specific message types.
        
        Args:
            agent_id: The ID of the subscribing agent
            message_types: MessageType enum or list of MessageType enums to subscribe to
        """
        # Convert single message type to list if needed
        if not isinstance(message_types, list):
            message_types = [message_types]
            
        for msg_type in message_types:
            if msg_type not in self.subscribers:
                self.subscribers[msg_type] = set()
            self.subscribers[msg_type].add(agent_id)
        logger.debug(f"Agent {agent_id} subscribed to {[m.value for m in message_types]}")
    
    def register_handler(self, message_type: MessageType, handler_func: Callable, agent_id: str = None):
        """
        Register a handler function for a specific message type.
        
        Args:
            message_type: The MessageType to handle
            handler_func: Function to call when this message type is processed
            agent_id: Optional agent ID for targeted handler registration
        """
        if agent_id:
            # Register agent-specific handler for targeted delivery
            if agent_id not in self.agent_handlers:
                self.agent_handlers[agent_id] = {}
            self.agent_handlers[agent_id][message_type] = handler_func
            logger.debug(f"Registered targeted handler for {message_type.value} -> {agent_id}")
        else:
            # Register global handler (for backwards compatibility and broadcasts)
            self.handlers[message_type].append(handler_func)
            logger.debug(f"Registered global handler for {message_type.value}")
    
    def send_message(
        self, 
        sender_id: str, 
        receiver_id: str, 
        message_type: MessageType,
        content: Dict[str, Any],
        priority: int = 5,
        expiry: Optional[float] = None
    ) -> str:
        """
        Send a message from one agent to another.
        
        Args:
            sender_id: The ID of the sending agent
            receiver_id: The ID of the receiving agent
            message_type: Type of message from MessageType enum
            content: Dictionary containing message data
            priority: Message priority (1=highest, 10=lowest)
            expiry: Time in seconds until message expires
            
        Returns:
            The ID of the sent message
        """
        # Create the message
        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            content=content,
            priority=priority,
            expiry=expiry
        )
        
        # Store in history
        self.message_history[message.id] = message
        
        # Add to queue
        self.message_queue.put(message)
        
        logger.info(f"Message queued: {message}")
        return message.id
    
    def broadcast_message(
        self, 
        sender_id: str, 
        message_type: MessageType,
        content: Dict[str, Any],
        target_agent_type: Optional[AgentType] = None,
        priority: int = 5,
        expiry: Optional[float] = None
    ) -> List[str]:
        """
        Broadcast a message to multiple agents.
        
        Args:
            sender_id: The ID of the sending agent
            message_type: Type of message from MessageType enum
            content: Dictionary containing message data
            target_agent_type: Optional filter for agent types to receive message
            priority: Message priority (1=highest, 10=lowest)
            expiry: Time in seconds until message expires
            
        Returns:
            List of sent message IDs
        """
        message_ids = []
        
        # Find all subscribers for this message type
        receivers = self.subscribers.get(message_type, set())
        
        # Filter by agent type if specified
        if target_agent_type:
            receivers = {
                agent_id for agent_id in receivers
                if self.agent_registry.get(agent_id) == target_agent_type
            }
        
        # Send to each receiver
        for receiver_id in receivers:
            msg_id = self.send_message(
                sender_id=sender_id,
                receiver_id=receiver_id,
                message_type=message_type,
                content=content,
                priority=priority,
                expiry=expiry
            )
            message_ids.append(msg_id)
        
        return message_ids
    
    def validate_message(self, message: Message) -> bool:
        """
        Validate a message before processing.
        
        Args:
            message: The message to validate
            
        Returns:
            True if message is valid, False otherwise
        """
        # Check for expiry
        if message.is_expired():
            logger.warning(f"Message {message.id} has expired")
            message.status = MessageStatus.EXPIRED
            return False
        
        # Validate sender
        if not self.validate_sender(message.sender_id, message.message_type):
            logger.warning(f"Invalid sender {message.sender_id} for message type {message.message_type}")
            message.status = MessageStatus.FAILED
            return False
            
        # Validate content
        if not self.validate_content(message.message_type, message.content):
            logger.warning(f"Invalid content for message type {message.message_type}")
            message.status = MessageStatus.FAILED
            return False
            
        return True
    
    def validate_sender(self, sender_id: str, message_type: MessageType) -> bool:
        """
        Validate the sender for a specific message type.
        
        Args:
            sender_id: The ID of the sender
            message_type: The type of message being sent
            
        Returns:
            True if sender can send this message type, False otherwise
        """
        # Get sender type
        sender_type = self.agent_registry.get(sender_id)
        
        # If sender not registered, disallow
        if not sender_type:
            return False
            
        # Validate based on message type and sender type
        if message_type == MessageType.PURCHASE_REQUEST:
            return sender_type == AgentType.CUSTOMER
        elif message_type == MessageType.PURCHASE_CONFIRMATION:
            return sender_type == AgentType.BOOK
        elif message_type == MessageType.PAYMENT_PROCESS:
            return sender_type == AgentType.CUSTOMER
        elif message_type == MessageType.INVENTORY_UPDATE:
            return sender_type == AgentType.BOOK
        elif message_type == MessageType.RESTOCK_ALERT:
            return sender_type == AgentType.BOOK
        elif message_type == MessageType.RESTOCK_CONFIRMATION:
            return sender_type == AgentType.EMPLOYEE
        elif message_type == MessageType.STOCK_INQUIRY:
            return sender_type == AgentType.EMPLOYEE or sender_type == AgentType.CUSTOMER
        elif message_type == MessageType.SUPPLIER_NOTIFICATION:
            return sender_type == AgentType.EMPLOYEE
        elif message_type == MessageType.ASSISTANCE_REQUEST:
            return sender_type == AgentType.CUSTOMER
        elif message_type == MessageType.RECOMMENDATION_RESPONSE:
            return sender_type == AgentType.EMPLOYEE
        elif message_type == MessageType.GENRE_INQUIRY:
            return sender_type == AgentType.CUSTOMER
        elif message_type == MessageType.PRICE_UPDATE:
            return sender_type == AgentType.BOOK
            
        # Unknown message type
        return False
    
    def validate_content(self, message_type: MessageType, content: Dict[str, Any]) -> bool:
        """
        Validate the content of a message based on its type.
        
        Args:
            message_type: The type of message
            content: The message content to validate
            
        Returns:
            True if content is valid for this message type, False otherwise
        """
        # Each message type requires specific fields
        if message_type == MessageType.PURCHASE_REQUEST:
            required_fields = {'book_id', 'customer_budget'}
        elif message_type == MessageType.PURCHASE_CONFIRMATION:
            required_fields = {'book_id', 'price', 'available'}
        elif message_type == MessageType.PAYMENT_PROCESS:
            required_fields = {'book_id', 'amount'}
        elif message_type == MessageType.INVENTORY_UPDATE:
            required_fields = {'book_id', 'quantity_change'}
        elif message_type == MessageType.RESTOCK_ALERT:
            required_fields = {'book_id', 'current_stock', 'minimum_threshold'}
        elif message_type == MessageType.RESTOCK_CONFIRMATION:
            required_fields = {'book_id', 'restock_amount'}
        elif message_type == MessageType.STOCK_INQUIRY:
            required_fields = {'book_id'}
        elif message_type == MessageType.SUPPLIER_NOTIFICATION:
            required_fields = {'book_id', 'quantity', 'priority'}
        elif message_type == MessageType.ASSISTANCE_REQUEST:
            required_fields = {'request_type', 'details'}
        elif message_type == MessageType.RECOMMENDATION_RESPONSE:
            required_fields = {'book_recommendations'}
        elif message_type == MessageType.GENRE_INQUIRY:
            required_fields = {'genre'}
        elif message_type == MessageType.PRICE_UPDATE:
            required_fields = {'book_id', 'new_price', 'old_price'}
        else:
            # Unknown message type
            return False
            
        # Check that all required fields are present
        return all(field in content for field in required_fields)
        
    def process_messages(self, max_messages: int = 10) -> int:
        """
        Process a batch of messages from the queue.
        
        Args:
            max_messages: Maximum number of messages to process in this batch
            
        Returns:
            Number of messages processed
        """
        processed_count = 0
        
        for _ in range(max_messages):
            if self.message_queue.empty():
                break
                
            # Get next message
            message = self.message_queue.get()
            
            # Validate message
            if not self.validate_message(message):
                continue
                
            # Process message
            self._process_single_message(message)
            processed_count += 1
            
        return processed_count
        
    def _process_single_message(self, message: Message) -> bool:
        """
        Process a single message with intelligent targeted delivery.
        
        For targeted messages (specific receiver_id), delivers only to that agent.
        For broadcast messages, delivers to all subscribed agents.
        This ensures efficient routing and eliminates unnecessary processing.
        
        Args:
            message: The message to process
            
        Returns:
            True if message was processed successfully, False otherwise
        """
        # Update status to delivered
        message.status = MessageStatus.DELIVERED
        
        # Determine if this is a broadcast message
        is_broadcast = (message.receiver_id in ["BROADCAST", "", None] or 
                       message.message_type == MessageType.BROADCAST)
        
        handlers_called = 0
        
        if is_broadcast:
            # Broadcast: call all global handlers for this message type
            for handler in self.handlers.get(message.message_type, []):
                try:
                    handler(message)
                    handlers_called += 1
                except Exception as e:
                    logger.error(f"Error in broadcast handler: {e}")
                    message.status = MessageStatus.FAILED
                    return False
            
            if handlers_called > 0:
                logger.debug(f"Broadcast message {message.id} delivered to {handlers_called} handlers")
        else:
            # Targeted message: deliver only to specific receiver
            receiver_id = message.receiver_id
            
            # Check if receiver has a specific handler registered
            if (receiver_id in self.agent_handlers and 
                message.message_type in self.agent_handlers[receiver_id]):
                try:
                    handler = self.agent_handlers[receiver_id][message.message_type]
                    handler(message)
                    handlers_called += 1
                    logger.debug(f"Message {message.id} delivered to {receiver_id}")
                except Exception as e:
                    logger.error(f"Error in handler for {receiver_id}: {e}")
                    message.status = MessageStatus.FAILED
                    return False
            else:
                # Fallback to global handlers (backwards compatibility)
                # But the handler should check receiver_id internally
                for handler in self.handlers.get(message.message_type, []):
                    try:
                        handler(message)
                        handlers_called += 1
                    except Exception as e:
                        logger.error(f"Error in handler: {e}")
                        message.status = MessageStatus.FAILED
                        return False
        
        # Mark as processed if at least one handler was called
        if handlers_called > 0:
            message.status = MessageStatus.PROCESSED
        else:
            logger.warning(f"No handler found for message {message.id} to {message.receiver_id}")
            message.status = MessageStatus.FAILED
            return False
        
        # Check if this message is a response to another message
        if message.response_to and message.response_to in self.pending_responses:
            # Remove from pending responses
            original_msg_id = self.pending_responses.pop(message.response_to)
            logger.debug(f"Received response to message {original_msg_id}")
            
        return True
        
    def get_message_status(self, message_id: str) -> Optional[MessageStatus]:
        """
        Get the current status of a message.
        
        Args:
            message_id: The ID of the message to check
            
        Returns:
            The status of the message, or None if not found
        """
        if message_id not in self.message_history:
            return None
        return self.message_history[message_id].status
        
    def get_pending_messages(self, receiver_id: str = None) -> List[Message]:
        """
        Get all pending messages, optionally filtered by receiver.
        
        Args:
            receiver_id: Optional ID of receiver to filter messages
            
        Returns:
            List of pending messages
        """
        pending = []
        for msg_id, message in self.message_history.items():
            if message.status == MessageStatus.PENDING:
                if receiver_id is None or message.receiver_id == receiver_id:
                    pending.append(message)
        return pending
    
    # ========== Ontology Integration Methods ==========
    
    def integrate_with_ontology(self, onto_instance=None):
        """
        Integrate the message bus with the bookstore ontology.
        
        Args:
            onto_instance: An optional instance of the bookstore ontology
        """
        # If no ontology instance provided, use the imported module
        if onto_instance is None and bookstore_ontology is not None:
            try:
                # Create a new ontology if needed
                if not hasattr(bookstore_ontology, 'onto') or bookstore_ontology.onto is None:
                    bookstore_ontology.create_ontology()
                onto_instance = bookstore_ontology.onto
            except Exception as e:
                logger.error(f"Failed to create ontology: {e}")
                return
                
        if onto_instance is None:
            logger.warning("No ontology instance available for integration")
            return
            
        self.ontology = onto_instance
        logger.info("MessageBus integrated with bookstore ontology")
        
    def create_message_individuals(self, message: Message) -> bool:
        """
        Create ontology individuals for a message.
        
        Args:
            message: The message to represent in the ontology
            
        Returns:
            True if successfully created, False otherwise
        """
        if not hasattr(self, 'ontology') or self.ontology is None:
            logger.warning("Cannot create message individuals - no ontology")
            return False
            
        try:
            # Create a CommunicationEvent individual for the message
            message_name = f"Message_{message.id.replace('-', '_')}"
            
            with self.ontology:
                if hasattr(self.ontology, "CommunicationEvent"):
                    comm_event = self.ontology.CommunicationEvent(message_name)
                    comm_event.hasTimestamp = message.timestamp
                    comm_event.hasMessageType = str(message.message_type.value)
                    comm_event.hasStatus = str(message.status.value)
                    
                    # Try to link the sender and receiver
                    try:
                        # Find sender individual
                        sender_individual = None
                        if message.sender_id in self.agent_registry:
                            sender_type = self.agent_registry[message.sender_id]
                            if sender_type == AgentType.CUSTOMER:
                                sender_class = self.ontology.Customer
                            elif sender_type == AgentType.EMPLOYEE:
                                sender_class = self.ontology.Employee
                            elif sender_type == AgentType.BOOK:
                                sender_class = self.ontology.Book
                            else:
                                sender_class = None
                                
                            if sender_class:
                                # Try to find the individual
                                for individual in sender_class.instances():
                                    if hasattr(individual, "hasID") and individual.hasID == message.sender_id:
                                        sender_individual = individual
                                        break
                                        
                        # Find receiver individual
                        receiver_individual = None
                        if message.receiver_id in self.agent_registry:
                            receiver_type = self.agent_registry[message.receiver_id]
                            if receiver_type == AgentType.CUSTOMER:
                                receiver_class = self.ontology.Customer
                            elif receiver_type == AgentType.EMPLOYEE:
                                receiver_class = self.ontology.Employee
                            elif receiver_type == AgentType.BOOK:
                                receiver_class = self.ontology.Book
                            else:
                                receiver_class = None
                                
                            if receiver_class:
                                # Try to find the individual
                                for individual in receiver_class.instances():
                                    if hasattr(individual, "hasID") and individual.hasID == message.receiver_id:
                                        receiver_individual = individual
                                        break
                                        
                        # Link sender and receiver if found
                        if sender_individual:
                            comm_event.hasSender = sender_individual
                        if receiver_individual:
                            comm_event.hasReceiver = receiver_individual
                            
                    except Exception as e:
                        logger.warning(f"Error linking message to agents: {e}")
                        
                    return True
                else:
                    logger.warning("CommunicationEvent class not found in ontology")
                    
        except Exception as e:
            logger.error(f"Error creating message individual: {e}")
            
        return False
        
    def apply_rules_to_message(self, message: Message) -> bool:
        """
        Apply SWRL rules to a message.
        
        Args:
            message: The message to apply rules to
            
        Returns:
            True if rules were applied, False otherwise
        """
        if not hasattr(self, 'ontology') or self.ontology is None or bookstore_rules is None:
            return False
            
        try:
            # Create the message individual if it doesn't exist
            self.create_message_individuals(message)
            
            # Apply message-specific rules based on message type
            if message.message_type == MessageType.PURCHASE_REQUEST:
                if hasattr(bookstore_rules, "apply_purchase_request_rules"):
                    bookstore_rules.apply_purchase_request_rules(self.ontology, message.content)
                    return True
            elif message.message_type == MessageType.INVENTORY_UPDATE:
                if hasattr(bookstore_rules, "apply_inventory_rules"):
                    bookstore_rules.apply_inventory_rules(self.ontology, message.content)
                    return True
            elif message.message_type == MessageType.GENRE_INQUIRY:
                if hasattr(bookstore_rules, "apply_genre_inquiry_rules"):
                    bookstore_rules.apply_genre_inquiry_rules(self.ontology, message.content)
                    return True
                    
            # If no specific rule was applied, try applying general rules
            if hasattr(bookstore_rules, "apply_general_rules"):
                bookstore_rules.apply_general_rules(self.ontology)
                return True
                
        except Exception as e:
            logger.error(f"Error applying rules to message: {e}")
            
        return False
    
    def get_ontology_recommendations(self, customer_id: str, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get book recommendations from the ontology based on customer preferences.
        
        Args:
            customer_id: The ID of the customer
            genre: Optional genre to filter recommendations
            
        Returns:
            List of recommended books as dictionaries
        """
        if not hasattr(self, 'ontology') or self.ontology is None:
            return []
            
        recommendations = []
        
        try:
            # Find the customer individual
            customer_individual = None
            for individual in self.ontology.Customer.instances():
                if hasattr(individual, "hasID") and individual.hasID == customer_id:
                    customer_individual = individual
                    break
                    
            if not customer_individual:
                return []
                
            # Get customer preferences
            preferences = []
            if hasattr(customer_individual, "hasPreferredGenre"):
                preferences = list(customer_individual.hasPreferredGenre)
                
            # If genre is specified, only consider that genre
            if genre:
                preferences = [genre]
                
            # If no preferences and no genre specified, return empty list
            if not preferences:
                return []
                
            # Find books matching preferences
            for book_individual in self.ontology.Book.instances():
                book_genres = []
                if hasattr(book_individual, "hasGenre"):
                    book_genres = list(book_individual.hasGenre)
                    
                # Check if book matches any preference
                if any(pref in book_genres for pref in preferences):
                    book_info = {
                        "id": book_individual.hasID if hasattr(book_individual, "hasID") else str(book_individual),
                        "title": book_individual.hasTitle if hasattr(book_individual, "hasTitle") else "Unknown",
                        "author": book_individual.hasAuthor if hasattr(book_individual, "hasAuthor") else "Unknown",
                        "price": book_individual.hasPrice if hasattr(book_individual, "hasPrice") else 0.0,
                        "genre": book_genres
                    }
                    recommendations.append(book_info)
                    
            # Sort recommendations by price (lowest first)
            recommendations.sort(key=lambda x: x.get("price", float('inf')))
            
            return recommendations
                    
        except Exception as e:
            logger.error(f"Error getting ontology recommendations: {e}")
            
        return []
        return self.message_history[message_id].status
        
    def get_pending_messages(self, receiver_id: str = None) -> List[Message]:
        """
        Get all pending messages, optionally filtered by receiver.
        
        Args:
            receiver_id: Optional ID of receiver to filter messages
            
        Returns:
            List of pending messages
        """
        pending = []
        for msg_id, message in self.message_history.items():
            if message.status == MessageStatus.PENDING:
                if receiver_id is None or message.receiver_id == receiver_id:
                    pending.append(message)
        return pending