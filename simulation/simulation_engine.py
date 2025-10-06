"""
Simulation Engine Implementation for the Bookstore Management System.

This module provides the control mechanism for executing the Mesa-based
simulation with features for managing execution flow and state persistence.
"""

import logging
import time
import json
import datetime
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from simulation.bookstore_model import BookstoreModel

logger = logging.getLogger(__name__)

class SimulationEngine:
    """
    Controls the execution of the bookstore simulation with pause/resume/stop capabilities.
    
    This engine manages the simulation execution flow, controls simulation speed,
    and provides features for saving and loading simulation state.
    """
    
    def __init__(self, 
                 model_params: Optional[Dict[str, Any]] = None,
                 max_steps: int = 1000,
                 output_dir: Optional[str] = None):
        """
        Initialize the simulation engine.
        
        Args:
            model_params: Parameters for the BookstoreModel initialization
            max_steps: Maximum number of simulation steps
            output_dir: Directory for saving simulation outputs and states
        """
        # Default model parameters
        default_params = {
            "num_customers": 10,
            "num_employees": 3,
            "num_books": 50,
            "width": 20,
            "height": 20
        }
        
        # Use provided params or defaults
        self.model_params = model_params if model_params is not None else default_params
        
        # Set up simulation configuration
        self.max_steps = max_steps
        self.current_step = 0
        self.speed_factor = 1.0  # Normal speed
        self.is_running = False
        self.is_paused = False
        self.step_delay = 1.0  # Base delay between steps in seconds
        
        # Set up output directory
        if output_dir is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join("output", f"simulation_{timestamp}")
        
        self.output_dir = Path(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize model
        self.model = None
        self.metrics_history = []
        self._initialize_model()
        
        logger.info(f"Simulation engine initialized with output directory: {self.output_dir}")
    
    def _initialize_model(self):
        """Initialize the bookstore model with current parameters."""
        logger.info("Initializing bookstore model...")
        self.model = BookstoreModel(**self.model_params)
        self.current_step = 0
        self.metrics_history = []
        logger.info("Bookstore model initialized successfully.")
    
    def start(self):
        """Start the simulation from the beginning or current state."""
        logger.info("Starting simulation...")
        self.is_running = True
        self.is_paused = False
    
    def pause(self):
        """Pause the simulation execution."""
        logger.info("Pausing simulation...")
        self.is_paused = True
    
    def resume(self):
        """Resume a paused simulation."""
        logger.info("Resuming simulation...")
        self.is_paused = False
    
    def stop(self):
        """Stop the simulation execution."""
        logger.info("Stopping simulation...")
        self.is_running = False
        self.is_paused = False
        
    def step(self):
        """
        Execute a single step of the simulation.
        
        Returns:
            bool: True if step was executed, False if simulation is done or paused
        """
        if not self.is_running or self.is_paused:
            logger.info("Simulation is not running or is paused. Cannot step.")
            return False
        
        if self.current_step >= self.max_steps:
            logger.info("Reached maximum steps. Simulation complete.")
            self.is_running = False
            return False
        
        if self.model is None:
            logger.error("No model initialized. Cannot step.")
            return False
        
        # Execute the model step
        logger.debug(f"Executing step {self.current_step + 1} of {self.max_steps}")
        self.model.step()
        self.current_step += 1
        
        # Collect metrics after the step
        metrics = {
            "step": self.current_step,
            "revenue": self.model.get_total_revenue(),
            "customers": self.model.count_active_customers(),
            "books_sold": self.model.get_books_sold(),
            "satisfaction": self.model.get_avg_customer_satisfaction()
        }
        self.metrics_history.append(metrics)
        
        # Apply step delay based on speed factor
        time.sleep(self.step_delay / self.speed_factor)
        
        return True
        
    def get_current_metrics(self):
        """
        Get the current metrics from the simulation model.
        
        Returns:
            Dict[str, Any]: Dictionary containing the current metrics
        """
        if self.model is None:
            logger.warning("No model initialized. Unable to get metrics.")
            return {
                "Total Revenue": 0.0,
                "Books Sold": 0,
                "Active Customers": 0,
                "Average Customer Satisfaction": 0.0
            }
        
        # Get data from the model's datacollector
        model_vars = self.model.datacollector.get_model_vars_dataframe()
        
        if model_vars.empty:
            # If no data, return zeros
            return {
                "Total Revenue": 0.0,
                "Books Sold": 0,
                "Active Customers": 0,
                "Average Customer Satisfaction": 0.0
            }
        
        # Get the latest values
        latest = model_vars.iloc[-1].to_dict()
        return latest
        logger.info("Stopping simulation...")
        self.is_running = False
    
    def reset(self):
        """Reset the simulation to initial state."""
        logger.info("Resetting simulation...")
        self.is_running = False
        self.is_paused = False
        self._initialize_model()
    
    def set_speed(self, speed_factor: float):
        """
        Set simulation speed.
        
        Args:
            speed_factor: Factor to adjust simulation speed (0.5 = half speed, 2.0 = double speed)
        """
        logger.info(f"Setting simulation speed to {speed_factor}x")
        self.speed_factor = max(0.1, min(10.0, speed_factor))  # Clamp between 0.1x and 10x
    
    def update_model_params(self, new_params: Dict[str, Any]):
        """
        Update model parameters and reset the simulation.
        
        Args:
            new_params: New parameters to update
        """
        logger.info("Updating model parameters...")
        self.model_params.update(new_params)
        self.reset()
    
    def step(self):
        """Execute a single simulation step."""
        if self.is_running and not self.is_paused and self.current_step < self.max_steps:
            logger.info(f"Executing step {self.current_step + 1} of {self.max_steps}...")
            
            # Run one step of the model
            self.model.step()
            
            # Track metrics
            metrics = self._collect_metrics()
            self.metrics_history.append(metrics)
            
            # Update step count
            self.current_step += 1
            
            # Check if simulation is complete
            if self.current_step >= self.max_steps:
                logger.info("Simulation reached maximum steps.")
                self.is_running = False
                self._save_results()
            
            return True
        return False
    
    def run_simulation(self):
        """
        Run the full simulation until completion or manual stop.
        
        This method blocks until simulation is complete or stopped.
        """
        logger.info("Running full simulation...")
        self.start()
        
        while self.is_running:
            if not self.is_paused:
                self.step()
                
                # Apply speed factor to delay
                actual_delay = self.step_delay / max(0.1, self.speed_factor)
                time.sleep(actual_delay)
            else:
                # When paused, just sleep briefly to prevent CPU spinning
                time.sleep(0.1)
        
        logger.info("Simulation run completed.")
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current simulation metrics."""
        if not self.model:
            return {}
        
        metrics = {
            "step": self.current_step,
            "revenue": self.model.get_total_revenue(),
            "active_customers": self.model.count_active_customers(),
            "books_sold": self.model.get_books_sold(),
            "customer_satisfaction": self.model.get_avg_customer_satisfaction(),
            "inventory": self.model.get_inventory_by_genre(),
            "sales_by_genre": self.model.get_sales_by_genre(),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return metrics
    
    def _save_results(self):
        """Save simulation results to output directory."""
        logger.info("Saving simulation results...")
        
        # Save metrics history
        metrics_file = self.output_dir / "metrics_history.json"
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)
        
        # Save final simulation state
        summary_file = self.output_dir / "simulation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(self.model.get_simulation_summary(), f, indent=2)
        
        logger.info(f"Simulation results saved to {self.output_dir}")
    
    def save_state(self, filename: Optional[str] = None):
        """
        Save the current simulation state.
        
        Args:
            filename: Optional custom filename, otherwise uses timestamp
        """
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_state_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        state = {
            "model_params": self.model_params,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "metrics_history": self.metrics_history,
            "saved_at": datetime.datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Simulation state saved to {filepath}")
        return str(filepath)
    
    def load_state(self, filepath: str):
        """
        Load a previously saved simulation state.
        
        Args:
            filepath: Path to the saved state file
        """
        logger.info(f"Loading simulation state from {filepath}")
        
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.model_params = state.get("model_params", self.model_params)
            self.current_step = state.get("current_step", 0)
            self.max_steps = state.get("max_steps", self.max_steps)
            self.metrics_history = state.get("metrics_history", [])
            
            # Re-initialize the model with loaded parameters
            self._initialize_model()
            
            # Re-run steps to reach the saved state
            for _ in range(self.current_step):
                self.model.step()
            
            logger.info(f"Simulation state loaded successfully: Step {self.current_step}/{self.max_steps}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load simulation state: {e}")
            return False
    
    def get_progress(self) -> Tuple[int, int, float]:
        """
        Get the current simulation progress.
        
        Returns:
            Tuple of (current_step, max_steps, progress_percentage)
        """
        percentage = (self.current_step / self.max_steps * 100) if self.max_steps > 0 else 0
        return self.current_step, self.max_steps, percentage
    
    def get_latest_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics collected."""
        if self.metrics_history:
            return self.metrics_history[-1]
        return {}