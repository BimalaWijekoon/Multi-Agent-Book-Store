// ============================================
// GRAPHS PAGE - Interactive Analytics
// Complete Rebuild with Clean Data Persistence
// ============================================

// Initialize WebSocket
const socket = io();

// Global state - all chart instances
let charts = {};

// Global state - simulation data
let simulationData = {
    metrics: [],
    messages: [],
    rules: [],
    transactions: [],
    agents: {}
};

// ============================================
// WEBSOCKET EVENT HANDLERS
// ============================================

socket.on('connect', () => {
    console.log('✓ Graphs page connected to WebSocket');
});

socket.on('simulation_started', () => {
    console.log('✓ New simulation started - clearing old graph data');
    
    // Clear all data
    simulationData = {
        metrics: [],
        messages: [],
        rules: [],
        transactions: [],
        agents: {}
    };
    
    // Reset all charts
    Object.values(charts).forEach(chart => {
        if (chart && chart.data) {
            chart.data.labels = [];
            chart.data.datasets.forEach(dataset => {
                dataset.data = [];
            });
            chart.update();
        }
    });
    
    // Clear all stats
    clearAllStats();
});

socket.on('metrics_update', (metrics) => {
    simulationData.metrics.push(metrics);
    updateAllCharts();
});

socket.on('message_logged', (message) => {
    simulationData.messages.push(message);
    // Update message-related charts
    updateMessageCharts();
});

socket.on('rule_executed', (rule) => {
    simulationData.rules.push(rule);
    // Update rule-related charts
    updateRulesCharts();
});

socket.on('transaction_logged', (transaction) => {
    simulationData.transactions.push(transaction);
    // Update revenue charts
    updateRevenueCharts();
});

socket.on('agents_initialized', (agents) => {
    simulationData.agents = agents;
    updateAgentCharts();
    updateSatisfactionCharts();
    updateInventoryCharts();
});

socket.on('simulation_complete', (summary) => {
    console.log('✓ Simulation complete - final graph update');
    updateAllCharts();
});

// ============================================
// CHART INITIALIZATION
// ============================================

function initializeAllCharts() {
    console.log('Initializing all charts...');
    
    // Revenue Charts
    initRevenueCharts();
    
    // Agent Charts
    initAgentCharts();
    
    // Rules Charts
    initRulesCharts();
    
    // Message Charts
    initMessageCharts();
    
    // Satisfaction Charts
    initSatisfactionCharts();
    
    // Inventory Charts
    initInventoryCharts();
    
    console.log('✓ All charts initialized');
}

function initRevenueCharts() {
    // Cumulative Revenue Chart
    charts.revenue = new Chart(document.getElementById('revenueChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cumulative Revenue',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getCommonChartOptions('Revenue Over Time', 'Revenue ($)')
    });
    
    // Revenue per Step Chart
    charts.revenueByStep = new Chart(document.getElementById('revenueByStepChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Revenue per Step',
                data: [],
                backgroundColor: 'rgba(99, 102, 241, 0.8)',
            }]
        },
        options: getCommonChartOptions('Revenue per Step', 'Revenue ($)')
    });
}

function initAgentCharts() {
    // Agent Activity Chart
    charts.agentActivity = new Chart(document.getElementById('agentActivityChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Active Customers',
                    data: [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Active Employees',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Total Books',
                    data: [],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: getCommonChartOptions('Agent Activity Over Time', 'Count')
    });
    
    // Book Stock Chart
    charts.bookStock = new Chart(document.getElementById('bookStockChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Books in Stock',
                data: [],
                backgroundColor: 'rgba(16, 185, 129, 0.8)',
            }]
        },
        options: getCommonChartOptions('Inventory Levels Over Time', 'Stock')
    });
}

function initRulesCharts() {
    // Rules Execution Doughnut Chart
    charts.rulesExecution = new Chart(document.getElementById('rulesExecutionChart').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#3b82f6']
            }]
        },
        options: getDoughnutChartOptions()
    });
    
    // Rules Timeline Chart
    charts.rulesTimeline = new Chart(document.getElementById('rulesTimelineChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Rules Fired per Step',
                data: [],
                backgroundColor: 'rgba(139, 92, 246, 0.8)',
            }]
        },
        options: getCommonChartOptions('Rules Execution Timeline', 'Count')
    });
}

function initMessageCharts() {
    // Message Throughput Chart
    charts.messageThroughput = new Chart(document.getElementById('messageThroughputChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Messages Processed',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getCommonChartOptions('Message Throughput', 'Messages')
    });
    
    // Message Types Doughnut Chart
    charts.messageTypes = new Chart(document.getElementById('messageTypesChart').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
            }]
        },
        options: getDoughnutChartOptions()
    });
}

function initSatisfactionCharts() {
    // Satisfaction Trend Chart
    charts.satisfaction = new Chart(document.getElementById('satisfactionChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Average Satisfaction',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getCommonChartOptions('Customer Satisfaction Trend', 'Satisfaction (0-1)')
    });
    
    // Satisfaction Distribution Doughnut Chart
    charts.satisfactionDistribution = new Chart(document.getElementById('satisfactionDistributionChart').getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['😢 Very Low (0.0-0.2)', '😐 Low (0.2-0.4)', '😊 Medium (0.4-0.6)', '😀 High (0.6-0.8)', '🤩 Very High (0.8-1.0)'],
            datasets: [{
                data: [0, 0, 0, 0, 0],
                backgroundColor: ['#ef4444', '#f59e0b', '#fbbf24', '#10b981', '#059669']
            }]
        },
        options: getDoughnutChartOptions()
    });
}

function initInventoryCharts() {
    // Inventory Level Chart
    charts.inventory = new Chart(document.getElementById('inventoryChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Stock',
                data: [],
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.2)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getCommonChartOptions('Inventory Levels', 'Stock')
    });
    
    // Inventory vs Sales Chart
    charts.inventoryHistory = new Chart(document.getElementById('inventoryHistoryChart').getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Books in Stock',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Books Sold',
                    data: [],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: getCommonChartOptions('Inventory vs Sales', 'Count')
    });
}

// ============================================
// CHART OPTIONS HELPERS
// ============================================

function getCommonChartOptions(title, yAxisLabel) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    color: '#e0e0e0',
                    font: {
                        family: 'Inter, sans-serif',
                        size: 12
                    }
                }
            },
            title: {
                display: true,
                text: title,
                color: '#ffffff',
                font: {
                    size: 16,
                    weight: 'bold',
                    family: 'Inter, sans-serif'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(18, 18, 26, 0.95)',
                borderColor: 'rgba(139, 92, 246, 0.8)',
                borderWidth: 1,
                titleColor: '#ffffff',
                bodyColor: '#e0e0e0',
                padding: 12
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(203, 213, 225, 0.1)'
                },
                ticks: {
                    color: '#e0e0e0'
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: yAxisLabel,
                    color: '#e0e0e0'
                },
                grid: {
                    color: 'rgba(203, 213, 225, 0.1)'
                },
                ticks: {
                    color: '#e0e0e0'
                }
            }
        }
    };
}

function getDoughnutChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    color: '#e0e0e0',
                    font: {
                        family: 'Inter, sans-serif',
                        size: 12
                    },
                    padding: 15,
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(18, 18, 26, 0.95)',
                borderColor: 'rgba(139, 92, 246, 0.8)',
                borderWidth: 1,
                titleColor: '#ffffff',
                bodyColor: '#e0e0e0',
                padding: 12,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
}

// ============================================
// CHART UPDATE FUNCTIONS
// ============================================

function updateAllCharts() {
    updateRevenueCharts();
    updateAgentCharts();
    updateRulesCharts();
    updateMessageCharts();
    updateSatisfactionCharts();
    updateInventoryCharts();
    updateStats();
}

function updateRevenueCharts() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const labels = simulationData.metrics.map(m => `Step ${m.step}`);
    const revenues = simulationData.metrics.map(m => parseFloat(m.total_revenue) || 0);
    
    // Update cumulative revenue
    charts.revenue.data.labels = labels;
    charts.revenue.data.datasets[0].data = revenues;
    charts.revenue.update();
    
    // Calculate revenue per step
    const revenuePerStep = revenues.map((val, idx) => {
        if (idx === 0) return val;
        return val - revenues[idx - 1];
    });
    
    charts.revenueByStep.data.labels = labels;
    charts.revenueByStep.data.datasets[0].data = revenuePerStep;
    charts.revenueByStep.update();
}

function updateAgentCharts() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const labels = simulationData.metrics.map(m => `Step ${m.step}`);
    
    // Update agent activity chart
    charts.agentActivity.data.labels = labels;
    charts.agentActivity.data.datasets[0].data = simulationData.metrics.map(m => parseInt(m.active_customers) || 0);
    charts.agentActivity.data.datasets[1].data = simulationData.metrics.map(m => parseInt(m.active_employees) || 0);
    charts.agentActivity.data.datasets[2].data = simulationData.metrics.map(m => parseInt(m.total_books) || 0);
    charts.agentActivity.update();
    
    // Update book stock chart
    charts.bookStock.data.labels = labels;
    charts.bookStock.data.datasets[0].data = simulationData.metrics.map(m => parseInt(m.books_in_stock) || 0);
    charts.bookStock.update();
}

function updateRulesCharts() {
    if (!simulationData.rules || simulationData.rules.length === 0) return;
    
    // Count rules by type
    const ruleCounts = {};
    simulationData.rules.forEach(rule => {
        const ruleName = rule.rule_name || 'Unknown';
        ruleCounts[ruleName] = (ruleCounts[ruleName] || 0) + 1;
    });
    
    // Update rules execution doughnut
    const labels = Object.keys(ruleCounts);
    const values = Object.values(ruleCounts);
    charts.rulesExecution.data.labels = labels;
    charts.rulesExecution.data.datasets[0].data = values;
    charts.rulesExecution.update();
    
    // Count rules by step for timeline
    const rulesByStep = {};
    simulationData.rules.forEach(rule => {
        const step = rule.step;
        rulesByStep[step] = (rulesByStep[step] || 0) + 1;
    });
    
    const steps = Object.keys(rulesByStep).sort((a, b) => a - b);
    charts.rulesTimeline.data.labels = steps.map(s => `Step ${s}`);
    charts.rulesTimeline.data.datasets[0].data = steps.map(s => rulesByStep[s]);
    charts.rulesTimeline.update();
}

function updateMessageCharts() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const labels = simulationData.metrics.map(m => `Step ${m.step}`);
    
    // Update message throughput
    charts.messageThroughput.data.labels = labels;
    charts.messageThroughput.data.datasets[0].data = simulationData.metrics.map(m => parseInt(m.messages_processed) || 0);
    charts.messageThroughput.update();
    
    // Update message types doughnut
    if (simulationData.messages && simulationData.messages.length > 0) {
        const typeCounts = {};
        simulationData.messages.forEach(msg => {
            const msgType = msg.type || 'Unknown';
            typeCounts[msgType] = (typeCounts[msgType] || 0) + 1;
        });
        
        const msgLabels = Object.keys(typeCounts);
        const msgValues = Object.values(typeCounts);
        charts.messageTypes.data.labels = msgLabels;
        charts.messageTypes.data.datasets[0].data = msgValues;
        charts.messageTypes.update();
    }
}

function updateSatisfactionCharts() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const labels = simulationData.metrics.map(m => `Step ${m.step}`);
    const satisfactionData = simulationData.metrics.map(m => parseFloat(m.avg_customer_satisfaction) || 0);
    
    // Update satisfaction trend
    charts.satisfaction.data.labels = labels;
    charts.satisfaction.data.datasets[0].data = satisfactionData;
    charts.satisfaction.update();
    
    // Update satisfaction distribution
    if (simulationData.agents && simulationData.agents.customers) {
        const distribution = [0, 0, 0, 0, 0]; // 5 buckets
        
        simulationData.agents.customers.forEach(customer => {
            const satisfaction = parseFloat(customer.satisfaction) || 0;
            const bucket = Math.min(Math.floor(satisfaction * 5), 4);
            distribution[bucket]++;
        });
        
        charts.satisfactionDistribution.data.datasets[0].data = distribution;
        charts.satisfactionDistribution.update();
    }
}

function updateInventoryCharts() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const labels = simulationData.metrics.map(m => `Step ${m.step}`);
    
    // Update inventory level
    charts.inventory.data.labels = labels;
    charts.inventory.data.datasets[0].data = simulationData.metrics.map(m => parseInt(m.books_in_stock) || 0);
    charts.inventory.update();
    
    // Update inventory vs sales
    charts.inventoryHistory.data.labels = labels;
    charts.inventoryHistory.data.datasets[0].data = simulationData.metrics.map(m => parseInt(m.books_in_stock) || 0);
    charts.inventoryHistory.data.datasets[1].data = simulationData.metrics.map(m => parseInt(m.books_sold) || 0);
    charts.inventoryHistory.update();
}

// ============================================
// STATS UPDATE FUNCTIONS
// ============================================

function updateStats() {
    if (!simulationData.metrics || simulationData.metrics.length === 0) return;
    
    const latest = simulationData.metrics[simulationData.metrics.length - 1];
    
    // Update revenue stats
    const totalRevenue = parseFloat(latest.total_revenue) || 0;
    const avgTransaction = simulationData.transactions.length > 0 
        ? (totalRevenue / simulationData.transactions.length) 
        : 0;
    
    updateStatElement('total-revenue', `$${totalRevenue.toFixed(2)}`);
    updateStatElement('avg-transaction', `$${avgTransaction.toFixed(2)}`);
    
    // Update agent stats
    updateStatElement('active-customers-count', latest.active_customers || 0);
    updateStatElement('active-employees-count', latest.active_employees || 0);
    updateStatElement('total-books-count', latest.total_books || 0);
    
    // Update rules stats
    updateStatElement('total-rules-executed', simulationData.rules.length);
    
    if (simulationData.rules.length > 0) {
        const ruleCounts = {};
        simulationData.rules.forEach(rule => {
            const ruleName = rule.rule_name || 'Unknown';
            ruleCounts[ruleName] = (ruleCounts[ruleName] || 0) + 1;
        });
        const mostFired = Object.entries(ruleCounts).sort((a, b) => b[1] - a[1])[0];
        updateStatElement('most-fired-rule', mostFired[0].replace(/_/g, ' '));
    }
    
    // Update message stats
    updateStatElement('total-messages', simulationData.messages.length);
    updateStatElement('processed-messages', latest.messages_processed || 0);
    
    const avgMsgRate = simulationData.metrics.length > 0 
        ? (simulationData.messages.length / simulationData.metrics.length) 
        : 0;
    updateStatElement('avg-msg-rate', avgMsgRate.toFixed(1));
    
    // Update satisfaction stats
    const avgSatisfaction = parseFloat(latest.avg_customer_satisfaction) || 0;
    updateStatElement('avg-satisfaction', avgSatisfaction.toFixed(2));
    
    // Update inventory stats
    updateStatElement('total-stock', latest.books_in_stock || 0);
    updateStatElement('books-sold-total', latest.books_sold || 0);
    
    // Calculate low stock items
    if (simulationData.agents && simulationData.agents.books) {
        const lowStockCount = simulationData.agents.books.filter(b => (b.stock || 0) < 5).length;
        updateStatElement('low-stock-count', lowStockCount);
    }
}

function updateStatElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function clearAllStats() {
    // Clear all stat displays
    const statIds = [
        'total-revenue', 'avg-transaction',
        'active-customers-count', 'active-employees-count', 'total-books-count',
        'total-rules-executed', 'most-fired-rule',
        'total-messages', 'processed-messages', 'avg-msg-rate',
        'avg-satisfaction',
        'total-stock', 'books-sold-total', 'low-stock-count'
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
        
        // Update charts for this tab (helps with rendering)
        if (charts[tabName]) {
            charts[tabName].update();
        }
    });
});

// ============================================
// DATA PERSISTENCE - LOAD FROM SERVER
// ============================================

async function loadExistingData() {
    try {
        console.log('Loading existing simulation data from server...');
        const response = await fetch('/api/get_current_data');
        const data = await response.json();
        
        if (data.has_data && data.metrics && data.metrics.length > 0) {
            console.log('✓ Found existing simulation data');
            
            // Restore all data
            simulationData.metrics = data.metrics || [];
            simulationData.messages = data.messages || [];
            simulationData.rules = data.rules || [];
            simulationData.transactions = data.transactions || [];
            simulationData.agents = data.agents || {};
            
            // Update all charts with restored data
            updateAllCharts();
            
            console.log('✓ Graphs page fully restored from server');
        } else {
            console.log('No previous simulation data found');
        }
    } catch (error) {
        console.error('Error loading existing data:', error);
    }
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function refreshGraphs() {
    console.log('Refreshing graphs...');
    loadExistingData();
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    const themeButton = document.querySelector('.theme-toggle');
    if (themeButton) {
        themeButton.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);
const themeButton = document.querySelector('.theme-toggle');
if (themeButton) {
    themeButton.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Graphs page loaded - initializing...');
    
    // Initialize all charts first
    initializeAllCharts();
    
    // Then try to load existing data
    loadExistingData();
});
