"""
Bookstore Model Implementation using Mesa Framework.

This module integrates the Mesa simulation framework with our bookstore agents,
ontology system, and message bus for a comprehensive multi-agent simulation.
"""

import mesa
import logging
import random
from typing import Dict, List, Any, Optional, Tuple

from agents import CustomerAgent, EmployeeAgent, BookAgent
from agents.agent_names import generate_customer_name, generate_employee_name
from communication import MessageBus, MessageType, AgentType
from ontology import bookstore_ontology, validate_ontology

logger = logging.getLogger(__name__)

class BookstoreModel(mesa.Model):
    """
    Mesa model implementation for the Bookstore Management System simulation.
    
    This model orchestrates all three agent types, controls the simulation flow,
    and manages the integration with the ontology and message bus systems.
    """
    
    def __init__(self, 
                 num_customers: int = 10, 
                 num_employees: int = 3,
                 num_books: int = 50,
                 width: int = 20, 
                 height: int = 20):
        """
        Initialize the bookstore model with agents and environment.
        
        Args:
            num_customers: Number of customer agents to create
            num_employees: Number of employee agents to create
            num_books: Number of book agents to create
            width: Width of the 2D grid space
            height: Height of the 2D grid space
        """
        super().__init__()
        
        # Initialize basic model properties
        self.num_customers = num_customers
        self.num_employees = num_employees
        self.num_books = num_books
        self.running = True
        self.step_count = 0
        
        # Set up grid and scheduler
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        
        # Set up the ontology system
        logger.info("Validating the bookstore ontology...")
        self.ontology_valid = validate_ontology()
        if not self.ontology_valid:
            logger.error("Ontology validation failed! Simulation cannot continue.")
            self.running = False
            return
        
        logger.info("Ontology validation successful!")
        self.onto = bookstore_ontology.onto
        
        # Initialize the message bus
        logger.info("Initializing message bus for simulation...")
        self.message_bus = MessageBus()
        self.message_bus.integrate_with_ontology(self.onto)
        
        # Create agent collections
        self.customer_agents = []
        self.employee_agents = []
        self.book_agents = []
        
        # Initialize data collectors for simulation metrics
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Total Revenue": lambda m: m.get_total_revenue(),
                "Active Customers": lambda m: m.count_active_customers(),
                "Books Sold": lambda m: m.get_books_sold(),
                "Average Customer Satisfaction": lambda m: m.get_avg_customer_satisfaction()
            },
            agent_reporters={
                "Position": lambda a: a.pos if hasattr(a, "pos") else None,
                "Type": lambda a: a.agent_type if hasattr(a, "agent_type") else "Unknown"
            }
        )
        
        # Create agents
        self._create_agents()
        
        # Add datacollector's agent reporters
        self.datacollector.collect(self)
        
    def _create_agents(self):
        """Create and initialize all agents for the simulation."""
        self._create_book_agents()
        self._create_employee_agents()
        self._create_customer_agents()
    
    def _create_book_agents(self):
        """Create book agents with random properties."""
        logger.info(f"Creating {self.num_books} book agents...")
        
        # Sri Lankan book titles and authors
        book_titles = [
            "Gamperaliya", "Viragaya", "Kaliyugaya", "Madol Duwa",
            "Aithihyamala", "The Seven Moons of Maali Almeida", "Funny Boy", "Cinnamon Gardens",
            "Running in the Family", "The Village in the Jungle", "Chinaman", "The Story of Sigiri",
            "The Legend of the Sword", "Yakada Yaka", "Selalihini Sandeshaya", "Alagiyawanna Mukaveti",
            "Sandeshaya Kavya", "Meghaduta", "Guttila Kavya", "Kavsilumina",
            "Yashodhara Kavya", "Asadisa Dhammapadaya", "Muvadevdavata", "Kusa Jataka Kavya",
            "Salalihinisekaraya", "Sinhala Bodhi Vamsa", "Butsarana", "Amavatura",
            "Thun Man Handiya", "Magul Kema", "Hathpana", "Deveni Aththo",
            "Berava", "Yuganthaya", "Amba Yahaluwo", "Ran Kirilli",
            "Durakathanaya", "Malagiya Aththo", "Kurulu Hadawatha", "Viharamahadevi",
            "Hansa Maliga", "Dharmapradeepaya", "Sevarathna", "Sanda Kinduru",
            "Dhawala Bheeshana", "Malpaluwa", "Sarungal", "Island of a Thousand Mirrors"
        ]
        
        authors = [
            "Martin Wickramasinghe", "W.A. Silva", "Martin Wickramasinghe", "G.B. Senanayake",
            "M. Aithihyamala", "Shehan Karunatilaka", "Shyam Selvadurai", "Shyam Selvadurai",
            "Michael Ondaatje", "Leonard Woolf", "Shehan Karunatilaka", "Sybil Wettasinghe",
            "Aloy Perera", "Victor Ratnayake", "Thotagamuwe Sri Rahula Thera", "Alagiyawanna Mukaveti",
            "Various Buddhist Scholars", "Kalidasa", "Vidagama Maitreya Thera", "Various Monks",
            "Various Buddhist Authors", "Various Scholars", "Gurulugomi", "Various Monks",
            "Wickramabahu III", "Various Buddhist Monks", "Various Authors", "Gurulugomi",
            "Mahagamasekera", "Ediriweera Sarachchandra", "Kumaratunga Munidasa", "Mahagamasekera",
            "Siri Gunasinghe", "Ediriweera Sarachchandra", "W.A. Silva", "Simon Nawagattegama",
            "Simon Nawagattegama", "Mahagamasekera", "Mahagamasekera", "K. Jayatillake",
            "Mahagamasekera", "Mahagama Sekara", "K. Jayatillake", "Various Authors",
            "Sybil Wettasinghe", "Martin Wickramasinghe", "K. Jayatillake", "Nayomi Munaweera"
        ]
        
        # Book properties for simulation
        genres = ["Fiction", "Mystery", "Science Fiction", "Fantasy", 
                  "Biography", "History", "Business", "Romance", "Horror"]
        
        publishers = ["Penguin", "HarperCollins", "Random House", "Simon & Schuster",
                     "Oxford Press", "Macmillan", "Scholastic"]
        
        # Create book agents
        for i in range(self.num_books):
            book_id = f"book_{i}"
            
            # Create agent
            book_agent = BookAgent(
                unique_id=book_id,
                model=self,  # Pass the model to the agent
                message_bus=self.message_bus,
                ontology_individual=None  # We'll use simulated data for now
            )
            
            # Set book properties with real titles and authors
            book_agent.title = book_titles[i % len(book_titles)]
            book_agent.author = authors[i % len(authors)]
            book_agent.genre = random.choice(genres)  # Random genre from list
            book_agent.genres = [book_agent.genre]  # Store as list too
            book_agent.publisher = random.choice(publishers)
            
            # Set additional random properties (in Sri Lankan Rupees)
            book_agent.price = round(random.uniform(300.0, 5000.0), 2)
            book_agent.current_price = book_agent.price
            book_agent.stock_level = random.randint(1, 20)
            book_agent.rating = round(random.uniform(3.0, 5.0), 1)
            
            # Add to model and scheduler
            self.schedule.add(book_agent)
            self.book_agents.append(book_agent)
            
            # Add to grid at a random position
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(book_agent, (x, y))
            
            # Register with message bus
            self.message_bus.register_agent(book_id, AgentType.BOOK)
            self.message_bus.subscribe(book_id, [MessageType.PURCHASE_REQUEST, 
                                              MessageType.STOCK_INQUIRY,
                                              MessageType.PAYMENT_PROCESS])
        
        logger.info(f"Created {len(self.book_agents)} book agents successfully.")
    
    def _create_employee_agents(self):
        """Create employee agents with different roles."""
        logger.info(f"Creating {self.num_employees} employee agents...")
        
        roles = ["Associate", "Manager", "Specialist"]
        expertise_areas = ["Fiction", "Non-Fiction", "Children", "Academic",
                         "Rare Books", "Customer Service"]
        
        # Create employee agents
        for i in range(self.num_employees):
            employee_id = f"employee_{i}"
            
            # Generate realistic employee name
            employee_name = generate_employee_name(include_title=True)
            
            # Create agent with name
            employee_agent = EmployeeAgent(
                unique_id=employee_id,
                model=self,  # Pass the model to the agent
                message_bus=self.message_bus,
                ontology_individual=None,  # We'll use simulated data for now
                name=employee_name  # Pass the generated name
            )
            
            # Assign role: first employee is always Manager, others are random
            if i == 0:
                employee_agent.role = "Manager"
            else:
                employee_agent.role = random.choice(["Associate", "Specialist"])
            
            # Set additional properties
            employee_agent.expertise = random.sample(expertise_areas, 
                                                  k=random.randint(1, 3))
            employee_agent.expertise_areas = employee_agent.expertise  # Ensure both properties set
            employee_agent.years_experience = random.randint(1, 15)
            
            # Add to model and scheduler
            self.schedule.add(employee_agent)
            self.employee_agents.append(employee_agent)
            
            # Add to grid at a random position
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(employee_agent, (x, y))
            
            # Register with message bus
            self.message_bus.register_agent(employee_id, AgentType.EMPLOYEE)
            self.message_bus.subscribe(employee_id, [MessageType.ASSISTANCE_REQUEST,
                                                  MessageType.INVENTORY_UPDATE,
                                                  MessageType.RESTOCK_ALERT])
        
        logger.info(f"Created {len(self.employee_agents)} employee agents successfully.")
    
    def _create_customer_agents(self):
        """Create customer agents with varying preferences."""
        logger.info(f"Creating {self.num_customers} customer agents...")
        
        genres = ["Fiction", "Mystery", "Science Fiction", "Fantasy", 
                  "Biography", "History", "Business", "Romance", "Horror"]
        
        # Create customer agents
        for i in range(self.num_customers):
            customer_id = f"customer_{i}"
            
            # Generate realistic customer name
            customer_name = generate_customer_name()
            
            # Create agent with name
            customer_agent = CustomerAgent(
                unique_id=customer_id,
                model=self,  # Pass the model to the agent
                message_bus=self.message_bus,
                ontology_individual=None,  # We'll use simulated data for now
                name=customer_name  # Pass the generated name
            )
            
            # Set additional properties
            customer_agent.budget = round(random.uniform(20.0, 200.0), 2)
            
            # Assign 1-3 preferred genres
            preferred_genres_count = random.randint(1, 3)
            customer_agent.preferred_genres = random.sample(genres, k=preferred_genres_count)
            
            # Assign satisfaction level
            customer_agent.satisfaction_level = random.uniform(0.5, 1.0)
            
            # Set active status
            customer_agent.is_active = True
            
            # Add to model and scheduler
            self.schedule.add(customer_agent)
            self.customer_agents.append(customer_agent)
            
            # Add to grid at a random position
            x = random.randrange(self.grid.width)
            y = random.randrange(self.grid.height)
            self.grid.place_agent(customer_agent, (x, y))
            
            # Register with message bus
            self.message_bus.register_agent(customer_id, AgentType.CUSTOMER)
            self.message_bus.subscribe(customer_id, [MessageType.PURCHASE_CONFIRMATION,
                                                  MessageType.RECOMMENDATION_RESPONSE,
                                                  MessageType.ACKNOWLEDGEMENT])
        
        logger.info(f"Created {len(self.customer_agents)} customer agents successfully.")
    
    def step(self):
        """Execute one step of the simulation."""
        logger.info(f"Executing step {self.step_count} of the simulation...")
        
        # Let all agents take their step
        self.schedule.step()
        
        # Process messages in the message bus
        messages_processed = self.message_bus.process_messages()
        logger.info(f"Processed {messages_processed} messages this step")
        
        # Collect data
        self.datacollector.collect(self)
        
        # Update step count
        self.step_count += 1
        
        logger.info(f"Step {self.step_count} completed.")
    
    def get_total_revenue(self) -> float:
        """Calculate total revenue from all book sales."""
        total = 0.0
        for book in self.book_agents:
            if hasattr(book, 'revenue'):
                total += book.revenue
        return round(total, 2)
    
    def count_active_customers(self) -> int:
        """Count customers currently active in the store."""
        return sum(1 for c in self.customer_agents if c.is_active)
    
    def get_books_sold(self) -> int:
        """Get total number of books sold."""
        total = 0
        for book in self.book_agents:
            if hasattr(book, 'sold_count'):
                total += book.sold_count
        return total
    
    def get_avg_customer_satisfaction(self) -> float:
        """Calculate average customer satisfaction."""
        if not self.customer_agents:
            return 0.0
        
        total = sum(c.satisfaction_level for c in self.customer_agents 
                   if hasattr(c, 'satisfaction_level'))
        return round(total / len(self.customer_agents), 2)
    
    def get_inventory_by_genre(self) -> Dict[str, int]:
        """Get current inventory counts by genre."""
        inventory = {}
        for book in self.book_agents:
            if hasattr(book, 'genre') and hasattr(book, 'stock_level'):
                genre = book.genre
                if genre not in inventory:
                    inventory[genre] = 0
                inventory[genre] += book.stock_level
        return inventory
    
    def get_sales_by_genre(self) -> Dict[str, int]:
        """Get sales counts by genre."""
        sales = {}
        for book in self.book_agents:
            if hasattr(book, 'genre') and hasattr(book, 'sold_count'):
                genre = book.genre
                if genre not in sales:
                    sales[genre] = 0
                sales[genre] += book.sold_count
        return sales
    
    def get_employee_task_distribution(self) -> Dict[str, int]:
        """Get distribution of tasks across employees."""
        tasks = {}
        for emp in self.employee_agents:
            if hasattr(emp, 'tasks_completed'):
                for task_type, count in emp.tasks_completed.items():
                    if task_type not in tasks:
                        tasks[task_type] = 0
                    tasks[task_type] += count
        return tasks
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get a complete summary of the simulation state."""
        return {
            "step_count": self.step_count,
            "total_revenue": self.get_total_revenue(),
            "books_sold": self.get_books_sold(),
            "avg_satisfaction": self.get_avg_customer_satisfaction(),
            "inventory_by_genre": self.get_inventory_by_genre(),
            "sales_by_genre": self.get_sales_by_genre(),
            "employee_tasks": self.get_employee_task_distribution(),
            "active_customers": self.count_active_customers(),
            "total_customers": len(self.customer_agents),
            "total_employees": len(self.employee_agents),
            "total_books": len(self.book_agents)
        }