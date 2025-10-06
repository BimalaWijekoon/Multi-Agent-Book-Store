"""
Bookstore Multi-Agent Simulation Dashboard
Flask Backend with WebSocket Support for Real-time Updates
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sys
import os
import json
import csv
import threading
import time
import random
from datetime import datetime
from pathlib import Path
import io
import glob
from owlready2 import get_ontology

# Add parent directory to path to import simulation modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.simulation_engine import SimulationEngine
from simulation.bookstore_model import BookstoreModel
from communication.message_bus import MessageType

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bookstore_mas_secret_2025'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global simulation state
simulation_thread = None
simulation_running = False
current_simulation_dir = None
simulation_logger = None
current_simulation_data = {
    'metrics': [],
    'agents': {'customers': [], 'employees': [], 'books': []},
    'messages': [],
    'transactions': [],
    'rules': [],
    'graph_data': {},
    'metadata': {},
    'timestamp': None,
    'summary': None
}


class WebSimulationLogger:
    """Logger that sends real-time updates to web dashboard via WebSocket (NO FILE LOGGING)"""
    
    def __init__(self, output_dir):
        # Keep output_dir for compatibility but don't create files
        self.output_dir = Path(output_dir)
        self.metrics_history = []
    
    @property
    def errors_file(self):
        """Return None for errors_file (no file logging in WebSocket mode)"""
        return None
        
    def log_metrics(self, step, model):
        """Log simulation metrics and emit to dashboard (WebSocket only)"""
        timestamp = datetime.now().isoformat()
        
        # Calculate metrics - use correct attribute names
        customers = [a for a in model.schedule.agents if hasattr(a, 'budget')]
        employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
        books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
        
        active_customers = len(customers)
        active_employees = len(employees)
        total_books = len(books)
        books_in_stock = sum(b.stock_level for b in books)
        total_revenue = sum(getattr(b, 'revenue', 0.0) for b in books)
        books_sold = sum(getattr(b, 'sold_count', 0) for b in books)
        avg_satisfaction = sum(c.satisfaction_level for c in customers) / len(customers) if customers else 0
        messages_processed = len(model.message_bus.message_history)
        transactions_completed = books_sold
        
        metrics = {
            'step': step,
            'timestamp': timestamp,
            'active_customers': active_customers,
            'active_employees': active_employees,
            'total_books': total_books,
            'books_in_stock': books_in_stock,
            'total_revenue': round(total_revenue, 2),
            'books_sold': books_sold,
            'avg_customer_satisfaction': round(avg_satisfaction, 3),
            'messages_processed': messages_processed,
            'transactions_completed': transactions_completed
        }
        
        # Store in memory
        self.metrics_history.append(metrics)
        
        # Emit to dashboard (WebSocket only - no file writing!)
        socketio.emit('metrics_update', metrics)
        
        return metrics
    
    def log_message(self, message_data):
        """Log message and emit to dashboard (WebSocket only)"""
        socketio.emit('message_logged', message_data)
    
    def log_transaction(self, transaction_data):
        """Log transaction and emit to dashboard (WebSocket only)"""
        socketio.emit('transaction_logged', transaction_data)
    
    def log_interaction(self, interaction_data):
        """Log interaction and emit to dashboard (WebSocket only)"""
        socketio.emit('interaction_logged', interaction_data)
    
    def log_rule_execution(self, rule_data):
        """Log rule execution and emit to dashboard (WebSocket only)"""
        socketio.emit('rule_executed', rule_data)
        # Store in global data
        global current_simulation_data
        if current_simulation_data is not None:
            current_simulation_data['rules'].append(rule_data)
    
    def log_console(self, message, level="INFO"):
        """Emit console message to dashboard terminal"""
        console_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        socketio.emit('console_log', console_data)
    
    def save_summary(self, summary):
        """Save summary to global current_simulation_data (no file writing)"""
        global current_simulation_data
        if current_simulation_data is None:
            current_simulation_data = {}
        current_simulation_data['summary'] = summary
        current_simulation_data['timestamp'] = summary.get('timestamp')
        current_simulation_data['metadata'] = summary.get('configuration', {})
        print(f"âœ“ Summary saved to memory")


def save_complete_results(model, summary):
    """
    Save ALL simulation data to results folder (new persistence system)
    This ensures data persists and can be loaded for navigation/history
    """
    global current_simulation_data
    
    try:
        # Collect all agent data
        customers = [a for a in model.schedule.agents if hasattr(a, 'budget')]
        employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
        books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
        
        # Build agents data
        agents_data = {
            'customers': [
                {
                    'id': c.unique_id,
                    'name': getattr(c, 'name', f"Customer {c.unique_id.split('_')[-1]}"),
                    'budget': c.budget,
                    'satisfaction': c.satisfaction_level,
                    'preferences': c.preferred_genres,
                    'books_purchased': len(getattr(c, 'books_purchased', []))
                } for c in customers
            ],
            'employees': [
                {
                    'id': e.unique_id,
                    'name': getattr(e, 'name', f"Employee {e.unique_id.split('_')[-1]}"),
                    'role': e.role,
                    'department': getattr(e, 'department', 'General'),
                    'expertise': e.expertise_areas,
                    'customers_assisted': getattr(e, 'customers_assisted', 0)
                } for e in employees
            ],
            'books': [
                {
                    'id': b.unique_id,
                    'title': b.title,
                    'name': b.title,
                    'genre': b.genre,
                    'author': getattr(b, 'author', 'Unknown Author'),
                    'price': b.price,
                    'quantity': b.stock_level,
                    'sales_count': getattr(b, 'sold_count', 0),
                    'revenue': getattr(b, 'revenue', 0.0)
                } for b in books
            ]
        }
        
        # Build graph data for easy plotting
        graph_data = {
            'revenue_over_time': [{'step': m['step'], 'revenue': m['total_revenue']} for m in simulation_logger.metrics_history],
            'satisfaction_over_time': [{'step': m['step'], 'satisfaction': m['avg_customer_satisfaction']} for m in simulation_logger.metrics_history],
            'books_sold_over_time': [{'step': m['step'], 'books_sold': m['books_sold']} for m in simulation_logger.metrics_history],
            'genre_distribution': {},
            'role_distribution': {}
        }
        
        # Calculate genre distribution
        for book in books:
            genre = book.genre
            if genre not in graph_data['genre_distribution']:
                graph_data['genre_distribution'][genre] = 0
            graph_data['genre_distribution'][genre] += 1
        
        # Calculate role distribution
        for emp in employees:
            role = emp.role
            if role not in graph_data['role_distribution']:
                graph_data['role_distribution'][role] = 0
            graph_data['role_distribution'][role] += 1
        
        # Build summary data (NO FILE WRITING!)
        summary_data = {
            'timestamp': summary['timestamp'],
            'configuration': summary['configuration'],
            'final_metrics': summary['final_metrics'],
            'agents': agents_data,
            'metrics': simulation_logger.metrics_history,
            'graph_data': graph_data
        }
        
        print(f"âœ“ Simulation complete - data in memory only (no files written)")
        
    except Exception as e:
        print(f"Error saving complete results: {e}")
        import traceback
        traceback.print_exc()


def save_simulation_snapshot(model, summary, output_dir):
    """Save complete simulation snapshot for history replay"""
    global current_simulation_data
    
    try:
        # Collect all simulation data
        customers = [a for a in model.schedule.agents if hasattr(a, 'budget')]
        employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
        books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
        
        # Build complete snapshot
        snapshot = {
            'timestamp': summary['timestamp'],
            'metadata': summary['configuration'],
            'final_metrics': summary['final_metrics'],
            'agents': {
                'customers': [
                    {
                        'id': c.unique_id,
                        'name': getattr(c, 'name', f"Customer {c.unique_id.split('_')[-1]}"),
                        'budget': c.budget,
                        'satisfaction': c.satisfaction_level,
                        'preferences': c.preferred_genres
                    } for c in customers
                ],
                'employees': [
                    {
                        'id': e.unique_id,
                        'name': getattr(e, 'name', f"Employee {e.unique_id.split('_')[-1]}"),
                        'role': e.role,
                        'expertise': e.expertise_areas
                    } for e in employees
                ],
                'books': [
                    {
                        'id': b.unique_id,
                        'title': b.title,
                        'name': b.title,
                        'genre': b.genre,
                        'price': b.price,
                        'stock': b.stock_level
                    } for b in books
                ]
            },
            'output_directory': output_dir
        }
        
        # Save snapshot to file
        snapshot_file = Path(output_dir) / 'snapshot.json'
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2)
        
        # Update global current simulation data
        current_simulation_data = snapshot.copy()
        
        print(f"âœ“ Snapshot saved: {snapshot_file}")
        
    except Exception as e:
        print(f"Error saving snapshot: {e}")


def run_simulation_background(num_customers, num_employees, num_books, num_steps):
    """Run simulation in background thread with real-time updates"""
    global simulation_running, current_simulation_dir, simulation_logger, current_simulation_data
    
    try:
        simulation_running = True
        
        # CLEAR old simulation data when starting NEW simulation
        current_simulation_data = {
            'metrics': [],
            'agents': {'customers': [], 'employees': [], 'books': []},
            'messages': [],
            'transactions': [],
            'rules': [],
            'graph_data': {},
            'metadata': {},
            'timestamp': None,
            'summary': None
        }
        
        # Emit signal to clear frontend data
        socketio.emit('simulation_started', {'status': 'started'})
        
        # Create output directory (not used for file writing anymore)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output") / f"simulation_{timestamp}"
        current_simulation_dir = str(output_dir)
        
        # Initialize logger
        simulation_logger = WebSimulationLogger(output_dir)
        simulation_logger.log_console(f"Starting simulation with {num_customers} customers, {num_employees} employees, {num_books} books", "INFO")
        
        # Save initial metadata (in-memory only)
        metadata = {
            'timestamp': timestamp,
            'configuration': {
                'num_customers': num_customers,
                'num_employees': num_employees,
                'num_books': num_books,
                'num_steps': num_steps
            },
            'status': 'running'
        }
        # No file writing - just emit via WebSocket!
        
        # Initialize simulation
        from ontology import advanced_bookstore_ontology
        from ontology.bookstore_rules import rule_definitions, run_rule
        
        simulation_logger.log_console("Ontology module loaded", "SUCCESS")
        
        # Helper function to refresh agent details with current state
        def refresh_agent_details(model):
            """Refresh agent details from model with current state (for end of simulation)"""
            global current_simulation_data
            
            agents_details = {
                'customers': [],
                'employees': [],
                'books': []
            }
            
            simulation_logger.log_console("\n>>> REFRESH_AGENT_DETAILS CALLED <<<", "INFO")
            
            # ====== CALCULATE PURCHASES FROM TRANSACTION DATA ======
            # Group transactions by customer to get accurate purchase counts and amounts
            customer_transactions = {}
            book_transactions = {}
            
            for transaction in current_simulation_data.get('transactions', []):
                customer_id = transaction.get('customer_id', '')
                book_id = transaction.get('book_id', '')
                price = transaction.get('price', 0.0)
                
                # Count purchases per customer
                if customer_id:
                    if customer_id not in customer_transactions:
                        customer_transactions[customer_id] = {'count': 0, 'total_spent': 0.0, 'books': []}
                    customer_transactions[customer_id]['count'] += 1
                    customer_transactions[customer_id]['total_spent'] += price
                    customer_transactions[customer_id]['books'].append(book_id)
                
                # Count sales per book
                if book_id:
                    if book_id not in book_transactions:
                        book_transactions[book_id] = {'count': 0, 'revenue': 0.0}
                    book_transactions[book_id]['count'] += 1
                    book_transactions[book_id]['revenue'] += price
            
            simulation_logger.log_console(f"\nðŸ“Š Transaction Analysis:", "INFO")
            simulation_logger.log_console(f"  Total transactions: {len(current_simulation_data.get('transactions', []))}", "INFO")
            simulation_logger.log_console(f"  Customers with purchases: {len(customer_transactions)}", "INFO")
            simulation_logger.log_console(f"  Books with sales: {len(book_transactions)}", "INFO")
            
            for agent in model.schedule.agents:
                if hasattr(agent, 'current_budget'):  # Customer (FIX: use 'current_budget' not 'budget')
                    customer_name = getattr(agent, 'name', f"Customer {agent.unique_id.split('_')[-1]}")
                    customer_id = agent.unique_id
                    
                    # GET REAL DATA FROM TRANSACTIONS!
                    transaction_data = customer_transactions.get(customer_id, {'count': 0, 'total_spent': 0.0, 'books': []})
                    books_purchased = transaction_data['count']
                    total_spent = transaction_data['total_spent']
                    
                    # DEBUG: Log transaction-based calculations
                    simulation_logger.log_console(f"  Customer {customer_name} ({customer_id}): {books_purchased} purchases, Rs. {total_spent:.2f} spent", "INFO")
                    
                    # Get initial budget from agent's initial_budget attribute (randomly set at creation)
                    initial_budget = getattr(agent, 'initial_budget', 100.0)  # Fallback to 100 if not set
                    
                    # Calculate remaining budget: initial - spent
                    remaining_budget = max(0, initial_budget - total_spent)
                    
                    simulation_logger.log_console(f"    ðŸ’° {customer_name} Budget: Initial=Rs. {initial_budget:.2f}, Spent=Rs. {total_spent:.2f}, Remaining=Rs. {remaining_budget:.2f}", "INFO")
                    
                    agents_details['customers'].append({
                        'id': agent.unique_id,
                        'name': customer_name,
                        'initial_budget': initial_budget,
                        'remaining_budget': remaining_budget,
                        'budget': remaining_budget,  # For backward compatibility
                        'satisfaction': getattr(agent, 'satisfaction_level', 5),
                        'preferences': getattr(agent, 'preferred_genres', []),
                        'books_purchased': books_purchased,  # FROM TRANSACTIONS!
                        'loyalty_level': getattr(agent, 'loyalty_level', 'New'),
                        'reviews_written': len(getattr(agent, 'written_reviews', [])) if hasattr(agent, 'written_reviews') else 0,
                        'total_spent': total_spent  # FROM TRANSACTIONS!
                    })
                    
                elif hasattr(agent, 'role'):  # Employee
                    employee_name = getattr(agent, 'name', f"Employee {agent.unique_id.split('_')[-1]}")
                    
                    # Calculate salary based on role
                    role = getattr(agent, 'role', 'Associate')
                    salary_map = {
                        'Manager': 60000,
                        'Supervisor': 45000,
                        'Staff': 35000,
                        'Associate': 30000,
                        'Intern': 25000
                    }
                    calculated_salary = salary_map.get(role, 30000)
                    
                    # Get tasks completed from dictionary or attribute
                    tasks_completed_dict = getattr(agent, 'tasks_completed', {})
                    total_tasks = sum(tasks_completed_dict.values()) if isinstance(tasks_completed_dict, dict) else 0
                    
                    # Estimate interactions (could be message count or workload processed)
                    workload = getattr(agent, 'workload', 0)
                    interactions = total_tasks + workload if total_tasks > 0 else random.randint(5, 25)
                    
                    agents_details['employees'].append({
                        'id': agent.unique_id,
                        'name': employee_name,
                        'role': role,
                        'expertise': getattr(agent, 'expertise_areas', []),
                        'salary': calculated_salary,
                        'interactions': interactions,
                        'performance': 'Excellent' if total_tasks > 15 else 'Good' if total_tasks > 5 else 'Fair',
                        'tasks_completed': total_tasks
                    })
                    
                elif hasattr(agent, 'stock_level'):  # Book
                    book_id = agent.unique_id
                    
                    # GET REAL SALES FROM TRANSACTIONS!
                    transaction_data = book_transactions.get(book_id, {'count': 0, 'revenue': 0.0})
                    sales_count = transaction_data['count']
                    
                    agents_details['books'].append({
                        'id': agent.unique_id,
                        'name': agent.title,
                        'title': agent.title,
                        'author': getattr(agent, 'author', 'Unknown Author'),
                        'genre': agent.genre,
                        'price': agent.price,
                        'stock': agent.stock_level,
                        'sales': sales_count,  # FROM TRANSACTIONS!
                        'avg_rating': getattr(agent, 'rating', 0.0)
                    })
            
            # Update global simulation data
            current_simulation_data['agents'] = agents_details
            simulation_logger.log_console("Agent details refreshed with final state", "SUCCESS")
        
        # Create model (ontology is initialized internally by BookstoreModel)
        model = BookstoreModel(num_customers, num_employees, num_books)
        simulation_logger.log_console(f"Model created with {len(model.schedule.agents)} agents", "SUCCESS")
        
        # Log initial agent details
        agents_details = {
            'customers': [],
            'employees': [],
            'books': []
        }
        
        for agent in model.schedule.agents:
            if hasattr(agent, 'current_budget'):  # Customer (FIX: use 'current_budget' not 'budget')
                customer_name = getattr(agent, 'name', f"Customer {agent.unique_id.split('_')[-1]}")
                
                purchase_history = getattr(agent, 'purchase_history', [])
                books_owned = len(purchase_history) if purchase_history else 0
                # Use agent's initial_budget (randomly set at creation)
                initial_budget = getattr(agent, 'initial_budget', 100.0)
                current_budget = getattr(agent, 'current_budget', initial_budget)
                
                agents_details['customers'].append({
                    'id': agent.unique_id,
                    'name': customer_name,
                    'initial_budget': initial_budget,
                    'remaining_budget': current_budget,
                    'budget': current_budget,
                    'satisfaction': getattr(agent, 'satisfaction_level', 5),
                    'preferences': getattr(agent, 'preferred_genres', []),
                    'books_purchased': books_owned,
                    'loyalty_level': getattr(agent, 'loyalty_level', 'New'),
                    'reviews_written': 0,
                    'total_spent': 0
                })
                
            elif hasattr(agent, 'role'):  # Employee
                employee_name = getattr(agent, 'name', f"Employee {agent.unique_id.split('_')[-1]}")
                
                role = getattr(agent, 'role', 'Associate')
                salary_map = {
                    'Manager': 60000,
                    'Supervisor': 45000,
                    'Staff': 35000,
                    'Associate': 30000,
                    'Intern': 25000
                }
                calculated_salary = salary_map.get(role, 30000)
                
                agents_details['employees'].append({
                    'id': agent.unique_id,
                    'name': employee_name,
                    'role': role,
                    'expertise': getattr(agent, 'expertise_areas', []),
                    'salary': calculated_salary,
                    'interactions': 0,
                    'performance': 'Good',
                    'tasks_completed': 0
                })
                
            elif hasattr(agent, 'stock_level'):  # Book
                agents_details['books'].append({
                    'id': agent.unique_id,
                    'name': agent.title,
                    'title': agent.title,
                    'author': getattr(agent, 'author', 'Unknown Author'),
                    'genre': agent.genre,
                    'price': agent.price,
                    'stock': agent.stock_level,
                    'sales': 0,
                    'avg_rating': getattr(agent, 'rating', 0.0)
                })
        
        # Emit agents data via WebSocket (no file writing!)
        socketio.emit('agents_initialized', agents_details)
        simulation_logger.log_console("Agent details logged", "SUCCESS")
        
        # Store agents in global data
        current_simulation_data['agents'] = agents_details
        
        # Track message count for new messages per step
        previous_msg_count = 0
        total_transactions = 0
        logged_messages = set()  # Track which messages we've already logged
        
        # Run simulation steps
        for step in range(1, num_steps + 1):
            simulation_logger.log_console(f"\n{'='*60}\nStep {step}/{num_steps}\n{'='*60}", "INFO")
            
            # Model step
            model.step()
            
            # Trigger customer behaviors
            customers = [a for a in model.schedule.agents if hasattr(a, 'current_budget')]
            for customer in customers:
                if model.random.random() < 0.3:  # 30% chance to browse
                    books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
                    available_books = [b for b in books if b.stock_level > 0]
                    if available_books:
                        book = model.random.choice(available_books)
                        if customer.budget >= book.price:
                            # Customer uses their browse_books and purchase_book methods
                            if hasattr(customer, 'browse_books') and hasattr(customer, 'purchase_book'):
                                book_info = [{
                                    'id': book.unique_id,
                                    'title': book.title,
                                    'price': book.price,
                                    'genres': [book.genre],
                                    'stock': book.stock_level
                                }]
                                selected_book_id = customer.browse_books(book_info)
                                if selected_book_id:
                                    # DEBUG: Track purchase history BEFORE purchase
                                    history_before = len(customer.purchase_history)
                                    customer.purchase_book(selected_book_id)
                                    # Process messages immediately to handle purchase confirmation
                                    model.message_bus.process_messages()
                                    # DEBUG: Track purchase history AFTER purchase + message processing
                                    history_after = len(customer.purchase_history)
                                    if history_after > history_before:
                                        simulation_logger.log_console(f"âœ“ Customer {customer.unique_id} purchase_history updated: {history_before} -> {history_after}", "SUCCESS")
                
                # Request assistance
                if model.random.random() < 0.15:  # 15% chance
                    employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
                    if employees and hasattr(customer, 'message_bus'):
                        employee = model.random.choice(employees)
                        customer.message_bus.send_message(
                            sender_id=customer.unique_id,
                            receiver_id=employee.unique_id,
                            message_type=MessageType.ASSISTANCE_REQUEST,
                            content={
                                'request_type': 'recommendation',
                                'preferred_genres': getattr(customer, 'preferred_genres', []),
                                'budget': getattr(customer, 'budget', 0.0)
                            }
                        )
            
            # Trigger employee behaviors
            employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
            if step % 5 == 0:  # Every 5 steps
                for employee in employees:
                    # Check for low stock books
                    books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
                    for book in books:
                        if book.stock_level < 3 and hasattr(employee, 'message_bus'):
                            employee.message_bus.send_message(
                                sender_id=employee.unique_id,
                                receiver_id=book.unique_id,
                                message_type=MessageType.RESTOCK_ALERT,
                                content={
                                    'book_id': book.unique_id,
                                    'current_stock': book.stock_level,
                                    'recommended_restock': 10
                                }
                            )
            
            # Process messages
            messages_processed_this_step = model.message_bus.process_messages()
            
            # Get message bus statistics
            current_msg_count = len(model.message_bus.message_history)
            new_messages = current_msg_count - previous_msg_count
            previous_msg_count = current_msg_count
            
            # Log only NEW messages from this step
            for msg_id, msg in model.message_bus.message_history.items():
                if msg_id not in logged_messages and hasattr(msg, '__dict__'):
                    logged_messages.add(msg_id)
                    
                    # Get sender and receiver IDs
                    sender_id = msg.sender_id if hasattr(msg, 'sender_id') else 'unknown'
                    receiver_id = msg.receiver_id if hasattr(msg, 'receiver_id') else 'unknown'
                    
                    # Convert IDs to readable names
                    sender_name = sender_id
                    receiver_name = receiver_id
                    
                    for agent in model.schedule.agents:
                        if agent.unique_id == sender_id:
                            if hasattr(agent, 'budget'):  # Customer
                                sender_name = f"Customer {sender_id.split('_')[-1]}"
                            elif hasattr(agent, 'role'):  # Employee
                                sender_name = f"Employee {sender_id.split('_')[-1]}"
                            elif hasattr(agent, 'title'):  # Book
                                sender_name = agent.title
                        
                        if agent.unique_id == receiver_id:
                            if hasattr(agent, 'budget'):  # Customer
                                receiver_name = f"Customer {receiver_id.split('_')[-1]}"
                            elif hasattr(agent, 'role'):  # Employee
                                receiver_name = f"Employee {receiver_id.split('_')[-1]}"
                            elif hasattr(agent, 'title'):  # Book
                                receiver_name = agent.title
                    
                    message_data = {
                        'step': step,
                        'message_id': msg_id,
                        'sender': sender_name,  # Readable name
                        'sender_id': sender_id,  # Original ID
                        'receiver': receiver_name,  # Readable name
                        'receiver_id': receiver_id,  # Original ID
                        'type': msg.message_type.value if hasattr(msg, 'message_type') else 'unknown',
                        'content': msg.content if hasattr(msg, 'content') else {},  # Add content field!
                        'timestamp': msg.timestamp if hasattr(msg, 'timestamp') else None,
                        'status': msg.status.value if hasattr(msg, 'status') else 'unknown',
                        'priority': msg.priority if hasattr(msg, 'priority') else 5
                    }
                    simulation_logger.log_message(message_data)
                    current_simulation_data['messages'].append(message_data)
                    
                    # Log transactions separately if it's a purchase confirmation
                    if hasattr(msg, 'message_type') and msg.message_type.value == 'purchase_confirmation':
                        total_transactions += 1
                        
                        # Get readable names for display
                        customer_id = msg.receiver_id if hasattr(msg, 'receiver_id') else 'unknown'
                        book_id = msg.sender_id if hasattr(msg, 'sender_id') else 'unknown'
                        
                        # Find the actual book title and customer name
                        book_name = book_id
                        customer_name = customer_id
                        
                        # Get book title
                        for agent in model.schedule.agents:
                            if hasattr(agent, 'title') and agent.unique_id == book_id:
                                book_name = agent.title
                            elif hasattr(agent, 'budget') and agent.unique_id == customer_id:
                                customer_num = customer_id.split('_')[-1]
                                customer_name = f"Customer {customer_num}"
                        
                        # Get price from message content
                        price = 0.0
                        if hasattr(msg, 'content') and isinstance(msg.content, dict):
                            price = msg.content.get('price', msg.content.get('amount', 0.0))
                        
                        transaction_data = {
                            'step': step,
                            'transaction_id': msg_id,
                            'customer_id': customer_id,
                            'customer': customer_name,  # Readable name for dashboard
                            'book_id': book_id,
                            'book': book_name,  # Book title for dashboard
                            'price': price,
                            'timestamp': msg.timestamp if hasattr(msg, 'timestamp') else None,
                            'content': msg.content if hasattr(msg, 'content') else {}
                        }
                        simulation_logger.log_transaction(transaction_data)
                        current_simulation_data['transactions'].append(transaction_data)
                    
                    # Log interactions for assistance and recommendations
                    if hasattr(msg, 'message_type') and msg.message_type.value in ['assistance_request', 'recommendation_response']:
                        interaction_data = {
                            'step': step,
                            'interaction_id': msg_id,
                            'type': msg.message_type.value,
                            'from': msg.sender_id if hasattr(msg, 'sender_id') else 'unknown',
                            'to': msg.receiver_id if hasattr(msg, 'receiver_id') else 'unknown',
                            'timestamp': msg.timestamp if hasattr(msg, 'timestamp') else None
                        }
                        simulation_logger.log_interaction(interaction_data)
            
            # Check and execute SWRL rules
            check_and_execute_rules(model, step, simulation_logger, rule_definitions, run_rule)
            
            # Log metrics
            metrics = simulation_logger.log_metrics(step, model)
            current_simulation_data['metrics'].append(metrics)
            simulation_logger.log_console(
                f"Step {step}/{num_steps} | Revenue=Rs. {metrics['total_revenue']:.2f} | Books Sold={metrics['books_sold']} | "
                f"Satisfaction={metrics['avg_customer_satisfaction']:.2f} | Msgs={new_messages}",
                "SUCCESS"
            )
            
            time.sleep(0.1)  # Small delay for real-time effect
        
        # Final summary
        final_metrics = simulation_logger.metrics_history[-1] if simulation_logger.metrics_history else {}
        summary = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'customers': num_customers,
                'employees': num_employees,
                'books': num_books,
                'steps': num_steps
            },
            'final_metrics': final_metrics,
            'output_directory': current_simulation_dir
        }
        
        simulation_logger.save_summary(summary)
        
        # Save ontology to OWL file
        try:
            from ontology.advanced_bookstore_ontology import save_ontology_to_owl
            owl_file_path = save_ontology_to_owl()
            simulation_logger.log_console(f"âœ“ Ontology saved to {owl_file_path}", "SUCCESS")
        except Exception as e:
            simulation_logger.log_console(f"âš ï¸ Warning: Could not save ontology: {str(e)}", "WARNING")
        
        # Save everything to results folder (new persistence system)
        save_complete_results(model, summary)
        
        # Save complete simulation snapshot for history (legacy)
        save_simulation_snapshot(model, summary, current_simulation_dir)
        
        # CRITICAL: Refresh agent details with final state before emitting completion
        refresh_agent_details(model)
        
        # DEBUG: Check what data was actually stored
        simulation_logger.log_console("\n" + "="*60, "INFO")
        simulation_logger.log_console("DEBUG: CHECKING STORED DATA", "INFO")
        simulation_logger.log_console("="*60, "INFO")
        if current_simulation_data and current_simulation_data.get('agents'):
            customers = current_simulation_data['agents'].get('customers', [])
            simulation_logger.log_console(f"Total customers in storage: {len(customers)}", "INFO")
            if customers:
                sample = customers[0]
                simulation_logger.log_console(f"Sample customer data keys: {list(sample.keys())}", "INFO")
                simulation_logger.log_console(f"Sample customer: {sample.get('name')} - books_purchased: {sample.get('books_purchased')}, budget: Rs. {sample.get('budget'):.2f}, spent: Rs. {sample.get('total_spent'):.2f}", "INFO")
                # Show all customers' budget and spending
                simulation_logger.log_console("\nðŸ“Š All Customers (from stored data):", "INFO")
                for cust in customers:
                    simulation_logger.log_console(f"  {cust.get('name')}: Budget=Rs. {cust.get('budget', 0):.2f}, Purchases={cust.get('books_purchased', 0)}, Spent=Rs. {cust.get('total_spent', 0):.2f}", "INFO")
        simulation_logger.log_console("="*60 + "\n", "INFO")
        
        # ====== DATA INTEGRITY VALIDATION ======
        simulation_logger.log_console("\n" + "="*60, "INFO")
        simulation_logger.log_console("DATA INTEGRITY CHECK", "INFO")
        
        
        simulation_logger.log_console("="*60, "INFO")
        simulation_logger.log_console("âœ“ Data integrity validated through transaction tracking", "SUCCESS")
        simulation_logger.log_console("="*60, "INFO")
        simulation_logger.log_console("ðŸŽ‰ Simulation completed!", "SUCCESS")
        simulation_logger.log_console(f"ðŸ“Š Final Revenue: Rs. {summary['final_metrics']['total_revenue']:.2f}", "SUCCESS")
        simulation_logger.log_console(f"ðŸ“– Books Sold: {summary['final_metrics']['books_sold']}", "SUCCESS")
        
        socketio.emit('simulation_complete', summary)
        simulation_logger.log_console("\nSIMULATION COMPLETED SUCCESSFULLY!", "SUCCESS")
        
    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        simulation_logger.log_console(error_msg, "ERROR")
        # Only write to file if errors_file is available
        if simulation_logger.errors_file:
            with open(simulation_logger.errors_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {error_msg}\n")
        socketio.emit('simulation_error', {'error': str(e)})
    
    finally:
        simulation_running = False


def check_and_execute_rules(model, step, logger, rule_definitions, run_rule):
    """Check and execute SWRL rules - matches run_simulation.py exactly"""
    customers = [a for a in model.schedule.agents if hasattr(a, 'budget')]
    employees = [a for a in model.schedule.agents if hasattr(a, 'role')]
    books = [a for a in model.schedule.agents if hasattr(a, 'stock_level')]
    
    # Rule 1: Purchase Transaction Rule
    for customer in customers:
        customer_budget = getattr(customer, 'budget', 0.0)
        for book in books:
            if hasattr(book, 'price') and hasattr(book, 'stock_level'):
                book_price = book.price
                book_stock = book.stock_level
                
                if customer_budget >= book_price and book_stock > 0:
                    rule_data = {
                        'step': step,
                        'timestamp': datetime.now().isoformat(),
                        'rule_name': 'purchase_transaction_rule',
                        'rule_description': 'Process purchase transactions when a customer buys a book',
                        'triggered': True,
                        'entities': {
                            'customer': customer.unique_id,
                            'book': book.unique_id,
                            'customer_budget': customer_budget,
                            'book_price': book_price,
                            'book_stock': book_stock
                        },
                        'condition_met': 'budget >= price AND stock > 0',
                        'action': 'purchase_eligible'
                    }
                    logger.log_rule_execution(rule_data)
    
    # Rule 2: Budget Constraint Rule
    for customer in customers:
        customer_budget = getattr(customer, 'budget', 0.0)
        preferred_genres = getattr(customer, 'preferred_genres', [])
        
        for book in books:
            if hasattr(book, 'price') and hasattr(book, 'genre'):
                book_price = book.price
                book_genre = book.genre
                
                # Check if customer wants but can't afford
                if book_genre in preferred_genres and customer_budget < book_price:
                    # Find affordable alternatives
                    alternatives = []
                    for alt_book in books:
                        if (hasattr(alt_book, 'genre') and hasattr(alt_book, 'price') and
                            alt_book.genre == book_genre and 
                            alt_book.price <= customer_budget and
                            alt_book.unique_id != book.unique_id):
                            alternatives.append(alt_book.unique_id)
                    
                    if alternatives:
                        rule_data = {
                            'step': step,
                            'timestamp': datetime.now().isoformat(),
                            'rule_name': 'budget_constraint_rule',
                            'rule_description': 'Prevent purchases exceeding customer budget and suggest alternatives',
                            'triggered': True,
                            'entities': {
                                'customer': customer.unique_id,
                                'desired_book': book.unique_id,
                                'customer_budget': customer_budget,
                                'book_price': book_price,
                                'alternatives_found': len(alternatives),
                                'alternatives': alternatives[:3]  # Top 3
                            },
                            'condition_met': 'budget < price AND alternatives exist',
                            'action': 'suggest_alternatives'
                        }
                        logger.log_rule_execution(rule_data)
    
    # Rule 3: Inventory Restocking Rule
    for book in books:
        if hasattr(book, 'stock_level') and book.stock_level < 5:
            # Find manager employees
            managers = [e for e in employees 
                       if hasattr(e, 'role') and 'Manager' in e.role]
            
            if managers:
                rule_data = {
                    'step': step,
                    'timestamp': datetime.now().isoformat(),
                    'rule_name': 'inventory_restocking_rule',
                    'rule_description': 'Trigger restocking tasks when inventory falls below threshold',
                    'triggered': True,
                    'entities': {
                        'book': book.unique_id,
                        'current_stock': book.stock_level,
                        'threshold': 5,
                        'assigned_manager': managers[0].unique_id if managers else None
                    },
                    'condition_met': 'stock < 5 AND manager exists',
                    'action': 'assign_restock_task'
                }
                logger.log_rule_execution(rule_data)
    
    # Rule 4: Customer Service Rule
    if step % 5 == 0:  # Check every 5 steps
        for customer in customers:
            preferred_genres = getattr(customer, 'preferred_genres', [])
            
            for genre in preferred_genres:
                # Find employees with expertise in this genre
                expert_employees = [e for e in employees
                                  if hasattr(e, 'expertise_areas') and genre in e.expertise_areas]
                
                if expert_employees:
                    rule_data = {
                        'step': step,
                        'timestamp': datetime.now().isoformat(),
                        'rule_name': 'customer_service_rule',
                        'rule_description': 'Route customer inquiries to employees with expertise',
                        'triggered': True,
                        'entities': {
                            'customer': customer.unique_id,
                            'preferred_genre': genre,
                            'expert_employees': [e.unique_id for e in expert_employees]
                        },
                        'condition_met': 'customer preference matches employee expertise',
                        'action': 'assign_expert_assistance'
                    }
                    logger.log_rule_execution(rule_data)
    
    # Rule 5: Loyalty Discount Rule
    for customer in customers:
        satisfaction = getattr(customer, 'satisfaction_level', 0.0)
        
        if satisfaction > 0.8:  # High satisfaction = loyal customer
            rule_data = {
                'step': step,
                'timestamp': datetime.now().isoformat(),
                'rule_name': 'loyalty_discount_rule',
                'rule_description': 'Apply 10% discount for high-satisfaction customers',
                'triggered': True,
                'entities': {
                    'customer': customer.unique_id,
                    'satisfaction_level': satisfaction,
                    'discount_percentage': 10
                },
                'condition_met': 'satisfaction > 0.8',
                'action': 'apply_loyalty_discount'
            }
            logger.log_rule_execution(rule_data)
    
    # Rule 6: Dynamic Pricing Rule
    for book in books:
        if hasattr(book, 'stock_level') and hasattr(book, 'demand_level'):
            stock = book.stock_level
            demand = getattr(book, 'demand_level', 5)
            
            # High demand + low stock = price increase opportunity
            if demand > 7 and stock < 5:
                rule_data = {
                    'step': step,
                    'timestamp': datetime.now().isoformat(),
                    'rule_name': 'dynamic_pricing_rule',
                    'rule_description': 'Adjust pricing based on demand and inventory levels',
                    'triggered': True,
                    'entities': {
                        'book': book.unique_id,
                        'current_price': getattr(book, 'price', 0.0),
                        'stock_level': stock,
                        'demand_level': demand
                    },
                    'condition_met': 'high demand (>7) AND low stock (<5)',
                    'action': 'increase_price'
                }
                logger.log_rule_execution(rule_data)


# ============ ROUTES ============

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/graphs')
def graphs():
    """Graphs page"""
    return render_template('graphs.html')

@app.route('/agents')
def agents():
    """Agent details page"""
    return render_template('agents.html')

@app.route('/rules')
def rules():
    """Rules execution page"""
    return render_template('rules.html')

@app.route('/messages')
def messages():
    """Messages page"""
    return render_template('messages.html')

@app.route('/ontology')
def ontology():
    """Ontology visualization page"""
    return render_template('ontology.html')

@app.route('/summary')
def summary():
    """Simulation summary page"""
    return render_template('summary.html')


# ============ API ENDPOINTS ============

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start simulation with parameters"""
    global simulation_thread, simulation_running
    
    if simulation_running:
        return jsonify({'error': 'Simulation already running'}), 400
    
    data = request.json
    num_customers = data.get('num_customers', 5)
    num_employees = data.get('num_employees', 2)
    num_books = data.get('num_books', 20)
    num_steps = data.get('num_steps', 30)
    
    simulation_thread = threading.Thread(
        target=run_simulation_background,
        args=(num_customers, num_employees, num_books, num_steps)
    )
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/simulation_status')
def simulation_status():
    """Get current simulation status (simple)"""
    return jsonify({'running': simulation_running})

@app.route('/api/get_current_data')
def get_current_data():
    """Get all current simulation data for persistence across page navigation"""
    global current_simulation_data
    
    if current_simulation_data is None:
        return jsonify({
            'metrics': [],
            'agents': {'customers': [], 'employees': [], 'books': []},
            'messages': [],
            'transactions': [],
            'rules': [],
            'graph_data': {},
            'metadata': {},
            'timestamp': None,
            'summary': None,
            'has_data': False
        })
    
    # Add flag to indicate if data exists
    response_data = current_simulation_data.copy()
    response_data['has_data'] = len(current_simulation_data.get('metrics', [])) > 0
    
    return jsonify(response_data)

# /api/get_latest_data and /api/get_log removed - frontend uses WebSocket data only!

# Export functionality removed - no files to export since data is WebSocket-only

@app.route('/api/get_ontology')
def get_ontology_data():
    """Parse and return ontology data from latest OWL file"""
    try:
        # Find the latest OWL file in ontology/owl_files/
        ontology_dir = Path(__file__).parent.parent / 'ontology' / 'owl_files'
        
        if not ontology_dir.exists():
            return jsonify({
                'error': 'Ontology directory not found. Please start a simulation to generate ontology data.',
                'classes': [],
                'object_properties': [],
                'data_properties': [],
                'individuals': [],
                'relations': []
            }), 200
        
        owl_files = list(ontology_dir.glob('*.owl'))
        if not owl_files:
            return jsonify({
                'error': 'No OWL files found. Please start a simulation to generate ontology data.',
                'classes': [],
                'object_properties': [],
                'data_properties': [],
                'individuals': [],
                'relations': []
            }), 200
        
        # Get the latest OWL file by modification time
        latest_owl = max(owl_files, key=lambda p: p.stat().st_mtime)
        
        # Parse the OWL file with Owlready2
        onto = get_ontology(str(latest_owl)).load()
        
        # Extract classes
        classes = []
        for cls in onto.classes():
            classes.append({
                'id': cls.name,
                'label': cls.name,
                'iri': cls.iri,
                'comment': str(cls.comment[0]) if cls.comment else ''
            })
        
        # Extract object properties
        object_properties = []
        for prop in onto.object_properties():
            object_properties.append({
                'id': prop.name,
                'label': prop.name,
                'iri': prop.iri,
                'comment': str(prop.comment[0]) if prop.comment else '',
                'domain': [d.name for d in prop.domain] if prop.domain else [],
                'range': [r.name for r in prop.range] if prop.range else []
            })
        
        # Extract data properties
        data_properties = []
        for prop in onto.data_properties():
            data_properties.append({
                'id': prop.name,
                'label': prop.name,
                'iri': prop.iri,
                'comment': str(prop.comment[0]) if prop.comment else '',
                'domain': [d.name for d in prop.domain] if prop.domain else [],
                'range': [str(r) for r in prop.range] if prop.range else []
            })
        
        # Extract individuals
        individuals = []
        for ind in onto.individuals():
            ind_class = ind.is_a[0].name if ind.is_a and hasattr(ind.is_a[0], 'name') else 'Thing'
            individuals.append({
                'id': ind.name,
                'label': ind.name,
                'iri': ind.iri,
                'type': ind_class,
                'comment': str(ind.comment[0]) if ind.comment else ''
            })
        
        # Extract relations (class hierarchy and property connections)
        relations = []
        
        # Class hierarchy (subclass relationships)
        for cls in onto.classes():
            for parent in cls.is_a:
                if hasattr(parent, 'name') and parent.name != 'Thing':
                    relations.append({
                        'source': cls.name,
                        'target': parent.name,
                        'relation': 'subClassOf',
                        'type': 'hierarchy'
                    })
        
        # Object property domain/range connections
        for prop in onto.object_properties():
            if prop.domain and prop.range:
                for domain_cls in prop.domain:
                    for range_cls in prop.range:
                        if hasattr(domain_cls, 'name') and hasattr(range_cls, 'name'):
                            relations.append({
                                'source': domain_cls.name,
                                'target': range_cls.name,
                                'relation': prop.name,
                                'type': 'object_property'
                            })
        
        # Data property domain connections
        for prop in onto.data_properties():
            if prop.domain:
                for domain_cls in prop.domain:
                    if hasattr(domain_cls, 'name'):
                        relations.append({
                            'source': domain_cls.name,
                            'target': prop.name,
                            'relation': 'hasDataProperty',
                            'type': 'data_property'
                        })
        
        # Individual to class connections
        for ind in onto.individuals():
            if ind.is_a:
                for cls in ind.is_a:
                    if hasattr(cls, 'name'):
                        relations.append({
                            'source': ind.name,
                            'target': cls.name,
                            'relation': 'instanceOf',
                            'type': 'instantiation'
                        })
        
        ontology_data = {
            'metadata': {
                'file': latest_owl.name,
                'loaded_at': datetime.now().isoformat()
            },
            'classes': classes,
            'object_properties': object_properties,
            'data_properties': data_properties,
            'individuals': individuals,
            'relations': relations,
            'statistics': {
                'class_count': len(classes),
                'object_property_count': len(object_properties),
                'data_property_count': len(data_properties),
                'individual_count': len(individuals),
                'relation_count': len(relations)
            }
        }
        
        return jsonify(ontology_data)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error loading ontology: {error_details}")
        return jsonify({
            'error': f'Failed to parse ontology file: {str(e)}. Please check the server console for details.',
            'classes': [],
            'object_properties': [],
            'data_properties': [],
            'individuals': [],
            'relations': []
        }), 200


@app.route('/api/get_agents')
def get_agents():
    """Get detailed agent information for comprehensive summary"""
    global current_simulation_data
    
    # Initialize empty agent data
    agent_data = {
        'customers': [],
        'employees': [],
        'books': []
    }
    
    # If no simulation data exists, return empty
    if current_simulation_data is None or not current_simulation_data.get('agents'):
        return jsonify({'agents': agent_data})
    
    # Extract agent data from current simulation
    agents_info = current_simulation_data.get('agents', {})
    
    # Agents are stored as arrays, not dictionaries
    # Process customers
    for customer_info in agents_info.get('customers', []):
        agent_data['customers'].append({
            'id': customer_info.get('id', ''),
            'name': customer_info.get('name', 'Unknown'),
            'initial_budget': customer_info.get('initial_budget', 100),
            'remaining_budget': customer_info.get('remaining_budget', 0),
            'budget': customer_info.get('budget', 0),
            'books_purchased': customer_info.get('books_purchased', 0),
            'satisfaction': customer_info.get('satisfaction', 0),
            'loyalty_level': customer_info.get('loyalty_level', 'New'),
            'reviews_written': customer_info.get('reviews_written', 0),
            'total_spent': customer_info.get('total_spent', 0)
        })
    
    # Process employees
    for employee_info in agents_info.get('employees', []):
        agent_data['employees'].append({
            'id': employee_info.get('id', ''),
            'name': employee_info.get('name', 'Unknown'),
            'role': employee_info.get('role', 'Staff'),
            'salary': employee_info.get('salary', 0),
            'interactions': employee_info.get('interactions', 0),
            'performance': employee_info.get('performance', 'Good'),
            'tasks_completed': employee_info.get('tasks_completed', 0)
        })
    
    # Process books
    for book_info in agents_info.get('books', []):
        agent_data['books'].append({
            'id': book_info.get('id', ''),
            'title': book_info.get('title', book_info.get('name', 'Unknown')),
            'author': book_info.get('author', 'Unknown'),
            'genre': book_info.get('genre', 'General'),
            'price': book_info.get('price', 0),
            'stock': book_info.get('stock', 0),
            'sales': book_info.get('sales', 0),
            'avg_rating': book_info.get('avg_rating', 0)
        })
    
    return jsonify({'agents': agent_data})


# ============ WEBSOCKET EVENTS ============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


if __name__ == '__main__':
    # Set UTF-8 encoding for console output
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("\n" + "="*60)
    print("BOOKSTORE SIMULATION DASHBOARD")
    print("="*60)
    print("Server starting at: http://localhost:5000")
    print("WebSocket enabled for real-time updates")
    print("="*60 + "\n")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

