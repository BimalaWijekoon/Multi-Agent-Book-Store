# 📚 Bookstore Multi-Agent Simulation Dashboard

A modern, real-time web-based dashboard for monitoring and analyzing multi-agent simulations of a bookstore management system.

## 🌟 Features

### 🎮 Main Dashboard
- **Control Panel**: Configure simulation parameters (customers, employees, books, steps)
- **Real-time Terminal**: Live console output showing simulation progress
- **Live Metrics**: Real-time charts tracking revenue, sales, and satisfaction
- **Recent Activity**: Latest transactions and rule executions

### 📊 Graphs & Analytics
- **Revenue Tracking**: Cumulative and per-step revenue analysis
- **Agent Tracking**: Monitor customer, employee, and book activity
- **Rules Execution**: Visualize SWRL rule firing patterns
- **Message Throughput**: Track inter-agent communication
- **Customer Satisfaction**: Trend analysis and distribution
- **Inventory Levels**: Stock monitoring and sales correlation

### 👥 Agent Details
- **Customers**: View budgets, satisfaction levels, and preferences
- **Employees**: Track roles and expertise areas
- **Books**: Monitor pricing, stock levels, and sales
- Interactive DataTables with sorting, filtering, and search

### ⚙️ Rules Execution Log
- Detailed SWRL rule execution records
- Filter by rule type
- Search functionality
- Expandable cards showing:
  - Rule conditions
  - Actions taken
  - Affected entities
  - Timestamps

### 💬 Messages Log
- Complete inter-agent communication history
- Filter by message type
- Search across all message content
- JSON-formatted message details

### 📋 Summary & Export
- Comprehensive simulation statistics
- Performance metrics tables
- Visual charts and graphs
- **Export Options**:
  - 📄 PDF reports
  - 📝 JSON data
  - 📊 Excel spreadsheets
  - 📋 CSV files

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation & Launch

1. **Simple One-Command Launch**:
   ```bash
   python launch_dashboard.py
   ```

   This will:
   - ✓ Check Python version
   - ✓ Install required dependencies
   - ✓ Start the Flask server
   - ✓ Open the dashboard in your default browser

2. **Manual Launch** (if preferred):
   ```bash
   # Install dependencies
   pip install -r frontend/requirements.txt
   
   # Run the Flask application
   cd frontend
   python app.py
   
   # Open browser to http://localhost:5000
   ```

## 📖 Usage Guide

### Starting a Simulation

1. Navigate to the main dashboard (automatically opens)
2. Configure simulation parameters:
   - **Number of Customers**: 1-50 agents
   - **Number of Employees**: 1-20 agents
   - **Number of Books**: 1-100 items
   - **Simulation Steps**: 1-500 iterations

3. Click **"Start Simulation"**
4. Watch real-time updates in:
   - Terminal console
   - Stat cards
   - Live charts
   - Activity tables

### Navigating the Dashboard

Use the **navigation bar** at the top to access different sections:

- **Dashboard** 🏠: Main control panel and live monitoring
- **Graphs** 📊: Detailed analytics and visualizations
- **Agents** 👥: Agent details and statistics
- **Rules** ⚙️: SWRL rule execution logs
- **Messages** 💬: Communication history
- **Summary** 📋: Final reports and exports

### Theme Toggle

Click the **🌙/☀️** button in the navigation bar to switch between dark and light themes.

### Exporting Data

1. Navigate to **Summary** page
2. Click one of the export buttons:
   - **Export as PDF**: Formatted report with key metrics
   - **Export as JSON**: Complete data in JSON format
   - **Export as Excel**: Multi-sheet workbook with all data
   - **Export as CSV**: Metrics data in CSV format

## 🏗️ Architecture

### Backend (Flask + WebSocket)
- **Flask**: Web framework for serving pages and APIs
- **Flask-SocketIO**: Real-time bidirectional communication
- **Threading**: Background simulation execution
- **Logging**: Comprehensive data logging to JSONL/CSV files

### Frontend (HTML + CSS + JavaScript)
- **Modern CSS**: Glassmorphism effects, gradients, animations
- **Chart.js**: Interactive, responsive charts
- **DataTables.js**: Advanced table features
- **WebSocket Client**: Real-time updates without page refresh

### Simulation Engine
- **Mesa**: Agent-based modeling framework
- **Owlready2**: OWL ontology and SWRL rules
- **Custom Agents**: Customers, Employees, Books
- **Message Bus**: Inter-agent communication system

## 📁 Project Structure

```
frontend/
├── app.py                      # Flask application & simulation logic
├── requirements.txt            # Python dependencies
├── templates/                  # HTML templates
│   ├── index.html             # Main dashboard
│   ├── graphs.html            # Analytics page
│   ├── agents.html            # Agent details
│   ├── rules.html             # Rules log
│   ├── messages.html          # Messages log
│   └── summary.html           # Summary & export
└── static/
    ├── css/
    │   └── style.css          # Modern styling
    └── js/
        ├── dashboard.js       # Main dashboard logic
        ├── graphs.js          # Charts & analytics
        ├── agents.js          # Agent tables
        ├── rules.js           # Rules display
        ├── messages.js        # Messages display
        └── summary.js         # Summary & export logic
```

## 🔧 Configuration

### Server Settings
- **Host**: `0.0.0.0` (accessible from network)
- **Port**: `5000`
- **Debug Mode**: Enabled by default
- **WebSocket**: Enabled with threading mode

### Simulation Parameters
Default values (can be changed in UI):
- Customers: 5
- Employees: 2
- Books: 20
- Steps: 30

## 📊 Data Logging

All simulations create an output directory with:

```
output/simulation_YYYYMMDD_HHMMSS/
├── metrics_log.csv              # Time-series metrics
├── messages_log.jsonl           # All messages
├── transactions_log.jsonl       # Purchase transactions
├── interactions_log.jsonl       # Agent interactions
├── rules_execution_log.jsonl    # SWRL rule firings
├── agents_details.json          # Agent configurations
├── errors_log.txt               # Error messages
└── simulation_summary.json      # Final summary
```

## 🎨 Features Highlights

### Real-time Updates
- **WebSocket streaming**: Instant updates without page refresh
- **Live charts**: Automatic data refresh every 5-10 seconds
- **Console streaming**: Real-time log messages
- **Progress tracking**: Visual progress bar

### Interactive Visualizations
- **Zoomable charts**: Click and drag to zoom
- **Hover tooltips**: Detailed information on hover
- **Legend filtering**: Click legend items to toggle datasets
- **Responsive design**: Adapts to all screen sizes

### Advanced Filtering
- **Search**: Full-text search across all data
- **Type filters**: Filter by rule type, message type, etc.
- **Pagination**: Navigate through large datasets
- **Sorting**: Click column headers to sort

### Professional Design
- **Glassmorphism**: Modern frosted-glass effects
- **Gradient backgrounds**: Beautiful color transitions
- **Smooth animations**: Fade-in, slide-in effects
- **Dark/Light themes**: User preference support
- **Custom fonts**: Inter font family for clarity

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill existing Flask process
# Windows PowerShell:
Get-Process -Name python | Stop-Process

# Then restart
python launch_dashboard.py
```

### Dependencies Not Installing
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install manually
pip install Flask Flask-SocketIO Flask-CORS python-socketio eventlet
```

### Simulation Not Starting
1. Check console for error messages
2. Verify all agent files exist in `agents/` directory
3. Check ontology files in `ontology/` directory
4. Ensure `simulation/` module is accessible

### Browser Not Opening
Manually navigate to: `http://localhost:5000`

## 📝 API Endpoints

### REST APIs
- `GET /`: Main dashboard page
- `GET /graphs`: Graphs page
- `GET /agents`: Agents page
- `GET /rules`: Rules page
- `GET /messages`: Messages page
- `GET /summary`: Summary page
- `POST /api/start_simulation`: Start simulation
- `GET /api/simulation_status`: Get status
- `GET /api/get_latest_data`: Fetch latest data
- `GET /api/get_log/<type>`: Get specific log
- `GET /api/export/<format>`: Export data

### WebSocket Events
- `connect`: Client connection
- `console_log`: Terminal messages
- `metrics_update`: Metrics data
- `message_logged`: Message logged
- `transaction_logged`: Transaction logged
- `rule_executed`: Rule fired
- `interaction_logged`: Interaction logged
- `agents_initialized`: Agents created
- `simulation_complete`: Simulation finished
- `simulation_error`: Error occurred

## 🤝 Contributing

This dashboard integrates with the existing Bookstore MAS simulation. To extend:

1. Add new routes in `app.py`
2. Create HTML templates in `templates/`
3. Add JavaScript logic in `static/js/`
4. Update CSS in `static/css/style.css`

## 📄 License

Part of the Bookstore Multi-Agent Simulation project.

## 🎉 Credits

Built with:
- Flask & Flask-SocketIO
- Chart.js for visualizations
- DataTables.js for tables
- jsPDF for PDF export
- SheetJS for Excel export
- Mesa for agent-based modeling
- Owlready2 for ontology management

---

**Enjoy your simulation dashboard! 🚀📚**

For questions or issues, check the error logs in `output/` directories.
