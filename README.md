# 📚 Multi-Agent Book Store Simulation

A sophisticated multi-agent simulation system for a Sri Lankan bookstore, featuring intelligent agents, ontology-based reasoning with SWRL rules, real-time web dashboard, and comprehensive analytics.

## 🌟 Overview

This project implements a comprehensive bookstore management system using multi-agent technology, semantic web ontologies, and modern web interfaces. The simulation models realistic interactions between customers, employees, and books in a Sri Lankan bookstore context with localized content and pricing.

### Key Features

- **🤖 Intelligent Multi-Agent System**: Customer, Employee, and Book agents with autonomous behavior
- **🧠 Ontology-Based Reasoning**: OWL ontology with SWRL rules for intelligent decision-making
- **💬 Message Bus Communication**: Asynchronous inter-agent messaging system
- **📊 Real-Time Web Dashboard**: Modern Flask-based interface with WebSocket updates
- **🇱🇰 Sri Lankan Localization**: Authentic Sri Lankan books, authors, and LKR currency
- **📈 Advanced Analytics**: Comprehensive metrics tracking and visualization
- **📄 Multi-Format Export**: PDF, JSON, Excel, and CSV report generation
- **🎨 Professional UI**: Glassmorphism design with dark/light theme support

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- pip (Python package installer)
- Internet connection (for first-time dependency installation)

### One-Command Launch

Simply run the launcher script to automatically set up and start everything:

```bash
python launch_dashboard.py
```

This will:
1. ✓ Verify Python version
2. ✓ Install all required dependencies
3. ✓ Start the Flask web server
4. ✓ Open the dashboard in your browser automatically

### Manual Installation (Alternative)

If you prefer manual setup:

```bash
# Install main dependencies
pip install -r requirements.txt

# Install frontend dependencies
pip install -r frontend/requirements.txt

# Start the dashboard
cd frontend
python app.py
```

Then open your browser to: `http://localhost:5000`

## 📖 Usage Guide

### Starting a Simulation

1. **Launch the Dashboard**
   ```bash
   python launch_dashboard.py
   ```

2. **Configure Parameters**
   - Number of Customers (1-50)
   - Number of Employees (1-20)
   - Number of Books (1-100)
   - Simulation Steps (1-500)

3. **Start Simulation**
   - Click "Start Simulation" button
   - Watch real-time updates in the dashboard
   - Monitor console output for detailed logs

4. **Explore Results**
   - View live charts and metrics
   - Check agent details and interactions
   - Analyze SWRL rule executions
   - Review message logs
   - Export comprehensive reports

### Dashboard Navigation

The web interface provides multiple views:

- **🏠 Dashboard**: Main control panel with live monitoring
- **📊 Graphs**: Detailed analytics and visualizations
- **👥 Agents**: Customer, employee, and book details
- **⚙️ Rules**: SWRL rule execution logs
- **💬 Messages**: Inter-agent communication history
- **📋 Summary**: Final reports and export options
- **ℹ️ About**: Project overview and technology highlights

### Running Command-Line Simulation

For automated testing or batch processing:

```bash
python test_simulation.py
```

This runs a predefined simulation with default parameters.

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Dashboard (Flask)                    │
│  Templates │ Static Assets │ WebSocket │ REST API           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Simulation Engine (Mesa)                    │
│  BookstoreModel │ Scheduler │ Data Collectors               │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼─────┐ ┌──────▼──────┐ ┌────▼─────────┐
│   Customer    │ │   Employee  │ │     Book     │
│    Agents     │ │    Agents   │ │    Agents    │
└───────┬───────┘ └──────┬──────┘ └──────┬───────┘
        │                │               │
        └────────────────┼───────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Message Bus System                        │
│  Message Routing │ Queue Management │ Logging               │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Ontology System (Owlready2)                     │
│  OWL Classes │ Properties │ SWRL Rules │ Reasoner           │
└─────────────────────────────────────────────────────────────┘
```

### Agent Architecture

#### Customer Agents
- **Behaviors**: Browse books, evaluate options, make purchases, rate satisfaction
- **Properties**: Budget (Rs. 5,000-20,000), preferences, satisfaction level, loyalty
- **Decision Making**: Price-based, genre-based, recommendation-based selection

#### Employee Agents
- **Behaviors**: Assist customers, manage inventory, provide recommendations
- **Properties**: Role (Manager/Sales), expertise areas, performance metrics
- **Responsibilities**: Customer service, stock management, sales optimization

#### Book Agents
- **Behaviors**: Update pricing, track inventory, manage availability
- **Properties**: Title, author, genre, price (Rs. 300-5,000), stock level
- **Features**: Dynamic pricing, popularity tracking, recommendation scoring

### Technology Stack

#### Backend
- **Mesa**: Agent-based modeling framework
- **Owlready2**: OWL ontology and SWRL rule engine
- **Flask**: Web application framework
- **Flask-SocketIO**: Real-time bidirectional communication
- **Python 3.8+**: Core programming language

#### Frontend
- **HTML5/CSS3**: Modern responsive design
- **JavaScript (ES6+)**: Dynamic interactions
- **Chart.js**: Interactive data visualizations
- **DataTables.js**: Advanced table features
- **WebSocket**: Real-time updates

#### Data & Export
- **Pandas**: Data manipulation and analysis
- **Matplotlib/Plotly**: Advanced visualizations
- **jsPDF**: PDF generation
- **SheetJS**: Excel export
- **FPDF/ReportLab**: Server-side PDF reports

## 📁 Project Structure

```
Multi-Agent-Book-Store/
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # Main Python dependencies
├── 📄 launch_dashboard.py                # One-command launcher script
├── 📄 test_simulation.py                 # Automated testing script
├── 📄 SRI_LANKAN_LOCALIZATION.md         # Localization documentation
├── 📄 .gitignore                         # Git ignore rules
│
├── 📁 agents/                            # Agent implementations
│   ├── __init__.py
│   ├── customer_agent.py                 # Customer agent logic
│   ├── employee_agent.py                 # Employee agent logic
│   ├── book_agent.py                     # Book agent logic
│   ├── agent_names.py                    # Name generation utilities
│   ├── realistic_names.py                # Name databases
│   └── README.txt                        # Agent documentation
│
├── 📁 simulation/                        # Simulation engine
│   ├── __init__.py
│   ├── bookstore_model.py                # Mesa model implementation
│   └── simulation_engine.py              # Core simulation logic
│
├── 📁 ontology/                          # Semantic web layer
│   ├── __init__.py
│   ├── advanced_bookstore_ontology.py    # OWL ontology definitions
│   ├── bookstore_rules.py                # SWRL rule implementations
│   └── README.txt                        # Ontology documentation
│
├── 📁 communication/                     # Message bus system
│   ├── __init__.py
│   ├── message_bus.py                    # Message routing and queuing
│   └── README.txt                        # Communication documentation
│
└── 📁 frontend/                          # Web dashboard
    ├── app.py                            # Flask application
    ├── requirements.txt                  # Frontend dependencies
    ├── README.md                         # Frontend documentation
    │
    ├── 📁 templates/                     # HTML templates
    │   ├── index.html                    # Main dashboard
    │   ├── graphs.html                   # Analytics page
    │   ├── agents.html                   # Agent details
    │   ├── rules.html                    # Rules execution log
    │   ├── messages.html                 # Message history
    │   └── summary.html                  # Summary & export
    │
    └── 📁 static/                        # Static assets
        ├── 📁 css/
        │   └── style.css                 # Custom styles
        └── 📁 js/
            ├── dashboard.js              # Main dashboard logic
            ├── graphs.js                 # Chart implementations
            ├── agents.js                 # Agent table logic
            ├── rules.js                  # Rules display
            ├── messages.js               # Message display
            └── summary.js                # Summary & export logic
```

## 🇱🇰 Sri Lankan Localization

### Authentic Book Collection

The simulation features **48 authentic Sri Lankan books** including:

#### Classic Sinhala Literature
- Gamperaliya - Martin Wickramasinghe
- Viragaya - W.A. Silva  
- Kaliyugaya - Martin Wickramasinghe
- Yuganthaya - Ediriweera Sarachchandra

#### Contemporary Sri Lankan Fiction
- The Seven Moons of Maali Almeida - Shehan Karunatilaka (Booker Prize 2022)
- Chinaman - Shehan Karunatilaka (Commonwealth Book Prize)
- Funny Boy - Shyam Selvadurai
- Running in the Family - Michael Ondaatje
- Island of a Thousand Mirrors - Nayomi Munaweera

#### Children's Classics
- Madol Duwa - G.B. Senanayake
- Ran Kirilli - Simon Nawagattegama
- The Story of Sigiri - Sybil Wettasinghe

### Currency and Pricing

- **Currency**: Sri Lankan Rupees (Rs.)
- **Book Prices**: Rs. 300 - Rs. 5,000
- **Customer Budgets**: Rs. 5,000 - Rs. 20,000
- **Realistic Market Rates**: Based on actual Sri Lankan bookstore pricing

See [SRI_LANKAN_LOCALIZATION.md](SRI_LANKAN_LOCALIZATION.md) for complete details.

## 📊 Data Output and Logging

Each simulation creates a timestamped output directory:

```
output/simulation_YYYYMMDD_HHMMSS/
├── metrics_log.csv                 # Time-series performance metrics
├── messages_log.jsonl              # All inter-agent messages
├── transactions_log.jsonl          # Purchase transactions
├── interactions_log.jsonl          # Agent interactions
├── rules_execution_log.jsonl       # SWRL rule firing events
├── agents_details.json             # Agent configurations
├── errors_log.txt                  # Error messages
└── simulation_summary.json         # Final summary statistics
```

### Export Formats

The dashboard supports multiple export formats:

- **📄 PDF**: Formatted reports with charts and tables
- **📝 JSON**: Complete simulation data in JSON format
- **📊 Excel**: Multi-sheet workbooks with all metrics
- **📋 CSV**: Simple CSV files for spreadsheet analysis

## ⚙️ Configuration

### Simulation Parameters

Configure via the web dashboard or modify default values in code:

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Customers | 1-50 | 5 | Number of customer agents |
| Employees | 1-20 | 2 | Number of employee agents |
| Books | 1-100 | 20 | Number of book items |
| Steps | 1-500 | 30 | Simulation iterations |

### Server Configuration

Edit `frontend/app.py` to customize:

```python
# Server settings
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5000       # Server port
DEBUG = True      # Enable debug mode
```

### Agent Behavior

Customize agent parameters in respective agent files:

- `agents/customer_agent.py`: Budget ranges, preferences
- `agents/employee_agent.py`: Role definitions, expertise
- `agents/book_agent.py`: Pricing strategies, inventory rules

## 🎯 Use Cases

### Educational
- **Multi-Agent Systems**: Learn MAS concepts with practical examples
- **Ontology Engineering**: Understand OWL and SWRL rule systems
- **Software Engineering**: Study clean architecture and design patterns

### Research
- **Agent Behavior Analysis**: Study emergent behaviors in retail scenarios
- **Economic Modeling**: Analyze pricing strategies and market dynamics
- **Rule-Based AI**: Research semantic reasoning and rule engines

### Commercial
- **Business Simulation**: Model bookstore operations and optimize strategies
- **Inventory Management**: Test stock management policies
- **Customer Analytics**: Understand shopping patterns and satisfaction

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9  # macOS/Linux

# Or use different port
cd frontend
python app.py --port 5001
```

### Dependencies Not Installing

```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install individually if batch fails
pip install mesa owlready2 flask flask-socketio
```

### Simulation Errors

1. **Check Python Version**
   ```bash
   python --version  # Should be 3.8+
   ```

2. **Verify File Integrity**
   ```bash
   # Ensure all directories exist
   ls agents/ simulation/ ontology/ communication/
   ```

3. **Review Error Logs**
   ```bash
   # Check output directory for error logs
   cat output/simulation_*/errors_log.txt
   ```

### Browser Issues

- **Dashboard Not Loading**: Try `http://127.0.0.1:5000` instead of `localhost`
- **WebSocket Errors**: Check browser console (F12) for connection issues
- **Charts Not Displaying**: Ensure JavaScript is enabled

## 🧪 Testing

### Run Automated Tests

```bash
# Run test simulation with predefined parameters
python test_simulation.py

# Run with pytest (if test suite exists)
pytest
```

### Manual Testing

1. Launch dashboard: `python launch_dashboard.py`
2. Configure small simulation (5 customers, 2 employees, 10 books, 10 steps)
3. Verify:
   - ✓ Agents initialize correctly
   - ✓ Transactions occur
   - ✓ Charts update in real-time
   - ✓ Data exports successfully

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make Your Changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed
4. **Test Your Changes**
   ```bash
   python test_simulation.py
   ```
5. **Commit Your Changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### Development Guidelines

- Use meaningful variable and function names
- Follow PEP 8 style guide for Python code
- Add docstrings to all classes and functions
- Update README.md if adding new features
- Test thoroughly before submitting PR

## 📚 Additional Documentation

- **[Frontend README](frontend/README.md)**: Detailed web dashboard documentation
- **[Sri Lankan Localization](SRI_LANKAN_LOCALIZATION.md)**: Localization details and book list
- **[Frontend Simplification](frontend/BACKEND_SIMPLIFICATION.md)**: Backend architecture notes
- **[Persistence Solution](frontend/SIMPLE_PERSISTENCE_SOLUTION.md)**: Data persistence strategies

## 📄 License

This project is open source and available for educational and research purposes.

## 🎉 Credits

### Technologies
- **Mesa**: Agent-based modeling framework
- **Owlready2**: OWL ontology management
- **Flask & Flask-SocketIO**: Web framework and real-time communication
- **Chart.js**: Beautiful data visualizations
- **DataTables.js**: Enhanced table functionality

### Data Sources
- Sri Lankan book titles and authors from authentic sources
- Currency conversion based on realistic market rates

## 📞 Support

For questions, issues, or feature requests:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review error logs in `output/` directories
3. Open an issue on GitHub with detailed information

## 🌟 Acknowledgments

Special thanks to the Sri Lankan literary community for inspiring the authentic book collection and the open-source community for the excellent libraries that made this project possible.

---

**Made with ❤️ for the Multi-Agent Systems and Semantic Web community**

*Happy Simulating! 🚀📚*
