# app.py
from flask import Flask, jsonify, request
from database import ZeroDivisorDatabase
import json
import re

app = Flask(__name__)

def create_app():
    db = ZeroDivisorDatabase()
    
    def parse_component_filter(component_filter):
        """Parse component filter string into structured components"""
        components = []
        
        if not component_filter or not component_filter.strip():
            return components
            
        # Split by commas but be careful with parentheses
        parts = []
        current_part = ""
        paren_depth = 0
        
        for char in component_filter:
            if char == '(':
                paren_depth += 1
                current_part += char
            elif char == ')':
                paren_depth -= 1
                current_part += char
            elif char == ',' and paren_depth == 0:
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            if part.startswith('(') and part.endswith(')'):
                # Bipartite component: (a,b)
                try:
                    inner = part[1:-1]  # Remove parentheses
                    a, b = map(int, [x.strip() for x in inner.split(',')])
                    components.append({
                        'type': 'bipartite',
                        'p1': a,
                        'p2': b
                    })
                except ValueError:
                    raise ValueError(f"Invalid bipartite component format: {part}. Use (a,b)")
            else:
                # Complete component: a
                try:
                    a = int(part.strip())
                    components.append({
                        'type': 'complete',
                        'p1': a
                    })
                except ValueError:
                    raise ValueError(f"Invalid complete component format: {part}. Use a number")
        
        return components
    
    # Serve the HTML directly
    @app.route('/')
    def index():
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zero Divisor Graph Catalog</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            margin-bottom: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .filters {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .filter-group {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }
        
        .filter-item {
            display: flex;
            flex-direction: column;
        }
        
        label {
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #555;
        }
        
        input, select {
            padding: 0.75rem;
            border: 2px solid #e1e1e1;
            border-radius: 5px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1rem;
        }
        
        button {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .btn-success {
            background: #28a745;
            color: white;
        }
        
        .btn-success:hover {
            background: #218838;
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }
        
        .results {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .results-header {
            padding: 1rem 1.5rem;
            background: #f8f9fa;
            border-bottom: 1px solid #e1e1e1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .table-container {
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid #e1e1e1;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
            position: sticky;
            top: 0;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .component-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            background: #e9ecef;
            border-radius: 3px;
            font-size: 0.875rem;
            margin: 0.1rem;
        }
        
        .type-badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        
        .badge-complete {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-bipartite {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        .graph-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .graph-modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 10px;
            max-width: 90%;
            max-height: 90%;
            overflow: auto;
        }
        
        .close-modal {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Zero Divisor Graph Catalog</h1>
            <p class="subtitle">Explore exact zero divisor components for modular arithmetic rings Z_n</p>
        </header>
        
        <div class="filters">
            <div class="filter-group">
                <div class="filter-item">
                    <label for="startN">Start n:</label>
                    <input type="number" id="startN" value="1" min="1">
                </div>
                <div class="filter-item">
                    <label for="endN">End n:</label>
                    <input type="number" id="endN" value="100" min="1">
                </div>
                <div class="filter-item">
                    <label for="components">Components (comma-separated):</label>
                    <input type="text" id="components" placeholder="e.g., 4, (1,2), (2,8)">
                </div>
            </div>
            
            <div class="filter-group">
                <div class="filter-item">
                    <label for="componentType">Component Type:</label>
                    <select id="componentType">
                        <option value="">Any</option>
                        <option value="complete">Complete Only</option>
                        <option value="bipartite">Bipartite Only</option>
                    </select>
                </div>
                <div class="filter-item">
                    <div class="checkbox-group">
                        <input type="checkbox" id="exactMatch">
                        <label for="exactMatch">Exact component match only</label>
                    </div>
                </div>
            </div>
            
            <div class="actions">
                <button class="btn-secondary" onclick="resetFilters()">Reset Filters</button>
                <button class="btn-primary" onclick="loadEntries()">Search</button>
            </div>
        </div>
        
        <div class="results">
            <div class="results-header">
                <h3>Results</h3>
                <span id="resultCount">0 entries found</span>
            </div>
            <div class="table-container">
                <table id="resultsTable">
                    <thead>
                        <tr>
                            <th>n</th>
                            <th>Exact Components</th>
                            <th>Component Types</th>
                            <th>Partitions</th>
                            <th>Zero Vertices</th>
                            <th>Zero Edges</th>
                            <th>Exact Vertices</th>
                            <th>Exact Edges</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="resultsBody">
                        <!-- Results will be populated here -->
                    </tbody>
                </table>
            </div>
            <div id="loading" class="loading" style="display: none;">
                Loading entries...
            </div>
        </div>
    </div>
    
    <div id="graphModal" class="graph-modal">
        <div class="graph-modal-content">
            <button class="close-modal" onclick="closeGraphModal()">&times;</button>
            <h3 id="graphTitle">Graph</h3>
            <div id="graphContent">
                <!-- Graph content will be populated here -->
            </div>
        </div>
    </div>

    <script>
        let currentEntries = [];
        
        function loadEntries() {
            const startN = document.getElementById('startN').value;
            const endN = document.getElementById('endN').value;
            const components = document.getElementById('components').value;
            const componentType = document.getElementById('componentType').value;
            const exactMatch = document.getElementById('exactMatch').checked;
            
            const loading = document.getElementById('loading');
            const resultsBody = document.getElementById('resultsBody');
            const resultCount = document.getElementById('resultCount');
            
            loading.style.display = 'block';
            resultsBody.innerHTML = '';
            
            const params = new URLSearchParams({
                start_n: startN,
                end_n: endN,
                components: components,
                component_type: componentType,
                exact_match: exactMatch
            });
            
            fetch(`/api/entries?${params}`)
                .then(response => response.json())
                .then(data => {
                    loading.style.display = 'none';
                    
                    if (data.success) {
                        currentEntries = data.entries;
                        displayEntries(currentEntries);
                        resultCount.textContent = `${data.total} entries found`;
                    } else {
                        showError(data.error);
                    }
                })
                .catch(error => {
                    loading.style.display = 'none';
                    showError('Failed to load entries: ' + error.message);
                });
        }
        
        function displayEntries(entries) {
            const resultsBody = document.getElementById('resultsBody');
            
            if (entries.length === 0) {
                resultsBody.innerHTML = `
                    <tr>
                        <td colspan="9" style="text-align: center; padding: 2rem;">
                            No entries found matching your criteria
                        </td>
                    </tr>
                `;
                return;
            }
            
            resultsBody.innerHTML = entries.map(entry => `
                <tr>
                    <td><strong>Z<sub>${entry.n}</sub></strong></td>
                    <td>
                        ${entry.exact_components.split(',').map(comp => 
                            `<span class="component-badge">${comp.trim()}</span>`
                        ).join('')}
                    </td>
                    <td>
                        ${entry.has_complete ? '<span class="type-badge badge-complete">Complete</span>' : ''}
                        ${entry.has_bipartite ? '<span class="type-badge badge-bipartite">Bipartite</span>' : ''}
                    </td>
                    <td>${entry.partition_count}</td>
                    <td>${entry.zvertices_count}</td>
                    <td>${entry.zedges_count}</td>
                    <td>${entry.ezvertices_count}</td>
                    <td>${entry.ezedges_count}</td>
                    <td>
                        <button class="btn-success" 
                                onclick="generateGraph(${entry.n})"
                                ${entry.can_generate_graph ? '' : 'disabled'}
                                title="${entry.can_generate_graph ? 'Generate graph' : 'Graph not available for n > 5500'}">
                            Generate Graph
                        </button>
                    </td>
                </tr>
            `).join('');
        }
        
        function generateGraph(n) {
            const modal = document.getElementById('graphModal');
            const graphContent = document.getElementById('graphContent');
            const graphTitle = document.getElementById('graphTitle');
            
            graphTitle.textContent = `Graphs for Z_${n}`;
            graphContent.innerHTML = '<p>Loading graph data...</p>';
            modal.style.display = 'block';
            
            fetch(`/api/graph/${n}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        graphContent.innerHTML = `
                            <div style="margin-bottom: 1rem;">
                                <h4>Zero Divisor Graph</h4>
                                <pre>${JSON.stringify(data.data.zero_divisor_graph, null, 2)}</pre>
                            </div>
                            <div>
                                <h4>Exact Zero Divisor Graph</h4>
                                <pre>${JSON.stringify(data.data.exact_zero_divisor_graph, null, 2)}</pre>
                            </div>
                            <p><strong>Components:</strong> ${data.data.components}</p>
                        `;
                    } else {
                        graphContent.innerHTML = `<div class="error">${data.error}</div>`;
                    }
                })
                .catch(error => {
                    graphContent.innerHTML = `<div class="error">Failed to load graph: ${error.message}</div>`;
                });
        }
        
        function closeGraphModal() {
            document.getElementById('graphModal').style.display = 'none';
        }
        
        function resetFilters() {
            document.getElementById('startN').value = 1;
            document.getElementById('endN').value = 100;
            document.getElementById('components').value = '';
            document.getElementById('componentType').value = '';
            document.getElementById('exactMatch').checked = false;
        }
        
        function showError(message) {
            const resultsBody = document.getElementById('resultsBody');
            resultsBody.innerHTML = `
                <tr>
                    <td colspan="9">
                        <div class="error">${message}</div>
                    </td>
                </tr>
            `;
            document.getElementById('resultCount').textContent = 'Error loading entries';
        }
        
        // Load initial entries when page loads
        document.addEventListener('DOMContentLoaded', loadEntries);
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('graphModal');
            if (event.target === modal) {
                closeGraphModal();
            }
        });
    </script>
</body>
</html>
        '''
    
    @app.route('/api/entries')
    def get_entries():
        try:
            # Get query parameters
            start_n = request.args.get('start_n', 1, type=int)
            end_n = request.args.get('end_n', 100, type=int)
            component_filter = request.args.get('components', '')
            exact_match = request.args.get('exact_match', 'false') == 'true'
            component_type = request.args.get('component_type', '')
            
            # Build base query
            query = '''
                SELECT mn.nvalue, mn.exact_components_desc, mn.partition_count,
                       mn.zvertices_count, mn.zedges_count, mn.ezvertices_count, mn.ezedges_count,
                       mn.complete, mn.complete_bipartite
                FROM MyNumber mn
                WHERE mn.nvalue BETWEEN ? AND ?
            '''
            params = [start_n, end_n]
            
            # Parse and apply component filters
            if component_filter:
                components = parse_component_filter(component_filter)
                component_conditions = []
                component_params = []
                
                for comp in components:
                    if comp['type'] == 'bipartite':
                        component_conditions.append('''
                            EXISTS (
                                SELECT 1 FROM ExactConnection ec
                                WHERE ec.entry_id = mn.entry_id 
                                AND ec.component_type = 'bipartite'
                                AND ec.p1 = ? AND ec.p2 = ?
                            )
                        ''')
                        component_params.extend([comp['p1'], comp['p2']])
                    else:  # complete
                        component_conditions.append('''
                            EXISTS (
                                SELECT 1 FROM ExactConnection ec
                                WHERE ec.entry_id = mn.entry_id 
                                AND ec.component_type = 'complete'
                                AND ec.p1 = ? AND ec.p2 IS NULL
                            )
                        ''')
                        component_params.append(comp['p1'])
                
                if component_conditions:
                    query += ' AND (' + ' AND '.join(component_conditions) + ')'
                    params.extend(component_params)
                    
                    if exact_match:
                        # For exact match, also ensure the number of components matches
                        query += f' AND mn.partition_count = {len(components)}'
            
            # Apply component type filter
            if component_type:
                if component_type == 'complete':
                    query += ' AND mn.complete > 0'
                elif component_type == 'bipartite':
                    query += ' AND mn.complete_bipartite > 0'
            
            query += ' ORDER BY mn.nvalue'
            
            # Execute query
            conn = db._get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            # Format response
            entries = []
            for row in results:
                entry = {
                    'n': row[0],
                    'exact_components': row[1] if row[1] else 'None',
                    'partition_count': row[2],
                    'zvertices_count': row[3],
                    'zedges_count': row[4],
                    'ezvertices_count': row[5],
                    'ezedges_count': row[6],
                    'has_complete': row[7] > 0,
                    'has_bipartite': row[8] > 0,
                    'can_generate_graph': row[0] <= 5500
                }
                entries.append(entry)
            
            return jsonify({
                'success': True,
                'entries': entries,
                'total': len(entries)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/graph/<int:n>')
    def get_graph_data(n):
        try:
            if n > 5500:
                return jsonify({
                    'success': False,
                    'error': f'Graph generation not available for n > 5500 (requested n={n})'
                }), 400
            
            data = db.get_by_n(n)
            if not data:
                return jsonify({
                    'success': False,
                    'error': f'No data found for Z_{n}'
                }), 404
            
            # Check if structure data is available
            if (data.get('z_structure') == '0' or not data.get('z_structure') or
                data.get('ez_structure') == '0' or not data.get('ez_structure')):
                return jsonify({
                    'success': False,
                    'error': f'Structure data not available for Z_{n}'
                }), 404
            
            graph_data = {
                'n': n,
                'zero_divisor_graph': data['z_structure'],
                'exact_zero_divisor_graph': data['ez_structure'],
                'components': data['exact_components_desc']
            }
            
            return jsonify({
                'success': True,
                'data': graph_data
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)