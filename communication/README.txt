MESSAGE BUS COMMUNICATION SYSTEM
===========================

This document explains how to use the Message Bus communication system 
for the Bookstore Management System.

OVERVIEW
--------
The message bus provides a sophisticated message-passing infrastructure for 
communication between Customer, Employee, and Book agents. It integrates with 
the ontology properties and SWRL rules from previous phases.

BASIC USAGE
----------
To use the message bus in your application:

1. Import the necessary components:
   ```python
   from communication import MessageBus, MessageType, AgentType, MessageStatus
   ```

2. Create a message bus instance:
   ```python
   message_bus = MessageBus()
   ```

3. Register agents that will communicate:
   ```python
   message_bus.register_agent("customer1", AgentType.CUSTOMER)
   message_bus.register_agent("employee1", AgentType.EMPLOYEE)
   message_bus.register_agent("book1", AgentType.BOOK)
   ```

4. Subscribe agents to message types they should receive:
   ```python
   message_bus.subscribe("book1", MessageType.PURCHASE_REQUEST)
   message_bus.subscribe("customer1", MessageType.PURCHASE_CONFIRMATION)
   ```

5. Send messages between agents:
   ```python
   message_id = message_bus.send_message(
       sender_id="customer1",
       receiver_id="book1", 
       message_type=MessageType.PURCHASE_REQUEST,
       content={"book_id": "123", "customer_budget": 50.0}
   )
   ```

6. Process messages in the queue:
   ```python
   processed_count = message_bus.process_messages()
   ```

MESSAGE HANDLERS
--------------
To handle specific message types:

1. Define handler functions:
   ```python
   def handle_purchase_request(message):
       # Process the purchase request
       print(f"Processing purchase for {message.content.get('book_id')}")
   ```

2. Register the handlers:
   ```python
   message_bus.register_handler(MessageType.PURCHASE_REQUEST, handle_purchase_request)
   ```

3. When you call process_messages(), all registered handlers will be automatically executed
   for their corresponding message types.

ONTOLOGY INTEGRATION
------------------
To integrate the message bus with the ontology:

1. Import the ontology:
   ```python
   from ontology import bookstore_ontology
   ```

2. Integrate with the message bus:
   ```python
   message_bus.integrate_with_ontology(bookstore_ontology.onto)
   ```

3. Use ontology-aware functions:
   ```python
   # Create ontology individuals for messages
   message_bus.create_message_individuals(message)
   
   # Apply rules to messages
   message_bus.apply_rules_to_message(message)
   
   # Get recommendations based on ontology
   recommendations = message_bus.get_ontology_recommendations(customer_id, genre="Mystery")
   ```

MESSAGE TYPES
-----------
The system supports these message types:

1. Purchase-related messages:
   - PURCHASE_REQUEST: From customer to book
   - PURCHASE_CONFIRMATION: From book to customer
   - PAYMENT_PROCESS: From customer to book
   - INVENTORY_UPDATE: From book to system

2. Inventory management messages:
   - RESTOCK_ALERT: From book to employee
   - RESTOCK_CONFIRMATION: From employee to book
   - STOCK_INQUIRY: From customer/employee to book
   - SUPPLIER_NOTIFICATION: From employee to system

3. Customer service messages:
   - ASSISTANCE_REQUEST: From customer to employee
   - RECOMMENDATION_RESPONSE: From employee to customer
   - GENRE_INQUIRY: From customer to book/employee
   - PRICE_UPDATE: From book to system

4. System messages:
   - BROADCAST: To multiple receivers
   - ERROR: Error notifications
   - ACKNOWLEDGEMENT: Receipt confirmations

ADVANCED FEATURES
---------------
1. Broadcasting messages:
   ```python
   message_ids = message_bus.broadcast_message(
       sender_id="system",
       message_type=MessageType.BROADCAST,
       content={"announcement": "Store closing soon"},
       target_agent_type=AgentType.CUSTOMER  # Optional: target specific agent types
   )
   ```

2. Message validation:
   - The system automatically validates message content for each message type
   - The sender's permission to send specific message types is checked
   - Message expiry is handled automatically

3. Message priorities:
   ```python
   message_id = message_bus.send_message(
       sender_id="customer1",
       receiver_id="employee1",
       message_type=MessageType.ASSISTANCE_REQUEST,
       content={"request_type": "help", "details": "Need assistance"},
       priority=1  # High priority (1-10 scale, 1 is highest)
   )
   ```

TROUBLESHOOTING
-------------
1. If a message is not being delivered, check:
   - The receiver is registered with the message bus
   - The receiver is subscribed to the message type
   - The message has not expired

2. If handlers are not executing, verify:
   - The handler is registered for the correct message type
   - Messages are being processed with process_messages()
   - Messages are valid (correct content format for type)