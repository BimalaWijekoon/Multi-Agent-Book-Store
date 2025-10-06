// ============================================
// ONTOLOGY VISUALIZATION PAGE
// Interactive Graph using Cytoscape.js
// ============================================

let cy = null;
let ontologyData = null;

// ============================================
// INITIALIZATION
// ============================================

let retryCount = 0;
const MAX_RETRIES = 3;

document.addEventListener('DOMContentLoaded', () => {
    loadOntologyData();
    setupSearchFilter();
});

// ============================================
// DATA LOADING
// ============================================

async function loadOntologyData() {
    // Only show loading indicator on first attempt
    if (retryCount === 0) {
        showLoadingIndicator();
    }
    
    try {
        const response = await fetch('/api/get_ontology');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        ontologyData = await response.json();
        
        if (ontologyData.error) {
            console.error('Error loading ontology:', ontologyData.error);
            
            // Retry a few times if it's a temporary issue
            if (retryCount < MAX_RETRIES) {
                retryCount++;
                console.log(`Retrying... attempt ${retryCount} of ${MAX_RETRIES}`);
                setTimeout(() => loadOntologyData(), 1000);
                return;
            }
            
            showNoDataMessage(ontologyData.error);
            return;
        }
        
        // Check if we have valid data
        if (!ontologyData.classes || !ontologyData.relations) {
            showNoDataMessage('No ontology data available. Please start a simulation first.');
            return;
        }
        
        // Reset retry count on success
        retryCount = 0;
        
        updateStatistics();
        populateDetailsLists();
        initializeGraph();
    } catch (error) {
        console.error('Error loading ontology:', error);
        
        // Retry on network errors
        if (retryCount < MAX_RETRIES) {
            retryCount++;
            console.log(`Retrying... attempt ${retryCount} of ${MAX_RETRIES}`);
            setTimeout(() => loadOntologyData(), 1000);
            return;
        }
        
        showNoDataMessage('Failed to load ontology data. Please ensure a simulation is running.');
    }
}

function showNoDataMessage(message) {
    // Update statistics to show zeros
    document.getElementById('class-count').textContent = '0';
    document.getElementById('property-count').textContent = '0';
    document.getElementById('individual-count').textContent = '0';
    document.getElementById('relation-count').textContent = '0';
    
    // Show friendly message in graph area
    const graphContainer = document.getElementById('ontology-graph');
    graphContainer.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 1rem; padding: 2rem; text-align: center;">
            <div style="font-size: 4rem; opacity: 0.3;">📊</div>
            <h3 style="color: var(--text-primary); margin: 0;">No Ontology Data Available</h3>
            <p style="color: var(--text-secondary); margin: 0; max-width: 400px;">${message}</p>
            <p style="color: var(--text-secondary); margin: 0; font-size: 0.875rem;">Go to the <a href="/" style="color: var(--primary-color); text-decoration: none; font-weight: 600;">Dashboard</a> to start a simulation.</p>
        </div>
    `;
    
    // Clear lists
    document.getElementById('classes-list').innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem;">No classes available</div>';
    document.getElementById('object-properties-list').innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem;">No properties available</div>';
    document.getElementById('data-properties-list').innerHTML = '<div style="padding: 1rem; text-align: center; color: var(--text-secondary); font-size: 0.875rem;">No properties available</div>';
}

function showLoadingIndicator() {
    const graphContainer = document.getElementById('ontology-graph');
    if (!graphContainer) {
        console.error('Graph container not found!');
        return;
    }
    
    // Clear any existing content
    graphContainer.innerHTML = '';
    
    // Create loading div
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'ontology-loading';
    loadingDiv.style.cssText = 'display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 1rem;';
    loadingDiv.innerHTML = `
        <div class="loading-spinner" style="width: 48px; height: 48px; border: 4px solid var(--border-color); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite;"></div>
        <p style="color: var(--text-secondary); margin: 0;">Loading ontology data...</p>
    `;
    
    graphContainer.appendChild(loadingDiv);
    
    // Add spin animation if not already present
    if (!document.getElementById('spinner-style')) {
        const style = document.createElement('style');
        style.id = 'spinner-style';
        style.textContent = '@keyframes spin { to { transform: rotate(360deg); } }';
        document.head.appendChild(style);
    }
}

// ============================================
// STATISTICS UPDATE
// ============================================

function updateStatistics() {
    document.getElementById('class-count').textContent = ontologyData.classes.length;
    document.getElementById('property-count').textContent = 
        ontologyData.object_properties.length + ontologyData.data_properties.length;
    document.getElementById('individual-count').textContent = ontologyData.individuals.length;
    document.getElementById('relation-count').textContent = ontologyData.relations.length;
}

// ============================================
// DETAILS LISTS POPULATION
// ============================================

function populateDetailsLists() {
    // Classes list
    const classList = document.getElementById('classes-list');
    classList.innerHTML = ontologyData.classes.map(cls => `
        <div class="info-item" onclick="highlightNode('${cls.id}')" title="${cls.comment || cls.label}">
            ${cls.label}
        </div>
    `).join('');
    
    // Object properties list
    const objPropList = document.getElementById('object-properties-list');
    objPropList.innerHTML = ontologyData.object_properties.map(prop => `
        <div class="info-item" onclick="highlightNode('${prop.id}')" title="${prop.comment || prop.label}">
            ${prop.label}
        </div>
    `).join('');
    
    // Data properties list
    const dataPropList = document.getElementById('data-properties-list');
    dataPropList.innerHTML = ontologyData.data_properties.map(prop => `
        <div class="info-item" onclick="highlightNode('${prop.id}')" title="${prop.comment || prop.label}">
            ${prop.label}
        </div>
    `).join('');
}

// ============================================
// GRAPH INITIALIZATION
// ============================================

function initializeGraph() {
    const elements = buildGraphElements();
    
    console.log('Initializing graph with elements:', {
        nodeCount: elements.nodes.length,
        edgeCount: elements.edges.length,
        nodes: elements.nodes.slice(0, 5), // First 5 nodes for debugging
        edges: elements.edges.slice(0, 5)  // First 5 edges for debugging
    });
    
    if (elements.nodes.length === 0) {
        console.warn('No nodes to display in graph!');
        showNoDataMessage('Ontology data loaded but contains no displayable elements.');
        return;
    }
    
    // Get the container element
    const container = document.getElementById('ontology-graph');
    if (!container) {
        console.error('Graph container element not found!');
        return;
    }
    
    // Clear any existing content (loading indicator, etc.)
    container.innerHTML = '';
    
    // Ensure container has proper dimensions
    container.style.width = '100%';
    container.style.height = '100%';
    
    try {
        cy = cytoscape({
            container: container,
            
            elements: elements,
        
        style: [
            // Node styles
            {
                selector: 'node',
                style: {
                    'background-color': '#667eea',
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '14px',
                    'font-weight': 'bold',
                    'width': '80px',
                    'height': '80px',
                    'border-width': 4,
                    'border-color': '#4c51bf',
                    'text-outline-width': 2,
                    'text-outline-color': '#667eea',
                    'text-wrap': 'wrap',
                    'text-max-width': '100px',
                    'transition-property': 'background-color, border-color, width, height',
                    'transition-duration': '0.3s'
                }
            },
            {
                selector: 'node[type="class"]',
                style: {
                    'background-color': '#667eea',
                    'border-color': '#4c51bf',
                    'shape': 'ellipse',
                    'width': '100px',
                    'height': '100px'
                }
            },
            {
                selector: 'node[type="object_property"]',
                style: {
                    'background-color': '#f093fb',
                    'border-color': '#c471ed',
                    'shape': 'diamond',
                    'width': '70px',
                    'height': '70px',
                    'text-outline-color': '#f093fb'
                }
            },
            {
                selector: 'node[type="data_property"]',
                style: {
                    'background-color': '#fbbf24',
                    'border-color': '#f59e0b',
                    'shape': 'rectangle',
                    'width': '90px',
                    'height': '50px',
                    'text-outline-color': '#fbbf24'
                }
            },
            {
                selector: 'node[type="individual"]',
                style: {
                    'background-color': '#43e97b',
                    'border-color': '#38d17a',
                    'shape': 'roundrectangle',
                    'width': '80px',
                    'height': '60px',
                    'text-outline-color': '#43e97b'
                }
            },
            {
                selector: 'node:selected',
                style: {
                    'border-width': 6,
                    'border-color': '#ef4444',
                    'width': '120px',
                    'height': '120px',
                    'z-index': 9999
                }
            },
            {
                selector: 'node.highlighted',
                style: {
                    'border-width': 6,
                    'border-color': '#f59e0b',
                    'background-color': '#fbbf24',
                    'z-index': 9999
                }
            },
            {
                selector: 'node:hover',
                style: {
                    'border-width': 5,
                    'border-color': '#10b981'
                }
            },
            // Edge styles
            {
                selector: 'edge',
                style: {
                    'width': 3,
                    'line-color': '#cbd5e0',
                    'target-arrow-color': '#cbd5e0',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'label': 'data(label)',
                    'font-size': '11px',
                    'text-rotation': 'autorotate',
                    'text-margin-y': -12,
                    'color': '#1f2937',
                    'text-background-color': '#fff',
                    'text-background-opacity': 0.9,
                    'text-background-padding': '4px',
                    'text-background-shape': 'roundrectangle',
                    'transition-property': 'line-color, width',
                    'transition-duration': '0.3s'
                }
            },
            {
                selector: 'edge[type="subClassOf"]',
                style: {
                    'line-color': '#667eea',
                    'target-arrow-color': '#667eea',
                    'line-style': 'solid',
                    'width': 3
                }
            },
            {
                selector: 'edge[type="hierarchy"]',
                style: {
                    'line-color': '#8b5cf6',
                    'target-arrow-color': '#8b5cf6',
                    'line-style': 'solid',
                    'width': 3
                }
            },
            {
                selector: 'edge[type="object_property"]',
                style: {
                    'line-color': '#f093fb',
                    'target-arrow-color': '#f093fb',
                    'line-style': 'dashed',
                    'width': 2.5
                }
            },
            {
                selector: 'edge[type="data_property"]',
                style: {
                    'line-color': '#fbbf24',
                    'target-arrow-color': '#fbbf24',
                    'line-style': 'dotted',
                    'width': 2.5
                }
            },
            {
                selector: 'edge:selected',
                style: {
                    'width': 5,
                    'line-color': '#ef4444',
                    'target-arrow-color': '#ef4444',
                    'z-index': 9999
                }
            },
            {
                selector: 'edge:hover',
                style: {
                    'width': 4,
                    'line-color': '#10b981',
                    'target-arrow-color': '#10b981'
                }
            }
        ],
        
        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 1500,
            animationEasing: 'ease-out',
            nodeRepulsion: 12000,
            idealEdgeLength: 150,
            edgeElasticity: 120,
            nestingFactor: 5,
            gravity: 50,
            numIter: 1500,
            initialTemp: 300,
            coolingFactor: 0.95,
            minTemp: 1.0,
            padding: 50
        },
        
        minZoom: 0.2,
        maxZoom: 4,
        wheelSensitivity: 0.15
    });
    
    // Enhanced event listeners
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        
        // Highlight connected nodes
        cy.elements().removeClass('highlighted');
        node.addClass('highlighted');
        node.neighborhood().addClass('highlighted');
        
        showNodeDetails(node);
    });
    
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            cy.elements().removeClass('highlighted');
            hideNodeDetails();
        }
    });
    
    // Double-click to center and zoom on node
    cy.on('dbltap', 'node', function(evt) {
        const node = evt.target;
        cy.animate({
            center: { eles: node },
            zoom: 2,
            duration: 500,
            easing: 'ease-in-out-cubic'
        });
    });
    
    // Hover effects
    cy.on('mouseover', 'node', function(evt) {
        document.body.style.cursor = 'pointer';
    });
    
    cy.on('mouseout', 'node', function(evt) {
        document.body.style.cursor = 'default';
    });
    
    // Add graph control buttons
    addGraphControls();
    
        console.log('Graph initialized successfully!');
    } catch (error) {
        console.error('Error initializing Cytoscape graph:', error);
        showNoDataMessage('Failed to render graph visualization: ' + error.message);
    }
}

// ============================================
// GRAPH CONTROLS
// ============================================

function addGraphControls() {
    // Create control panel
    const controlsHtml = `
        <div style="position: absolute; top: 20px; right: 20px; display: flex; flex-direction: column; gap: 10px; z-index: 1000;">
            <button onclick="fitGraph()" style="background: var(--primary-color); color: white; border: none; border-radius: 8px; padding: 12px 16px; cursor: pointer; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2); transition: all 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🔍 Fit to Screen
            </button>
            <button onclick="resetZoom()" style="background: var(--card-bg); color: var(--text-primary); border: 2px solid var(--border-color); border-radius: 8px; padding: 12px 16px; cursor: pointer; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2); transition: all 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                ↺ Reset View
            </button>
            <button onclick="relayoutGraph()" style="background: var(--card-bg); color: var(--text-primary); border: 2px solid var(--border-color); border-radius: 8px; padding: 12px 16px; cursor: pointer; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2); transition: all 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                🔄 Re-layout
            </button>
            <button onclick="exportGraphImage()" style="background: #10b981; color: white; border: none; border-radius: 8px; padding: 12px 16px; cursor: pointer; font-size: 14px; font-weight: 600; box-shadow: 0 2px 8px rgba(0,0,0,0.2); transition: all 0.2s;" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                📸 Export PNG
            </button>
        </div>
    `;
    
    document.getElementById('ontology-graph').insertAdjacentHTML('beforebegin', controlsHtml);
}

// Graph control functions
function fitGraph() {
    if (cy) {
        cy.fit(null, 50);
        cy.animate({
            zoom: cy.zoom() * 0.9,
            duration: 500
        });
    }
}

function resetZoom() {
    if (cy) {
        cy.animate({
            zoom: 1,
            center: { eles: cy.elements() },
            duration: 500,
            easing: 'ease-in-out-cubic'
        });
    }
}

function relayoutGraph() {
    if (cy) {
        cy.layout({
            name: 'cose',
            animate: true,
            animationDuration: 1500,
            nodeRepulsion: 12000,
            idealEdgeLength: 150,
            edgeElasticity: 120,
            gravity: 50,
            numIter: 1500,
            padding: 50
        }).run();
    }
}

function exportGraphImage() {
    if (cy) {
        const png = cy.png({
            output: 'blob',
            bg: '#1a1f2e',
            full: true,
            scale: 3
        });
        
        const url = URL.createObjectURL(png);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ontology-graph-${Date.now()}.png`;
        a.click();
        URL.revokeObjectURL(url);
    }
}

// ============================================
// GRAPH ELEMENTS BUILDER
// ============================================

function buildGraphElements() {
    const nodes = [];
    const edges = [];
    const nodeIds = new Set(); // Track all node IDs
    
    // Add class nodes
    ontologyData.classes.forEach(cls => {
        nodes.push({
            data: {
                id: cls.id,
                label: cls.label,
                type: 'class'
            }
        });
        nodeIds.add(cls.id);
    });
    
    // Add object property nodes
    ontologyData.object_properties.forEach(prop => {
        nodes.push({
            data: {
                id: prop.id,
                label: prop.label,
                type: 'object_property'
            }
        });
        nodeIds.add(prop.id);
    });
    
    // Add data property nodes
    ontologyData.data_properties.forEach(prop => {
        nodes.push({
            data: {
                id: prop.id,
                label: prop.label,
                type: 'data_property'
            }
        });
        nodeIds.add(prop.id);
    });
    
    // Add individual nodes (limited to first 20 to avoid clutter)
    ontologyData.individuals.slice(0, 20).forEach(ind => {
        nodes.push({
            data: {
                id: ind.id,
                label: ind.label,
                type: 'individual'
            }
        });
        nodeIds.add(ind.id);
    });
    
    // Add edges from relations - ONLY if both source and target nodes exist
    ontologyData.relations.forEach((rel, idx) => {
        // Skip edges that reference non-existent nodes (like 'Thing', which is the root OWL class)
        if (nodeIds.has(rel.source) && nodeIds.has(rel.target)) {
            edges.push({
                data: {
                    id: `edge-${idx}`,
                    source: rel.source,
                    target: rel.target,
                    label: rel.relation,
                    type: rel.type || 'relation'
                }
            });
        } else {
            console.log(`Skipping edge ${idx}: ${rel.source} -> ${rel.target} (missing node)`);
        }
    });
    
    console.log(`Built graph: ${nodes.length} nodes, ${edges.length} valid edges (${ontologyData.relations.length - edges.length} edges skipped)`);
    
    return { nodes, edges };
}

// ============================================
// NODE DETAILS DISPLAY
// ============================================

function showNodeDetails(node) {
    const card = document.getElementById('node-details-card');
    const content = document.getElementById('node-details-content');
    
    const data = node.data();
    
    let html = `
        <div style="margin-bottom: 1rem;">
            <strong style="font-size: 1.1rem; color: var(--primary-color);">${data.label}</strong>
        </div>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="padding: 0.5rem; background: var(--bg-secondary); border-radius: 4px;">
                <strong>Type:</strong> ${data.type.replace('_', ' ').toUpperCase()}
            </div>
            <div style="padding: 0.5rem; background: var(--bg-secondary); border-radius: 4px;">
                <strong>ID:</strong> ${data.id}
            </div>
            <div style="padding: 0.5rem; background: var(--bg-secondary); border-radius: 4px;">
                <strong>Connections:</strong> ${node.degree()}
            </div>
    `;
    
    // Get connected nodes
    const connectedNodes = node.neighborhood('node');
    if (connectedNodes.length > 0) {
        html += `
            <div style="padding: 0.5rem; background: var(--bg-secondary); border-radius: 4px;">
                <strong>Connected to:</strong>
                <ul style="margin: 0.5rem 0 0 1rem; padding: 0;">
                    ${connectedNodes.slice(0, 5).map(n => `<li>${n.data('label')}</li>`).join('')}
                    ${connectedNodes.length > 5 ? `<li><em>...and ${connectedNodes.length - 5} more</em></li>` : ''}
                </ul>
            </div>
        `;
    }
    
    html += '</div>';
    
    content.innerHTML = html;
    card.style.display = 'block';
    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideNodeDetails() {
    document.getElementById('node-details-card').style.display = 'none';
}

// ============================================
// SEARCH & HIGHLIGHT
// ============================================

function setupSearchFilter() {
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value.toLowerCase();
            searchAndHighlight(query);
        }, 300);
    });
}

function searchAndHighlight(query) {
    if (!cy) return;
    
    // Remove previous highlights
    cy.nodes().removeClass('highlighted');
    
    if (!query) return;
    
    // Find matching nodes
    const matchingNodes = cy.nodes().filter(node => {
        const label = node.data('label').toLowerCase();
        return label.includes(query);
    });
    
    if (matchingNodes.length > 0) {
        matchingNodes.addClass('highlighted');
        cy.fit(matchingNodes, 100);
    }
}

function highlightNode(nodeName) {
    if (!cy) return;
    
    const node = cy.getElementById(nodeName);
    if (node.length > 0) {
        // Remove previous highlights
        cy.elements().removeClass('highlighted');
        
        // Highlight the node and its neighbors
        node.addClass('highlighted');
        node.neighborhood().addClass('highlighted');
        
        // Animate to center and zoom
        cy.animate({
            center: { eles: node },
            zoom: 2.5,
            duration: 600,
            easing: 'ease-in-out-cubic'
        });
        
        showNodeDetails(node);
    }
}

// ============================================
// LAYOUT CHANGE
// ============================================

function changeLayout(layoutName) {
    if (!cy) return;
    
    const layoutOptions = {
        name: layoutName,
        animate: true,
        animationDuration: 1000
    };
    
    // Add layout-specific options
    if (layoutName === 'cose') {
        layoutOptions.nodeRepulsion = 8000;
        layoutOptions.idealEdgeLength = 100;
        layoutOptions.gravity = 80;
    } else if (layoutName === 'circle') {
        layoutOptions.radius = 300;
    } else if (layoutName === 'grid') {
        layoutOptions.rows = 5;
    } else if (layoutName === 'breadthfirst') {
        layoutOptions.directed = true;
        layoutOptions.spacingFactor = 1.5;
    } else if (layoutName === 'concentric') {
        layoutOptions.concentric = node => node.degree();
        layoutOptions.levelWidth = () => 2;
    }
    
    cy.layout(layoutOptions).run();
}

// ============================================
// GRAPH CONTROLS
// ============================================

function resetGraph() {
    if (!cy) return;
    
    cy.nodes().removeClass('highlighted');
    cy.fit();
    hideNodeDetails();
}

function exportGraph() {
    if (!cy) return;
    
    const png = cy.png({
        full: true,
        scale: 2,
        bg: '#ffffff'
    });
    
    const link = document.createElement('a');
    link.href = png;
    link.download = 'bookstore-ontology.png';
    link.click();
}

// ============================================
// THEME SUPPORT
// ============================================

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    
    // Update graph background
    if (cy) {
        const isDark = document.body.classList.contains('dark-theme');
        document.getElementById('ontology-graph').style.background = 
            isDark ? '#1a202c' : '#f7fafc';
    }
}

// Load saved theme
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-theme');
}
