// ============================================
// SUMMARY PAGE - Enhanced Comprehensive Report
// With Additional Charts, Agent Details, and Statistics
// ============================================

// Initialize WebSocket
const socket = io();

// Global state - comprehensive summary data
let summaryData = {
    metrics: [],
    transactions: [],
    rules: [],
    agents: {},
    customers: [],
    employees: [],
    books: []
};

// Chart instances
let charts = {};

// Pagination state
let pagination = {
    customers: { page: 1, pageSize: 10, total: 0 },
    employees: { page: 1, pageSize: 10, total: 0 },
    books: { page: 1, pageSize: 15, total: 0 }
};

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('âœ“ Summary page connected to WebSocket');
});

socket.on('simulation_started', () => {
    console.log('âœ“ New simulation started - clearing summary');
    
    // Clear all data
    summaryData = {
        metrics: [],
        transactions: [],
        rules: [],
        agents: {},
        customers: [],
        employees: [],
        books: []
    };
    
    // Clear display
    clearSummaryDisplay();
});

socket.on('metrics_update', (metrics) => {
    summaryData.metrics.push(metrics);
});

socket.on('transaction_logged', (transaction) => {
    summaryData.transactions.push(transaction);
});

socket.on('rule_executed', (rule) => {
    summaryData.rules.push(rule);
});

socket.on('agents_initialized', (agents) => {
    summaryData.agents = agents;
    loadAgentDetails();
});

socket.on('simulation_complete', (summary) => {
    console.log('âœ“ Simulation complete - generating comprehensive summary');
    
    // Update with final summary data
    if (summary && summary.final_metrics) {
        summaryData.metrics.push(summary.final_metrics);
    }
    
    // Load all data and generate comprehensive report
    loadAgentDetails();
    updateComprehensiveSummary();
});

// ============================================
// DATA LOADING FUNCTIONS
// ============================================

async function loadAgentDetails() {
    try {
        const response = await fetch('/api/get_agents');
        const data = await response.json();
        
        if (data && data.agents) {
            summaryData.customers = data.agents.customers || [];
            summaryData.employees = data.agents.employees || [];
            summaryData.books = data.agents.books || [];
            
            // Update pagination totals
            pagination.customers.total = summaryData.customers.length;
            pagination.employees.total = summaryData.employees.length;
            pagination.books.total = summaryData.books.length;
            
            // Update tables
            updateCustomerTable();
            updateEmployeeTable();
            updateBookTable();
            updateTopPerformers();
            
            // CRITICAL: Update book revenue chart AFTER books data is loaded
            updateBookRevenueChart();
        }
    } catch (error) {
        console.error('Error loading agent details:', error);
    }
}

// ============================================
// COMPREHENSIVE SUMMARY UPDATE
// ============================================

function updateComprehensiveSummary() {
    if (!summaryData.metrics || summaryData.metrics.length === 0) {
        console.log('No metrics data available for summary');
        return;
    }
    
    const latest = summaryData.metrics[summaryData.metrics.length - 1];
    
    // Update header timestamp
    const timestampElement = document.getElementById('summaryTimestamp');
    if (timestampElement) {
        timestampElement.textContent = `Generated on ${new Date().toLocaleString()}`;
    }
    
    // Update all sections
    updateKeyMetrics(latest);
    updatePerformanceMetrics(latest);
    updateRulesStatistics(latest);
    updateOntologyStatistics(latest);
    updateRulesExecutionTable();
    updateConfiguration(latest);
    
    // Update all charts
    updateAllCharts();
    
    // Update agent tables
    updateCustomerTable();
    updateEmployeeTable();
    updateBookTable();
    updateTopPerformers();
}

function updateKeyMetrics(latest) {
    updateStatElement('final-revenue', `Rs. ${(parseFloat(latest.total_revenue) || 0).toFixed(2)}`);
    updateStatElement('final-books-sold', latest.books_sold || 0);
    updateStatElement('final-satisfaction', (parseFloat(latest.avg_customer_satisfaction) || 0).toFixed(2));
    updateStatElement('final-messages', latest.messages_processed || 0);
}

function updatePerformanceMetrics(latest) {
    const performanceElement = document.getElementById('performanceMetrics');
    if (!performanceElement) return;
    
    const avgTransactionValue = latest.books_sold > 0 
        ? (parseFloat(latest.total_revenue) / latest.books_sold).toFixed(2) 
        : '0.00';
    
    const performanceHtml = `
        <tr>
            <td><strong>Total Steps</strong></td>
            <td>${latest.step || 0}</td>
        </tr>
        <tr>
            <td><strong>Active Customers</strong></td>
            <td>${latest.active_customers || 0}</td>
        </tr>
        <tr>
            <td><strong>Active Employees</strong></td>
            <td>${latest.active_employees || 0}</td>
        </tr>
        <tr>
            <td><strong>Total Books</strong></td>
            <td>${latest.total_books || 0}</td>
        </tr>
        <tr>
            <td><strong>Books in Stock</strong></td>
            <td>${latest.books_in_stock || 0}</td>
        </tr>
        <tr>
            <td><strong>Transactions Completed</strong></td>
            <td>${summaryData.transactions.length}</td>
        </tr>
        <tr>
            <td><strong>Average Transaction Value</strong></td>
            <td>Rs. ${avgTransactionValue}</td>
        </tr>
    `;
    
    performanceElement.innerHTML = performanceHtml;
}

function updateRulesStatistics(latest) {
    const rulesElement = document.getElementById('rulesStatistics');
    if (!rulesElement) return;
    
    // Count rules by name
    const ruleCounts = {};
    (summaryData.rules || []).forEach(rule => {
        const ruleName = rule.rule_name || 'Unknown';
        ruleCounts[ruleName] = (ruleCounts[ruleName] || 0) + 1;
    });
    
    // Get top 5 rules
    const topRules = Object.entries(ruleCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    const avgRulesPerStep = latest.step > 0 
        ? (summaryData.rules.length / latest.step).toFixed(1) 
        : '0.0';
    
    const rulesHtml = `
        <tr>
            <td><strong>Total Rules Executed</strong></td>
            <td>${summaryData.rules.length}</td>
        </tr>
        <tr>
            <td><strong>Unique Rules</strong></td>
            <td>${Object.keys(ruleCounts).length}</td>
        </tr>
        <tr>
            <td><strong>Avg Rules per Step</strong></td>
            <td>${avgRulesPerStep}</td>
        </tr>
        <tr>
            <td colspan="2"><strong>Top 5 Rules:</strong></td>
        </tr>
        ${topRules.map(([name, count]) => `
            <tr>
                <td style="padding-left: 1rem;">${name.replace(/_/g, ' ')}</td>
                <td>${count}</td>
            </tr>
        `).join('')}
    `;
    
    rulesElement.innerHTML = rulesHtml;
}

function updateOntologyStatistics(latest) {
    // Update ontology stat cards
    const totalClasses = (latest.active_customers || 0) + (latest.active_employees || 0) + (latest.total_books || 0);
    updateStatElement('ontology-classes', totalClasses);
    updateStatElement('ontology-properties', summaryData.rules.length);
    updateStatElement('ontology-relationships', summaryData.transactions.length);
    
    // Update ontology details table
    const ontologyTable = document.getElementById('ontologyDetailsTable');
    if (!ontologyTable) return;
    
    const ontologyHtml = `
        <tr>
            <td>Customer Entities</td>
            <td>${latest.active_customers || 0}</td>
            <td><span class="badge badge-success">Active</span></td>
        </tr>
        <tr>
            <td>Employee Entities</td>
            <td>${latest.active_employees || 0}</td>
            <td><span class="badge badge-success">Active</span></td>
        </tr>
        <tr>
            <td>Book Entities</td>
            <td>${latest.total_books || 0}</td>
            <td><span class="badge badge-success">Active</span></td>
        </tr>
        <tr>
            <td>Transaction Entities</td>
            <td>${summaryData.transactions.length}</td>
            <td><span class="badge badge-info">Recorded</span></td>
        </tr>
        <tr>
            <td>Rule Executions</td>
            <td>${summaryData.rules.length}</td>
            <td><span class="badge badge-warning">Executed</span></td>
        </tr>
        <tr>
            <td>Message Entities</td>
            <td>${latest.messages_processed || 0}</td>
            <td><span class="badge badge-info">Processed</span></td>
        </tr>
    `;
    
    ontologyTable.innerHTML = ontologyHtml;
}

function updateRulesExecutionTable() {
    const rulesExecTable = document.getElementById('rulesExecutionTable');
    if (!rulesExecTable) return;
    
    // Analyze rules execution
    const ruleStats = {};
    (summaryData.rules || []).forEach(rule => {
        const ruleName = rule.rule_name || 'Unknown';
        if (!ruleStats[ruleName]) {
            ruleStats[ruleName] = {
                count: 0,
                totalTime: 0,
                successes: 0
            };
        }
        ruleStats[ruleName].count++;
        ruleStats[ruleName].totalTime += rule.execution_time || 0;
        // If success property exists, use it; otherwise assume success if rule was executed
        if (rule.success !== false) ruleStats[ruleName].successes++;
    });
    
    const rulesHtml = Object.entries(ruleStats).map(([name, stats]) => {
        const avgTime = stats.count > 0 ? (stats.totalTime / stats.count).toFixed(2) : '0.00';
        const successRate = stats.count > 0 ? ((stats.successes / stats.count) * 100).toFixed(1) : '100.0';
        const statusClass = successRate >= 90 ? 'badge-success' : successRate >= 70 ? 'badge-warning' : 'badge-error';
        
        return `
            <tr>
                <td>${name.replace(/_/g, ' ')}</td>
                <td>${stats.count}</td>
                <td>${successRate}%</td>
                <td>${avgTime}</td>
                <td><span class="badge ${statusClass}">${successRate >= 90 ? 'Excellent' : successRate >= 70 ? 'Good' : 'Needs Review'}</span></td>
            </tr>
        `;
    }).join('');
    
    rulesExecTable.innerHTML = rulesHtml || '<tr><td colspan="5" style="text-align: center;">No rules data available</td></tr>';
}

function updateConfiguration(latest) {
    const configElement = document.getElementById('configDetails');
    if (!configElement) return;
    
    const config = {
        'Simulation Steps': latest.step || 0,
        'Customers': latest.active_customers || 0,
        'Employees': latest.active_employees || 0,
        'Books': latest.total_books || 0,
        'Rules Enabled': Object.keys(getRuleCounts()).length,
        'Timestamp': new Date().toISOString(),
        'Status': 'Complete'
    };
    
    configElement.textContent = JSON.stringify(config, null, 2);
}

// ============================================
// AGENT DETAIL TABLES
// ============================================

function updateCustomerTable() {
    const tableElement = document.getElementById('customerDetailsTable');
    if (!tableElement) return;
    
    const filteredCustomers = filterCustomers();
    const start = (pagination.customers.page - 1) * pagination.customers.pageSize;
    const end = start + pagination.customers.pageSize;
    const pageCustomers = filteredCustomers.slice(start, end);
    
    if (pageCustomers.length === 0) {
        tableElement.innerHTML = '<tr><td colspan="7" style="text-align: center;">No customers found</td></tr>';
        return;
    }
    
    const customersHtml = pageCustomers.map(customer => {
        const loyaltyClass = customer.loyalty_level === 'Premium' ? 'badge-success' : 
                             customer.loyalty_level === 'Regular' ? 'badge-info' : 'badge-warning';
        
        const initialBudget = parseFloat(customer.initial_budget) || 100;
        const remainingBudget = parseFloat(customer.remaining_budget) || 0;
        const totalSpent = parseFloat(customer.total_spent) || 0;
        
        return `
            <tr>
                <td>${customer.id || 'N/A'}</td>
                <td>${customer.name || 'Unknown'}</td>
                <td>Rs. ${initialBudget.toFixed(2)}</td>
                <td>Rs. ${remainingBudget.toFixed(2)}</td>
                <td>Rs. ${totalSpent.toFixed(2)}</td>
                <td>${customer.books_purchased || 0}</td>
                <td>${(parseFloat(customer.satisfaction) || 0).toFixed(2)}</td>
                <td><span class="badge ${loyaltyClass}">${customer.loyalty_level || 'New'}</span></td>
            </tr>
        `;
    }).join('');
    
    tableElement.innerHTML = customersHtml;
    
    // Update pagination
    updatePaginationControls('customer', filteredCustomers.length);
}

function updateEmployeeTable() {
    const tableElement = document.getElementById('employeeDetailsTable');
    if (!tableElement) return;
    
    const filteredEmployees = filterEmployees();
    const start = (pagination.employees.page - 1) * pagination.employees.pageSize;
    const end = start + pagination.employees.pageSize;
    const pageEmployees = filteredEmployees.slice(start, end);
    
    if (pageEmployees.length === 0) {
        tableElement.innerHTML = '<tr><td colspan="7" style="text-align: center;">No employees found</td></tr>';
        return;
    }
    
    const employeesHtml = pageEmployees.map(employee => {
        const roleClass = employee.role === 'Manager' ? 'badge-success' : 
                          employee.role === 'Supervisor' ? 'badge-info' : 
                          employee.role === 'Staff' ? 'badge-warning' : 'badge-error';
        
        const performance = employee.performance || 'Good';
        const perfClass = performance === 'Excellent' ? 'badge-success' : 
                          performance === 'Good' ? 'badge-info' : 'badge-warning';
        
        return `
            <tr>
                <td>${employee.id || 'N/A'}</td>
                <td>${employee.name || 'Unknown'}</td>
                <td><span class="badge ${roleClass}">${employee.role || 'Staff'}</span></td>
                <td>Rs. ${(parseFloat(employee.salary) || 0).toFixed(2)}</td>
                <td>${employee.interactions || 0}</td>
                <td><span class="badge ${perfClass}">${performance}</span></td>
                <td><span class="badge badge-success">Active</span></td>
            </tr>
        `;
    }).join('');
    
    tableElement.innerHTML = employeesHtml;
    
    // Update pagination
    updatePaginationControls('employee', filteredEmployees.length);
}

function updateBookTable() {
    const tableElement = document.getElementById('bookDetailsTable');
    if (!tableElement) return;
    
    const filteredBooks = filterBooks();
    const start = (pagination.books.page - 1) * pagination.books.pageSize;
    const end = start + pagination.books.pageSize;
    const pageBooks = filteredBooks.slice(start, end);
    
    if (pageBooks.length === 0) {
        tableElement.innerHTML = '<tr><td colspan="8" style="text-align: center;">No books found</td></tr>';
        return;
    }
    
    const booksHtml = pageBooks.map(book => {
        return `
            <tr>
                <td>${book.id || 'N/A'}</td>
                <td>${book.title || 'Unknown'}</td>
                <td>${book.author || 'Unknown'}</td>
                <td>${book.genre || 'General'}</td>
                <td>Rs. ${(parseFloat(book.price) || 0).toFixed(2)}</td>
                <td>${book.stock || 0}</td>
                <td>${book.sales || 0}</td>
                <td>${(parseFloat(book.avg_rating) || 0).toFixed(1)} â­</td>
            </tr>
        `;
    }).join('');
    
    tableElement.innerHTML = booksHtml;
    
    // Update pagination
    updatePaginationControls('book', filteredBooks.length);
}

function updateTopPerformers() {
    // Top Books
    const topBooksTable = document.getElementById('topBooksTable');
    if (topBooksTable && summaryData.books.length > 0) {
        const topBooks = [...summaryData.books]
            .sort((a, b) => (b.sales || 0) - (a.sales || 0))
            .slice(0, 5);
        
        const topBooksHtml = topBooks.map((book, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${book.title || 'Unknown'}</td>
                <td>${book.sales || 0}</td>
                <td>Rs. ${((book.price || 0) * (book.sales || 0)).toFixed(2)}</td>
            </tr>
        `).join('');
        
        topBooksTable.innerHTML = topBooksHtml || '<tr><td colspan="4" style="text-align: center;">No data</td></tr>';
    }
    
    // Top Customers
    const topCustomersTable = document.getElementById('topCustomersTable');
    if (topCustomersTable && summaryData.customers.length > 0) {
        const topCustomers = [...summaryData.customers]
            .sort((a, b) => (b.books_purchased || 0) - (a.books_purchased || 0))
            .slice(0, 5);
        
        const topCustomersHtml = topCustomers.map((customer, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${customer.name || 'Unknown'}</td>
                <td>${customer.books_purchased || 0}</td>
                <td>Rs. ${(parseFloat(customer.total_spent) || 0).toFixed(2)}</td>
            </tr>
        `).join('');
        
        topCustomersTable.innerHTML = topCustomersHtml || '<tr><td colspan="4" style="text-align: center;">No data</td></tr>';
    }
}

// ============================================
// FILTERING AND SEARCH
// ============================================

function filterCustomers() {
    const searchTerm = (document.getElementById('customerSearchInput')?.value || '').toLowerCase();
    
    if (!searchTerm) return summaryData.customers;
    
    return summaryData.customers.filter(customer => 
        (customer.name || '').toLowerCase().includes(searchTerm) ||
        (customer.id || '').toString().includes(searchTerm)
    );
}

function filterEmployees() {
    const searchTerm = (document.getElementById('employeeSearchInput')?.value || '').toLowerCase();
    
    if (!searchTerm) return summaryData.employees;
    
    return summaryData.employees.filter(employee => 
        (employee.name || '').toLowerCase().includes(searchTerm) ||
        (employee.id || '').toString().includes(searchTerm) ||
        (employee.role || '').toLowerCase().includes(searchTerm)
    );
}

function filterBooks() {
    const searchTerm = (document.getElementById('bookSearchInput')?.value || '').toLowerCase();
    const genreFilter = document.getElementById('genreFilter')?.value || '';
    
    let filtered = summaryData.books;
    
    if (searchTerm) {
        filtered = filtered.filter(book => 
            (book.title || '').toLowerCase().includes(searchTerm) ||
            (book.author || '').toLowerCase().includes(searchTerm) ||
            (book.id || '').toString().includes(searchTerm)
        );
    }
    
    if (genreFilter) {
        filtered = filtered.filter(book => book.genre === genreFilter);
    }
    
    return filtered;
}

// ============================================
// PAGINATION CONTROLS
// ============================================

function updatePaginationControls(type, totalFiltered) {
    const paginationDiv = document.getElementById(`${type}Pagination`);
    const pageInfo = document.getElementById(`${type}PageInfo`);
    
    if (!paginationDiv || !pageInfo) return;
    
    const totalPages = Math.ceil(totalFiltered / pagination[type + 's'].pageSize);
    
    if (totalPages <= 1) {
        paginationDiv.style.display = 'none';
        return;
    }
    
    paginationDiv.style.display = 'flex';
    pageInfo.textContent = `Page ${pagination[type + 's'].page} of ${totalPages}`;
}

function prevCustomerPage() {
    if (pagination.customers.page > 1) {
        pagination.customers.page--;
        updateCustomerTable();
    }
}

function nextCustomerPage() {
    const totalPages = Math.ceil(filterCustomers().length / pagination.customers.pageSize);
    if (pagination.customers.page < totalPages) {
        pagination.customers.page++;
        updateCustomerTable();
    }
}

function prevEmployeePage() {
    if (pagination.employees.page > 1) {
        pagination.employees.page--;
        updateEmployeeTable();
    }
}

function nextEmployeePage() {
    const totalPages = Math.ceil(filterEmployees().length / pagination.employees.pageSize);
    if (pagination.employees.page < totalPages) {
        pagination.employees.page++;
        updateEmployeeTable();
    }
}

function prevBookPage() {
    if (pagination.books.page > 1) {
        pagination.books.page--;
        updateBookTable();
    }
}

function nextBookPage() {
    const totalPages = Math.ceil(filterBooks().length / pagination.books.pageSize);
    if (pagination.books.page < totalPages) {
        pagination.books.page++;
        updateBookTable();
    }
}

// ============================================
// COMPREHENSIVE CHART FUNCTIONS
// ============================================

function updateAllCharts() {
    if (!summaryData.metrics || summaryData.metrics.length === 0) return;
    
    updateRevenueChart();
    updateRulesChart();
    updateAgentActivityChart();
    updateMessageDistributionChart();
    updateBookRevenueChart();
    updateSatisfactionTrendChart();
}

function updateRevenueChart() {
    const canvas = document.getElementById('summaryRevenueChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.revenue) charts.revenue.destroy();
    
    charts.revenue = new Chart(ctx, {
        type: 'line',
        data: {
            labels: summaryData.metrics.map(m => `Step ${m.step}`),
            datasets: [{
                label: 'Revenue',
                data: summaryData.metrics.map(m => parseFloat(m.total_revenue) || 0),
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Revenue Over Time')
    });
}

function updateRulesChart() {
    const canvas = document.getElementById('summaryRulesChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.rules) charts.rules.destroy();
    
    const ruleCounts = getRuleCounts();
    
    charts.rules = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(ruleCounts).map(name => name.replace(/_/g, ' ')),
            datasets: [{
                data: Object.values(ruleCounts),
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#ec4899', 
                    '#10b981', '#f59e0b', '#3b82f6',
                    '#14b8a6', '#f43f5e', '#8b5cf6'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Rules Execution Distribution',
                    color: '#ffffff'
                },
                legend: {
                    position: 'right',
                    labels: { color: '#e0e0e0' }
                }
            }
        }
    });
}

function updateAgentActivityChart() {
    const canvas = document.getElementById('agentActivityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.agentActivity) charts.agentActivity.destroy();
    
    charts.agentActivity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: summaryData.metrics.map(m => `Step ${m.step}`),
            datasets: [
                {
                    label: 'Customers',
                    data: summaryData.metrics.map(m => m.active_customers || 0),
                    backgroundColor: 'rgba(99, 102, 241, 0.7)',
                    borderColor: '#6366f1',
                    borderWidth: 1
                },
                {
                    label: 'Employees',
                    data: summaryData.metrics.map(m => m.active_employees || 0),
                    backgroundColor: 'rgba(236, 72, 153, 0.7)',
                    borderColor: '#ec4899',
                    borderWidth: 1
                }
            ]
        },
        options: getChartOptions('Agent Activity Over Time', true)
    });
}

function updateMessageDistributionChart() {
    const canvas = document.getElementById('messageDistributionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.messageDistribution) charts.messageDistribution.destroy();
    
    // Mock data - in real scenario, you'd have message type breakdown
    charts.messageDistribution = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Purchase', 'Inquiry', 'Assistance', 'Review', 'Other'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    '#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Message Type Distribution',
                    color: '#ffffff'
                },
                legend: {
                    position: 'right',
                    labels: { color: '#e0e0e0' }
                }
            }
        }
    });
}

function updateBookRevenueChart() {
    const canvas = document.getElementById('bookRevenueChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.bookRevenue) charts.bookRevenue.destroy();
    
    // Calculate revenue per book and get top 10
    let bookRevenueData = [];
    if (summaryData.books && summaryData.books.length > 0) {
        console.log('ðŸ“Š Processing book revenue data. Total books:', summaryData.books.length);
        
        bookRevenueData = summaryData.books
            .map(book => {
                const price = parseFloat(book.price) || 0;
                const sales = parseInt(book.sales) || 0;
                const revenue = price * sales;
                
                if (sales > 0) {
                    console.log(`  ðŸ“– ${book.title}: Rs. ${price.toFixed(2)} Ã— ${sales} = Rs. ${revenue.toFixed(2)}`);
                }
                
                return {
                    title: book.title || 'Unknown',
                    revenue: revenue
                };
            })
            .filter(book => book.revenue > 0)  // Only books with revenue
            .sort((a, b) => b.revenue - a.revenue)  // Sort by revenue descending
            .slice(0, 10);  // Top 10 books
        
        console.log('ðŸ“Š Books with revenue:', bookRevenueData.length);
    }
    
    // If no data, show placeholder
    if (bookRevenueData.length === 0) {
        console.warn('âš ï¸ No book revenue data available for chart');
        bookRevenueData = [{title: 'No Sales Data', revenue: 0}];
    }
    
    charts.bookRevenue = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: bookRevenueData.map(b => b.title),
            datasets: [{
                label: 'Revenue by Book',
                data: bookRevenueData.map(b => b.revenue),
                backgroundColor: 'rgba(79, 172, 254, 0.7)',
                borderColor: '#4facfe',
                borderWidth: 1
            }]
        },
        options: {
            ...getChartOptions('Top 10 Books by Revenue', false),
            scales: {
                x: {
                    ticks: {
                        color: '#e0e0e0',
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    ticks: { color: '#e0e0e0' }
                }
            }
        }
    });
}

function updateSatisfactionTrendChart() {
    const canvas = document.getElementById('satisfactionTrendChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    if (charts.satisfactionTrend) charts.satisfactionTrend.destroy();
    
    charts.satisfactionTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: summaryData.metrics.map(m => `Step ${m.step}`),
            datasets: [{
                label: 'Satisfaction',
                data: summaryData.metrics.map(m => parseFloat(m.avg_customer_satisfaction) || 0),
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Customer Satisfaction Trend')
    });
}

function getChartOptions(title, stacked = false) {
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: title,
                color: '#ffffff'
            },
            legend: {
                labels: { color: '#e0e0e0' }
            }
        },
        scales: {
            x: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(203, 213, 225, 0.1)' }
            },
            y: {
                ticks: { color: '#e0e0e0' },
                grid: { color: 'rgba(203, 213, 225, 0.1)' }
            }
        }
    };
    
    if (stacked) {
        options.scales.x.stacked = true;
        options.scales.y.stacked = true;
    }
    
    return options;
}

// ============================================
// ENHANCED EXPORT FUNCTIONS
// ============================================

function exportPDF() {
    if (!summaryData.metrics || summaryData.metrics.length === 0) {
        alert('No data to export');
        return;
    }
    
    try {
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        let yPos = 20;
        const pageHeight = 280;
        const leftMargin = 20;
        const rightMargin = 190;
        
        // Helper function to add new page if needed
        const checkPageBreak = (neededSpace) => {
            if (yPos + neededSpace > pageHeight) {
                doc.addPage();
                yPos = 20;
                return true;
            }
            return false;
        };
        
        // Cover Page
        doc.setFontSize(28);
        doc.setTextColor(99, 102, 241);
        doc.text('Bookstore Multi-Agent System', 105, yPos, { align: 'center' });
        
        yPos += 15;
        doc.setFontSize(20);
        doc.setTextColor(0, 0, 0);
        doc.text('Comprehensive Simulation Report', 105, yPos, { align: 'center' });
        
        yPos += 20;
        doc.setFontSize(12);
        doc.setTextColor(100, 100, 100);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 105, yPos, { align: 'center' });
        
        yPos += 40;
        doc.setDrawColor(99, 102, 241);
        doc.setLineWidth(0.5);
        doc.line(40, yPos, 170, yPos);
        
        // Key Metrics Summary on Cover
        yPos += 15;
        doc.setFontSize(14);
        doc.setTextColor(0, 0, 0);
        const latest = summaryData.metrics[summaryData.metrics.length - 1];
        
        doc.text(`Total Revenue: Rs. ${(parseFloat(latest.total_revenue) || 0).toFixed(2)}`, 105, yPos, { align: 'center' });
        yPos += 10;
        doc.text(`Books Sold: ${latest.books_sold || 0}`, 105, yPos, { align: 'center' });
        yPos += 10;
        doc.text(`Customer Satisfaction: ${(parseFloat(latest.avg_customer_satisfaction) || 0).toFixed(2)}`, 105, yPos, { align: 'center' });
        yPos += 10;
        doc.text(`Messages Processed: ${latest.messages_processed || 0}`, 105, yPos, { align: 'center' });
        
        // Page 2: Executive Summary
        doc.addPage();
        yPos = 20;
        
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Executive Summary', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        
        const summaryStats = [
            ['Simulation Steps', `${latest.step || 0}`],
            ['Total Revenue', `Rs. ${(parseFloat(latest.total_revenue) || 0).toFixed(2)}`],
            ['Books Sold', `${latest.books_sold || 0}`],
            ['Average Transaction Value', `Rs. ${latest.books_sold > 0 ? ((latest.total_revenue || 0) / latest.books_sold).toFixed(2) : '0.00'}`],
            ['Customer Satisfaction', `${(parseFloat(latest.avg_customer_satisfaction) || 0).toFixed(2)}`],
            ['Messages Processed', `${latest.messages_processed || 0}`],
            ['Active Customers', `${latest.active_customers || 0}`],
            ['Active Employees', `${latest.active_employees || 0}`],
            ['Total Books', `${latest.total_books || 0}`],
            ['Books in Stock', `${latest.books_in_stock || 0}`]
        ];
        
        summaryStats.forEach(([label, value]) => {
            doc.setFont(undefined, 'bold');
            doc.text(`${label}:`, leftMargin, yPos);
            doc.setFont(undefined, 'normal');
            doc.text(value, leftMargin + 70, yPos);
            yPos += 7;
        });
        
        // Agent Statistics
        checkPageBreak(30);
        yPos += 10;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Agent Statistics', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.text(`Total Customers: ${summaryData.customers.length}`, leftMargin, yPos);
        yPos += 7;
        doc.text(`Total Employees: ${summaryData.employees.length}`, leftMargin, yPos);
        yPos += 7;
        doc.text(`Total Books in Catalog: ${summaryData.books.length}`, leftMargin, yPos);
        yPos += 7;
        doc.text(`Total Transactions: ${summaryData.transactions.length}`, leftMargin, yPos);
        
        // Customer Details Table
        if (summaryData.customers.length > 0) {
            checkPageBreak(40);
            yPos += 15;
            doc.setFontSize(16);
            doc.setTextColor(99, 102, 241);
            doc.text('Customer Details (Top 10)', leftMargin, yPos);
            yPos += 8;
            
            doc.setFontSize(9);
            doc.setTextColor(0, 0, 0);
            doc.setFont(undefined, 'bold');
            doc.text('Name', leftMargin, yPos);
            doc.text('Budget', leftMargin + 50, yPos);
            doc.text('Books', leftMargin + 80, yPos);
            doc.text('Satisfaction', leftMargin + 110, yPos);
            doc.text('Loyalty', leftMargin + 150, yPos);
            yPos += 5;
            doc.setFont(undefined, 'normal');
            
            summaryData.customers.slice(0, 10).forEach((customer, index) => {
                if (checkPageBreak(7)) {
                    doc.setFont(undefined, 'bold');
                    doc.text('Name', leftMargin, yPos);
                    doc.text('Budget', leftMargin + 50, yPos);
                    doc.text('Books', leftMargin + 80, yPos);
                    doc.text('Satisfaction', leftMargin + 110, yPos);
                    doc.text('Loyalty', leftMargin + 150, yPos);
                    yPos += 5;
                    doc.setFont(undefined, 'normal');
                }
                
                doc.text((customer.name || 'Unknown').substring(0, 20), leftMargin, yPos);
                doc.text(`Rs. ${(customer.budget || 0).toFixed(0)}`, leftMargin + 50, yPos);
                doc.text(`${customer.books_purchased || 0}`, leftMargin + 80, yPos);
                doc.text(`${(customer.satisfaction || 0).toFixed(2)}`, leftMargin + 110, yPos);
                doc.text(`${customer.loyalty_level || 'New'}`, leftMargin + 150, yPos);
                yPos += 6;
            });
        }
        
        // Employee Details Table
        if (summaryData.employees.length > 0) {
            checkPageBreak(40);
            yPos += 15;
            doc.setFontSize(16);
            doc.setTextColor(99, 102, 241);
            doc.text('Employee Details (Top 10)', leftMargin, yPos);
            yPos += 8;
            
            doc.setFontSize(9);
            doc.setTextColor(0, 0, 0);
            doc.setFont(undefined, 'bold');
            doc.text('Name', leftMargin, yPos);
            doc.text('Role', leftMargin + 50, yPos);
            doc.text('Salary', leftMargin + 90, yPos);
            doc.text('Interactions', leftMargin + 130, yPos);
            doc.text('Performance', leftMargin + 165, yPos);
            yPos += 5;
            doc.setFont(undefined, 'normal');
            
            summaryData.employees.slice(0, 10).forEach((employee, index) => {
                if (checkPageBreak(7)) {
                    doc.setFont(undefined, 'bold');
                    doc.text('Name', leftMargin, yPos);
                    doc.text('Role', leftMargin + 50, yPos);
                    doc.text('Salary', leftMargin + 90, yPos);
                    doc.text('Interactions', leftMargin + 130, yPos);
                    doc.text('Performance', leftMargin + 165, yPos);
                    yPos += 5;
                    doc.setFont(undefined, 'normal');
                }
                
                doc.text((employee.name || 'Unknown').substring(0, 20), leftMargin, yPos);
                doc.text(`${employee.role || 'Staff'}`, leftMargin + 50, yPos);
                doc.text(`Rs. ${(employee.salary || 0).toFixed(0)}`, leftMargin + 90, yPos);
                doc.text(`${employee.interactions || 0}`, leftMargin + 130, yPos);
                doc.text(`${employee.performance || 'Good'}`, leftMargin + 165, yPos);
                yPos += 6;
            });
        }
        
        // Book Inventory Table
        if (summaryData.books.length > 0) {
            checkPageBreak(40);
            yPos += 15;
            doc.setFontSize(16);
            doc.setTextColor(99, 102, 241);
            doc.text('Book Inventory (Top 15)', leftMargin, yPos);
            yPos += 8;
            
            doc.setFontSize(9);
            doc.setTextColor(0, 0, 0);
            doc.setFont(undefined, 'bold');
            doc.text('Title', leftMargin, yPos);
            doc.text('Genre', leftMargin + 60, yPos);
            doc.text('Price', leftMargin + 95, yPos);
            doc.text('Stock', leftMargin + 120, yPos);
            doc.text('Sales', leftMargin + 145, yPos);
            doc.text('Rating', leftMargin + 170, yPos);
            yPos += 5;
            doc.setFont(undefined, 'normal');
            
            summaryData.books.slice(0, 15).forEach((book, index) => {
                if (checkPageBreak(7)) {
                    doc.setFont(undefined, 'bold');
                    doc.text('Title', leftMargin, yPos);
                    doc.text('Genre', leftMargin + 60, yPos);
                    doc.text('Price', leftMargin + 95, yPos);
                    doc.text('Stock', leftMargin + 120, yPos);
                    doc.text('Sales', leftMargin + 145, yPos);
                    doc.text('Rating', leftMargin + 170, yPos);
                    yPos += 5;
                    doc.setFont(undefined, 'normal');
                }
                
                doc.text((book.title || 'Unknown').substring(0, 25), leftMargin, yPos);
                doc.text(`${book.genre || 'N/A'}`, leftMargin + 60, yPos);
                doc.text(`Rs. ${(book.price || 0).toFixed(2)}`, leftMargin + 95, yPos);
                doc.text(`${book.stock || 0}`, leftMargin + 120, yPos);
                doc.text(`${book.sales || 0}`, leftMargin + 145, yPos);
                doc.text(`${(book.avg_rating || 0).toFixed(1)}`, leftMargin + 170, yPos);
                yPos += 6;
            });
        }
        
        // Top Performers
        doc.addPage();
        yPos = 20;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Top Performers', leftMargin, yPos);
        yPos += 10;
        
        // Top Books
        if (summaryData.books.length > 0) {
            doc.setFontSize(14);
            doc.setTextColor(0, 0, 0);
            doc.text('Top 5 Books by Sales', leftMargin, yPos);
            yPos += 7;
            
            doc.setFontSize(10);
            const topBooks = [...summaryData.books]
                .sort((a, b) => (b.sales || 0) - (a.sales || 0))
                .slice(0, 5);
            
            topBooks.forEach((book, index) => {
                doc.text(`${index + 1}. ${(book.title || 'Unknown').substring(0, 40)} - ${book.sales || 0} sales`, leftMargin + 5, yPos);
                yPos += 6;
            });
        }
        
        // Top Customers
        yPos += 10;
        if (summaryData.customers.length > 0) {
            doc.setFontSize(14);
            doc.setTextColor(0, 0, 0);
            doc.text('Top 5 Customers by Purchases', leftMargin, yPos);
            yPos += 7;
            
            doc.setFontSize(10);
            const topCustomers = [...summaryData.customers]
                .sort((a, b) => (b.books_purchased || 0) - (a.books_purchased || 0))
                .slice(0, 5);
            
            topCustomers.forEach((customer, index) => {
                doc.text(`${index + 1}. ${customer.name || 'Unknown'} - ${customer.books_purchased || 0} books`, leftMargin + 5, yPos);
                yPos += 6;
            });
        }
        
        // SWRL Rules Execution
        checkPageBreak(40);
        yPos += 15;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('SWRL Rules Execution Analysis', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        doc.text(`Total Rules Executed: ${summaryData.rules.length}`, leftMargin, yPos);
        yPos += 7;
        
        const ruleCounts = getRuleCounts();
        const uniqueRules = Object.keys(ruleCounts).length;
        doc.text(`Unique Rules: ${uniqueRules}`, leftMargin, yPos);
        yPos += 10;
        
        doc.text('Top Executed Rules:', leftMargin, yPos);
        yPos += 7;
        doc.setFontSize(10);
        
        Object.entries(ruleCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10)
            .forEach(([name, count]) => {
                if (checkPageBreak(6)) {
                    doc.text('Top Executed Rules (continued):', leftMargin, yPos);
                    yPos += 7;
                }
                doc.text(`  - ${name.replace(/_/g, ' ')}: ${count} executions`, leftMargin, yPos);
                yPos += 6;
            });
        
        // Ontology Statistics
        checkPageBreak(30);
        yPos += 15;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Ontology Statistics', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(11);
        doc.setTextColor(0, 0, 0);
        const totalClasses = (latest.active_customers || 0) + (latest.active_employees || 0) + (latest.total_books || 0);
        doc.text(`Total Classes Instantiated: ${totalClasses}`, leftMargin, yPos);
        yPos += 7;
        doc.text(`Properties Used: ${summaryData.rules.length}`, leftMargin, yPos);
        yPos += 7;
        doc.text(`Relationships Created: ${summaryData.transactions.length}`, leftMargin, yPos);
        
        // Charts - Add chart images
        doc.addPage();
        yPos = 20;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Performance Charts', leftMargin, yPos);
        yPos += 10;
        
        // Add chart canvases as images
        try {
            // Revenue Chart
            const revenueCanvas = document.getElementById('summaryRevenueChart');
            if (revenueCanvas && charts.revenue) {
                const revenueImg = revenueCanvas.toDataURL('image/png');
                doc.addImage(revenueImg, 'PNG', leftMargin, yPos, 170, 80);
                yPos += 90;
            }
            
            // Check page break
            if (yPos > 180) {
                doc.addPage();
                yPos = 20;
            }
            
            // Rules Distribution Chart
            const rulesCanvas = document.getElementById('summaryRulesChart');
            if (rulesCanvas && charts.rules) {
                const rulesImg = rulesCanvas.toDataURL('image/png');
                doc.addImage(rulesImg, 'PNG', leftMargin, yPos, 170, 80);
                yPos += 90;
            }
            
            // Add new page for additional charts
            doc.addPage();
            yPos = 20;
            
            // Agent Activity Chart
            const agentCanvas = document.getElementById('agentActivityChart');
            if (agentCanvas && charts.agentActivity) {
                const agentImg = agentCanvas.toDataURL('image/png');
                doc.addImage(agentImg, 'PNG', leftMargin, yPos, 170, 80);
                yPos += 90;
            }
            
            if (yPos > 180) {
                doc.addPage();
                yPos = 20;
            }
            
            // Book Revenue Chart
            const bookCanvas = document.getElementById('bookRevenueChart');
            if (bookCanvas && charts.bookRevenue) {
                const bookImg = bookCanvas.toDataURL('image/png');
                doc.addImage(bookImg, 'PNG', leftMargin, yPos, 170, 80);
            }
        } catch (chartError) {
            console.warn('Could not add charts to PDF:', chartError);
        }
        
        // Simulation Configuration
        doc.addPage();
        yPos = 20;
        doc.setFontSize(18);
        doc.setTextColor(99, 102, 241);
        doc.text('Simulation Configuration', leftMargin, yPos);
        yPos += 10;
        
        doc.setFontSize(10);
        doc.setTextColor(0, 0, 0);
        const config = {
            'Simulation Steps': latest.step || 0,
            'Customers': latest.active_customers || 0,
            'Employees': latest.active_employees || 0,
            'Books': latest.total_books || 0,
            'Rules Enabled': uniqueRules,
            'Generated': new Date().toISOString(),
            'Status': 'Complete'
        };
        
        Object.entries(config).forEach(([key, value]) => {
            doc.setFont(undefined, 'bold');
            doc.text(`${key}:`, leftMargin, yPos);
            doc.setFont(undefined, 'normal');
            doc.text(`${value}`, leftMargin + 60, yPos);
            yPos += 7;
        });
        
        // Footer on all pages
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(10);
            doc.setTextColor(150, 150, 150);
            doc.text(`Bookstore MAS Report - Page ${i} of ${pageCount}`, 105, 290, { align: 'center' });
        }
        
        // Save PDF
        doc.save('bookstore_comprehensive_report.pdf');
        console.log('PDF exported successfully with', pageCount, 'pages');
    } catch (error) {
        console.error('Export PDF failed:', error);
        alert('Failed to export PDF: ' + error.message);
    }
}

async function exportJSON() {
    try {
        const exportData = {
            generated: new Date().toISOString(),
            metrics: summaryData.metrics,
            transactions: summaryData.transactions,
            rules: summaryData.rules,
            customers: summaryData.customers,
            employees: summaryData.employees,
            books: summaryData.books
        };
        
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        downloadBlob(blob, 'bookstore_complete_data.json', 'application/json');
    } catch (error) {
        console.error('Export JSON failed:', error);
        alert('Failed to export JSON.');
    }
}

async function exportCSV() {
    try {
        const latest = summaryData.metrics[summaryData.metrics.length - 1];
        
        const csvRows = [
            ['Metric', 'Value'],
            ['Total Revenue', `Rs. ${(parseFloat(latest.total_revenue) || 0).toFixed(2)}`],
            ['Books Sold', latest.books_sold || 0],
            ['Customer Satisfaction', (parseFloat(latest.avg_customer_satisfaction) || 0).toFixed(2)],
            ['Messages Processed', latest.messages_processed || 0],
            ['Simulation Steps', latest.step || 0],
            ['Active Customers', latest.active_customers || 0],
            ['Active Employees', latest.active_employees || 0],
            ['Total Books', latest.total_books || 0]
        ];
        
        const csvContent = csvRows.map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        downloadBlob(blob, 'bookstore_summary.csv', 'text/csv');
    } catch (error) {
        console.error('Export CSV failed:', error);
        alert('Failed to export CSV.');
    }
}

function exportExcel() {
    if (!summaryData.metrics || summaryData.metrics.length === 0) {
        alert('No data to export');
        return;
    }
    
    try {
        const wb = XLSX.utils.book_new();
        
        // Summary Sheet
        const summaryWS = XLSX.utils.json_to_sheet([{
            'Total Revenue': `Rs. ${(parseFloat(summaryData.metrics[summaryData.metrics.length - 1].total_revenue) || 0).toFixed(2)}`,
            'Books Sold': summaryData.metrics[summaryData.metrics.length - 1].books_sold || 0,
            'Customer Satisfaction': (parseFloat(summaryData.metrics[summaryData.metrics.length - 1].avg_customer_satisfaction) || 0).toFixed(2),
            'Messages Processed': summaryData.metrics[summaryData.metrics.length - 1].messages_processed || 0,
            'Total Customers': summaryData.customers.length,
            'Total Employees': summaryData.employees.length,
            'Total Books': summaryData.books.length
        }]);
        XLSX.utils.book_append_sheet(wb, summaryWS, 'Summary');
        
        // Customers Sheet
        if (summaryData.customers.length > 0) {
            const customersWS = XLSX.utils.json_to_sheet(summaryData.customers);
            XLSX.utils.book_append_sheet(wb, customersWS, 'Customers');
        }
        
        // Employees Sheet
        if (summaryData.employees.length > 0) {
            const employeesWS = XLSX.utils.json_to_sheet(summaryData.employees);
            XLSX.utils.book_append_sheet(wb, employeesWS, 'Employees');
        }
        
        // Books Sheet
        if (summaryData.books.length > 0) {
            const booksWS = XLSX.utils.json_to_sheet(summaryData.books);
            XLSX.utils.book_append_sheet(wb, booksWS, 'Books');
        }
        
        // Metrics Sheet
        const metricsWS = XLSX.utils.json_to_sheet(summaryData.metrics);
        XLSX.utils.book_append_sheet(wb, metricsWS, 'Metrics');
        
        // Rules Sheet
        if (summaryData.rules.length > 0) {
            const rulesWS = XLSX.utils.json_to_sheet(summaryData.rules);
            XLSX.utils.book_append_sheet(wb, rulesWS, 'Rules');
        }
        
        // Transactions Sheet
        if (summaryData.transactions.length > 0) {
            const transWS = XLSX.utils.json_to_sheet(summaryData.transactions);
            XLSX.utils.book_append_sheet(wb, transWS, 'Transactions');
        }
        
        XLSX.writeFile(wb, 'bookstore_comprehensive_report.xlsx');
    } catch (error) {
        console.error('Export Excel failed:', error);
        alert('Failed to export Excel.');
    }
}

function downloadBlob(blob, filename, mimeType) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function getRuleCounts() {
    const ruleCounts = {};
    (summaryData.rules || []).forEach(rule => {
        const ruleName = rule.rule_name || 'Unknown';
        ruleCounts[ruleName] = (ruleCounts[ruleName] || 0) + 1;
    });
    return ruleCounts;
}

function clearSummaryDisplay() {
    updateStatElement('final-revenue', '$0.00');
    updateStatElement('final-books-sold', '0');
    updateStatElement('final-satisfaction', '0.00');
    updateStatElement('final-messages', '0');
    
    const tables = ['performanceMetrics', 'rulesStatistics', 'ontologyDetailsTable', 
                    'customerDetailsTable', 'employeeDetailsTable', 'bookDetailsTable',
                    'topBooksTable', 'topCustomersTable', 'rulesExecutionTable'];
    
    tables.forEach(tableId => {
        const table = document.getElementById(tableId);
        if (table) {
            table.innerHTML = '<tr><td colspan="10" style="text-align: center;">No data available</td></tr>';
        }
    });
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

async function loadExistingData() {
    try {
        console.log('Loading existing summary data...');
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data) {
            console.log('âœ“ Found existing simulation data');
            
            summaryData.metrics = data.metrics || [];
            summaryData.transactions = data.transactions || [];
            summaryData.rules = data.rules || [];
            summaryData.agents = data.agents || {};
            
            if (summaryData.metrics.length > 0) {
                loadAgentDetails();
                updateComprehensiveSummary();
                console.log('âœ“ Comprehensive summary fully loaded');
            }
        } else {
            console.log('No previous simulation data found');
        }
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

function refreshSummary() {
    console.log('Refreshing comprehensive summary...');
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

// Event Listeners for Search and Filter
document.addEventListener('DOMContentLoaded', () => {
    console.log('Summary page loaded - initializing comprehensive view...');
    
    // Load theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const themeButton = document.querySelector('.theme-toggle');
    if (themeButton) {
        themeButton.textContent = savedTheme === 'dark' ? 'â˜€ï¸' : 'ðŸŒ™';
    }
    
    // Load existing data
    loadExistingData();
    
    // Setup search listeners
    const customerSearch = document.getElementById('customerSearchInput');
    if (customerSearch) {
        customerSearch.addEventListener('input', () => {
            pagination.customers.page = 1;
            updateCustomerTable();
        });
    }
    
    const employeeSearch = document.getElementById('employeeSearchInput');
    if (employeeSearch) {
        employeeSearch.addEventListener('input', () => {
            pagination.employees.page = 1;
            updateEmployeeTable();
        });
    }
    
    const bookSearch = document.getElementById('bookSearchInput');
    if (bookSearch) {
        bookSearch.addEventListener('input', () => {
            pagination.books.page = 1;
            updateBookTable();
        });
    }
    
    const genreFilter = document.getElementById('genreFilter');
    if (genreFilter) {
        genreFilter.addEventListener('change', () => {
            pagination.books.page = 1;
            updateBookTable();
        });
    }
});


