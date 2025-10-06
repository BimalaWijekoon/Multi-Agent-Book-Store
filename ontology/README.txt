SWRL RULES USAGE GUIDE
====================

This guide explains how to use the Semantic Web Rule Language (SWRL) rules 
defined in the bookstore_rules.py module for the Bookstore Management System.

LOADING RULES
------------
To load rules into your simulation environment:

1. Import the rules module:
   from ontology.bookstore_rules import load_rules

2. Apply to your ontology:
   load_rules(bookstore_ontology)

3. Test rules independently:
   python -m ontology.bookstore_rules

RULE VALIDATION
--------------
To validate all rules against your ontology:

1. Import the validation function:
   from ontology.bookstore_rules import validate_rules

2. Run validation on your ontology:
   is_valid = validate_rules(bookstore_ontology)

RULE CATEGORIES
--------------
The rules are organized into three main categories:

1. Customer Behavior Rules:
   - purchase_transaction_rule: Processes purchases and updates inventory
   - budget_constraint_rule: Prevents purchases exceeding customer budget
   - preference_recommendation_rule: Recommends books based on preferences
   - customer_loyalty_upgrade_rule: Upgrades customer status based on purchases
   - premium_customer_discount_rule: Applies discounts for premium customers

2. Employee Workflow Rules:
   - inventory_restocking_rule: Triggers restocking when inventory is low
   - customer_service_rule: Routes customers to employees with relevant expertise
   - manager_override_rule: Allows managers to override pricing decisions
   - workload_distribution_rule: Balances tasks among employees

3. Book Management Rules:
   - dynamic_pricing_rule: Adjusts prices based on demand patterns
   - availability_status_rule: Updates availability based on inventory
   - book_recommendation_network_rule: Creates book recommendation networks
   - publisher_reorder_rule: Manages relationships with publishers
   - seasonal_pricing_rule: Applies seasonal price adjustments

INTEGRATION WITH AGENTS
---------------------
These rules are designed to integrate directly with agent behaviors in later phases:

- Customer agents will use these rules to make purchase decisions, manage budgets,
  and respond to recommendations.

- Employee agents will use these rules to determine actions like restocking,
  assisting customers, and managing inventory.

- Book-related rules will govern pricing dynamics, availability status, and
  recommendation networks that agents interact with.

TROUBLESHOOTING
-------------
Common rule execution issues and solutions:

1. Rule not firing:
   - Verify that the class instances have all required properties
   - Check that property value types match what the rule expects
   - Ensure rule conditions aren't conflicting

2. Rule executing incorrectly:
   - Check the SPARQL implementation for logical errors
   - Verify domain and range specifications for properties
   - Test with simple test cases and add logging

3. Performance issues:
   - Optimize rules to avoid complex chained reasoning
   - Prioritize rules by execution order importance
   - Split complex rules into simpler components

EXTENDING THE RULE SYSTEM
-----------------------
To add new rules:

1. Use the register_rule() function with:
   - A unique name
   - A description
   - SWRL syntax
   - SPARQL implementation

2. Add test cases to the create_test_instances() function
3. Validate the new rule using test_rule(rule_name, ontology)

MESSAGE BUS INTEGRATION
----------------------
The ontology and rules can be integrated with the Message Bus communication system:

1. Import the necessary modules:
   from communication.message_bus import MessageBus
   from ontology.advanced_bookstore_ontology import onto

2. Create an instance of the MessageBus:
   message_bus = MessageBus()

3. Integrate with the ontology:
   message_bus.integrate_with_ontology(onto)

4. Apply rules when processing messages:
   message_bus.apply_rules_to_message(message)

5. Get recommendations using the ontology:
   recommendations = message_bus.get_ontology_recommendations(customer_id, genre)

This integration allows the agent communication system to leverage the ontology 
and rules for validation, reasoning, and recommendations.