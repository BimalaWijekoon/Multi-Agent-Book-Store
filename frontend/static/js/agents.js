// ============================================
// AGENTS PAGE - DataTables Implementation
// Complete Rebuild with Clean Data Persistence
// ============================================

// Initialize WebSocket
const socket = io();

// Global state - DataTables instances
let dataTables = {};

// Global state - agents data
let agentsData = {
    customers: [],
    employees: [],
    books: []
};

// Track if tables are initialized
let tablesInitialized = false;

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('âœ“ Agents page connected to WebSocket');
});

socket.on('simulation_started', () => {
    console.log('âœ“ New simulation started - clearing agents data');
    
    // Clear all data
    agentsData = {
        customers: [],
        employees: [],
        books: []
    };
    
    // Clear all tables
    if (dataTables.customers) {
        dataTables.customers.clear().draw();
    }
    if (dataTables.employees) {
        dataTables.employees.clear().draw();
    }
    if (dataTables.books) {
        dataTables.books.clear().draw();
    }
    
    // Clear stats
    clearAllStats();
});

socket.on('agents_initialized', (agents) => {
    console.log('âœ“ Agents initialized:', agents);
    
    // Store agents data
    agentsData = agents || {
        customers: [],
        employees: [],
        books: []
    };
    
    // Update tables and stats
    updateAllTables();
    updateStats();
});

socket.on('simulation_complete', () => {
    console.log('âœ“ Simulation complete - agents data persisted');
    // Data stays in agentsData for navigation persistence
});

// ============================================
// DATATABLES INITIALIZATION
// ============================================

function initializeAllTables() {
    if (tablesInitialized) {
        console.log('Tables already initialized, skipping...');
        return;
    }
    
    console.log('Initializing DataTables...');
    
    try {
        // Initialize Customers Table
        dataTables.customers = $('#customersTable').DataTable({
            data: [],
            columns: [
                { title: 'ID' },
                { title: 'Name' },
                { title: 'Initial Budget' },
                { title: 'Remaining Budget' },
                { title: 'Total Spent' },
                { title: 'Books Purchased' },
                { title: 'Satisfaction' },
                { title: 'Loyalty Level' }
            ],
            pageLength: 10,
            order: [[6, 'desc']], // Sort by satisfaction (now column 6)
            language: {
                emptyTable: "No customer data available"
            },
            destroy: true
        });
        
        // Initialize Employees Table
        dataTables.employees = $('#employeesTable').DataTable({
            data: [],
            columns: [
                { title: 'ID' },
                { title: 'Name' },
                { title: 'Role' },
                { title: 'Expertise' },
                { title: 'Status' }
            ],
            pageLength: 10,
            language: {
                emptyTable: "No employee data available"
            },
            destroy: true
        });
        
        // Initialize Books Table
        dataTables.books = $('#booksTable').DataTable({
            data: [],
            columns: [
                { title: 'ID' },
                { title: 'Title' },
                { title: 'Genre' },
                { title: 'Price' },
                { title: 'Stock' },
                { title: 'Status' }
            ],
            pageLength: 10,
            order: [[4, 'asc']], // Sort by stock (low to high)
            language: {
                emptyTable: "No book data available"
            },
            destroy: true
        });
        
        tablesInitialized = true;
        console.log('âœ“ All DataTables initialized');
        
    } catch (error) {
        console.error('Error initializing DataTables:', error);
    }
}

// ============================================
// TABLE UPDATE FUNCTIONS
// ============================================

function updateAllTables() {
    if (!tablesInitialized) {
        initializeAllTables();
    }
    
    updateCustomersTable();
    updateEmployeesTable();
    updateBooksTable();
}

function updateCustomersTable() {
    if (!dataTables.customers) return;
    
    const customers = agentsData.customers || [];
    const tableData = customers.map(customer => {
        const satisfaction = parseFloat(customer.satisfaction || 0);
        const loyaltyLevel = customer.loyalty_level || 'New';
        const loyaltyClass = loyaltyLevel === 'Premium' ? 'badge-success' : 
                             loyaltyLevel === 'Regular' ? 'badge-info' : 'badge-warning';
        
        const initialBudget = parseFloat(customer.initial_budget) || 0;
        const remainingBudget = parseFloat(customer.remaining_budget) || parseFloat(customer.budget) || 0;
        const totalSpent = parseFloat(customer.total_spent) || 0;
        const booksPurchased = customer.books_purchased || 0;
        
        return [
            customer.id || 'N/A',
            customer.name || 'Unnamed Customer',
            `Rs. ${initialBudget.toFixed(2)}`,
            `Rs. ${remainingBudget.toFixed(2)}`,
            `Rs. ${totalSpent.toFixed(2)}`,
            booksPurchased,
            satisfaction.toFixed(2),
            `<span class="badge ${loyaltyClass}">${loyaltyLevel}</span>`
        ];
    });
    
    dataTables.customers.clear().rows.add(tableData).draw();
}

function updateEmployeesTable() {
    if (!dataTables.employees) return;
    
    const employees = agentsData.employees || [];
    const tableData = employees.map(employee => {
        const roleBadge = employee.role === 'Manager' 
            ? '<span class="badge badge-primary">Manager</span>' 
            : '<span class="badge badge-info">Sales</span>';
        
        return [
            employee.id || 'N/A',
            employee.name || 'Unnamed Employee',
            employee.role || 'Unknown',
            (employee.expertise || []).join(', ') || 'General',
            roleBadge
        ];
    });
    
    dataTables.employees.clear().rows.add(tableData).draw();
}

function updateBooksTable() {
    if (!dataTables.books) return;
    
    const books = agentsData.books || [];
    const tableData = books.map(book => {
        const stock = parseInt(book.stock || 0);
        const statusBadge = stock > 10 
            ? '<span class="badge badge-success">In Stock</span>' 
            : stock > 0 
            ? '<span class="badge badge-warning">Low Stock</span>' 
            : '<span class="badge badge-danger">Out of Stock</span>';
        
        return [
            book.id || 'N/A',
            book.title || book.name || book.id || 'Untitled',
            book.genre || 'Unknown',
            `Rs.{(book.price || 0).toFixed(2)}`,
            stock,
            statusBadge
        ];
    });
    
    dataTables.books.clear().rows.add(tableData).draw();
}

// ============================================
// STATS UPDATE FUNCTIONS
// ============================================

function updateStats() {
    updateCustomerStats();
    updateEmployeeStats();
    updateBookStats();
}

function updateCustomerStats() {
    const customers = agentsData.customers || [];
    
    // Customer count
    updateStatElement('customer-count', customers.length);
    
    // Average budget
    const avgBudget = customers.length > 0 
        ? customers.reduce((sum, c) => sum + (parseFloat(c.budget) || 0), 0) / customers.length 
        : 0;
    updateStatElement('avg-budget', `Rs. ${avgBudget.toFixed(2)}`);
    
    // Average satisfaction
    const avgSatisfaction = customers.length > 0 
        ? customers.reduce((sum, c) => sum + (parseFloat(c.satisfaction) || 0), 0) / customers.length 
        : 0;
    updateStatElement('avg-cust-satisfaction', avgSatisfaction.toFixed(2));
}

function updateEmployeeStats() {
    const employees = agentsData.employees || [];
    
    // Employee count
    updateStatElement('employee-count', employees.length);
    
    // Manager count
    const managerCount = employees.filter(e => e.role === 'Manager').length;
    updateStatElement('manager-count', managerCount);
}

function updateBookStats() {
    const books = agentsData.books || [];
    
    // Book count
    updateStatElement('book-count', books.length);
    
    // Total inventory
    const totalStock = books.reduce((sum, b) => sum + (parseInt(b.stock) || 0), 0);
    updateStatElement('total-inventory', totalStock);
    
    // Average price
    const avgPrice = books.length > 0 
        ? books.reduce((sum, b) => sum + (parseFloat(b.price) || 0), 0) / books.length 
        : 0;
    updateStatElement('avg-price', `Rs. ${avgPrice.toFixed(2)}`);
    
    // Low stock count
    const lowStockCount = books.filter(b => (parseInt(b.stock) || 0) < 5).length;
    updateStatElement('low-stock', lowStockCount);
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function clearAllStats() {
    const statIds = [
        'customer-count', 'avg-budget', 'avg-cust-satisfaction',
        'employee-count', 'manager-count',
        'book-count', 'total-inventory', 'avg-price', 'low-stock'
    ];
    
    statIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = '0';
        }
    });
}

// ============================================
// TAB NAVIGATION
// ============================================

document.querySelectorAll('.chart-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active from all tabs
        document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
        
        // Add active to clicked tab
        tab.classList.add('active');
        const tabName = tab.getAttribute('data-tab');
        const tabContent = document.getElementById(`${tabName}-tab`);
        if (tabContent) {
            tabContent.style.display = 'block';
        }
        
        // Adjust DataTable columns for proper display
        if (dataTables[tabName]) {
            dataTables[tabName].columns.adjust().draw();
        }
    });
});

// ============================================
// DATA PERSISTENCE - LOAD FROM SERVER
// ============================================

async function loadExistingData() {
    try {
        console.log('Loading existing agents data from server...');
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data && data.agents) {
            console.log('âœ“ Found existing agents data');
            
            // Restore agents data
            agentsData = data.agents || {
                customers: [],
                employees: [],
                books: []
            };
            
            // Update tables and stats
            updateAllTables();
            updateStats();
            
            console.log('âœ“ Agents page fully restored from server');
        } else {
            console.log('No previous agents data found');
        }
    } catch (error) {
        console.error('Error loading existing data:', error);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function refreshAgents() {
    console.log('Refreshing agents data...');
    loadExistingData();
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeButton = document.querySelector('.theme-toggle');
    if (themeButton) {
        themeButton.textContent = newTheme === 'dark' ? 'â˜€ï¸' : 'ðŸŒ™';
    }
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
const themeButton = document.querySelector('.theme-toggle');
if (themeButton) {
    themeButton.textContent = savedTheme === 'dark' ? 'â˜€ï¸' : 'ðŸŒ™';
}

// ============================================
// INITIALIZATION
// ============================================

$(document).ready(function() {
    console.log('Agents page loaded - initializing...');
    
    // Initialize empty tables first
    initializeAllTables();
    
    // Then try to load existing data
    loadExistingData();
});

