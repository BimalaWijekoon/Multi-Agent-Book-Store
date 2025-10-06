AGENT IMPLEMENTATION USAGE
=======================

File Structure:
- customer_agent.py (Customer behaviors)
- employee_agent.py (Employee workflows) 
- book_agent.py (Book state management)

Each agent implements behaviors that utilize the ontology properties,
SWRL rules, and message bus from previous phases.

INITIALIZATION
-------------
1. Import: 
   ```python
   from agents.customer_agent import CustomerAgent
   from agents.employee_agent import EmployeeAgent
   from agents.book_agent import BookAgent
   ```

2. Create: 
   ```python
   customer = CustomerAgent(unique_id, message_bus, ontology_individual)
   employee = EmployeeAgent(unique_id, message_bus, ontology_individual)
   book = BookAgent(unique_id, message_bus, ontology_individual)
   ```

3. Test individually:
   ```
   python -m agents.customer_agent
   python -m agents.employee_agent
   python -m agents.book_agent
   ```

AGENT INTEGRATION
----------------
- Each agent connects to its corresponding ontology individual
- Agent behaviors automatically trigger SWRL rules through ontology property updates
- All communication happens through the established message bus
- Property changes reflect in ontology in real-time

Integration with main.py:
1. Import agent classes at the top of main.py:
   ```python
   from agents import (
       CustomerAgent,
       EmployeeAgent,
       BookAgent
   )
   ```

2. Initialize agents in setup_environment():
   ```python
   customer_agent = CustomerAgent(
       unique_id="customer1",
       message_bus=message_bus,
       ontology_individual=None  # Or actual ontology individual
   )
   
   employee_agent = EmployeeAgent(
       unique_id="employee1",
       message_bus=message_bus,
       ontology_individual=None  # Or actual ontology individual
   )
   
   book_agent = BookAgent(
       unique_id="book1",
       message_bus=message_bus,
       ontology_individual=None  # Or actual ontology individual
   )
   ```

3. Return agents collection along with message_bus:
   ```python
   return True, message_bus, agents
   ```

4. Create a simulation function to run agent behaviors:
   ```python
   def run_simulation(agents, message_bus):
       # Access agents by their IDs
       customer = agents["customer1"]
       employee = agents["employee1"]
       book = agents["book1"]
       
       # Trigger agent behaviors
       customer.browse_books(sample_books)
       employee.monitor_inventory(inventory)
       book.process_purchase_request("customer1", 20.0)
       
       # Process messages after agent actions
       message_bus.process_messages()
   ```

CUSTOMER AGENT
-------------
Core Behaviors:
- Preference-Based Browsing: Navigate based on genre preferences
- Budget-Aware Purchasing: Make buying decisions within budget constraints
- Recommendation Processing: Evaluate book suggestions from employees
- Purchase History Tracking: Update ontology after transactions

Key Methods:
- browse_books(): Find books matching preferences and budget
- purchase_book(): Send purchase request for selected book
- process_recommendations(): Evaluate and act on book recommendations
- request_assistance(): Ask employees for help finding books

EMPLOYEE AGENT
-------------
Core Behaviors:
- Role-Based Task Management: Execute responsibilities based on role
- Inventory Monitoring: Track stock levels and trigger restocking
- Customer Assistance: Respond to inquiries with expertise-based recommendations
- Workflow Coordination: Collaborate with other employees

Key Methods:
- monitor_inventory(): Check stock levels and request restocking
- assist_customers(): Process customer assistance requests
- adjust_prices(): Modify book prices based on market data
- handle_genre_inquiry(): Provide recommendations for specific genres

BOOK AGENT
---------
Core Behaviors:
- Dynamic State Management: Maintain pricing, inventory, and availability
- Market-Responsive Pricing: Adjust prices based on demand patterns
- Transaction Processing: Handle purchase requests and update stock
- Recommendation Network: Suggest related books based on genre and similarity

Key Methods:
- process_purchase_request(): Handle customer purchase requests
- adjust_pricing(): Modify price based on demand and inventory
- update_inventory(): Change stock levels and trigger restocking
- get_recommendations(): Provide related book suggestions

SIMULATION INTEGRATION
--------------------
- Agents register automatically with the message bus
- Ontology relationships define interactions between agents
- Message processing occurs during simulation steps
- All state changes are persisted through the ontology

TESTING
-------
Each agent file includes a test_agent_behavior() function demonstrating core functionality:
- Customer browsing and purchasing behavior
- Employee inventory monitoring and customer assistance
- Book transaction processing and price adjustment

Run the tests to validate:
- Agent interactions with the ontology
- Message bus communication between agents
- SWRL rule triggering from agent behaviors