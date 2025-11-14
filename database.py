# database.py
import sqlite3
import json
from typing import List, Tuple, Optional

class ZeroDivisorDatabase:
    def __init__(self, db_path="zero_divisor_catalog.db"):
        self.db_path = db_path
        self.init_database()
    
    def _get_connection(self):
        """Get database connection (for internal use)"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database with enhanced schema for both graph types"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create MyNumber table with enhanced fields including self_loops
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MyNumber (
                entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                nvalue INTEGER NOT NULL UNIQUE,
                
                -- Zero divisor graph data
                zvertices TEXT,
                zedges TEXT,
                zself_loops TEXT,
                zvertices_count INTEGER,
                zedges_count INTEGER,
                z_structure TEXT,
                
                -- Exact zero divisor graph data  
                ezvertices TEXT,
                ezedges TEXT,
                ezself_loops TEXT,
                ezvertices_count INTEGER,
                ezedges_count INTEGER,
                ez_structure TEXT,
                
                -- Component analysis
                complete INTEGER,
                complete_bipartite INTEGER,
                exact_components_desc TEXT,
                partition_count INTEGER
            )
        ''')
        
        # Create ExactConnection table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ExactConnection (
                connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                component_type TEXT NOT NULL CHECK(component_type IN ('complete', 'bipartite')),
                p1 INTEGER NOT NULL,
                p2 INTEGER,
                FOREIGN KEY (entry_id) REFERENCES MyNumber (entry_id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nvalue ON MyNumber(nvalue)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entry_id ON ExactConnection(entry_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_component_type ON ExactConnection(component_type)')
        
        conn.commit()
        conn.close()
    
    def insert_number_data(self, n, graph_data):
        """Insert data for a specific n value with both graph types INCLUDING SELF-LOOPS"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Component description string (like "(1,8),(2,4),(2,4),(2,8)")
        comp_desc = graph_data.get('comp_desc', '')
        
        # Zero divisor graph data - INCLUDE SELF-LOOPS
        zvertices = json.dumps(list(graph_data.get('zvertices', [])))
        zedges = json.dumps([list(pair) for pair in graph_data.get('zedges', [])])
        z_self_loops = json.dumps(list(graph_data.get('zself_loops', [])))
        z_structure = json.dumps({
            'vertices': list(graph_data.get('zvertices', [])),
            'edges': [list(pair) for pair in graph_data.get('zedges', [])],
            'self_loops': list(graph_data.get('zself_loops', []))
        })
        
        # Exact zero divisor graph data - INCLUDE SELF-LOOPS
        ezvertices = json.dumps(list(graph_data.get('ez_vertices', [])))
        ezedges = json.dumps([list(pair) for pair in graph_data.get('ez_edges', [])])
        ez_self_loops = json.dumps(list(graph_data.get('ez_self_loops', [])))
        ez_structure = json.dumps({
            'vertices': list(graph_data.get('ez_vertices', [])),
            'edges': [list(pair) for pair in graph_data.get('ez_edges', [])],
            'self_loops': list(graph_data.get('ez_self_loops', []))
        })
        
        cursor.execute('''
            INSERT OR REPLACE INTO MyNumber (
                nvalue, 
                zvertices, zedges, zself_loops, zvertices_count, zedges_count, z_structure,
                ezvertices, ezedges, ezself_loops, ezvertices_count, ezedges_count, ez_structure,
                complete, complete_bipartite, exact_components_desc, partition_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            n,
            zvertices, zedges, z_self_loops,
            graph_data.get('zvertices_count', 0), graph_data.get('zedges_count', 0),
            z_structure,
            ezvertices, ezedges, ez_self_loops,
            graph_data.get('ez_vertices_count', 0), graph_data.get('ez_edges_count', 0),
            ez_structure,
            graph_data.get('complete', 0),
            graph_data.get('complete_bipartite', 0),
            comp_desc,
            graph_data.get('partition_count', 0)
        ))
        
        entry_id = cursor.lastrowid
        
        # Clear existing connections and insert new ones
        cursor.execute('DELETE FROM ExactConnection WHERE entry_id = ?', (entry_id,))
        
        # Insert exact connection components
        for comp in graph_data.get('exact_components', []):
            if len(comp) == 1:  # Complete graph (clique)
                cursor.execute('''
                    INSERT INTO ExactConnection (entry_id, component_type, p1, p2)
                    VALUES (?, 'complete', ?, NULL)
                ''', (entry_id, comp[0]))
            elif len(comp) == 2:  # Complete bipartite graph
                cursor.execute('''
                    INSERT INTO ExactConnection (entry_id, component_type, p1, p2)
                    VALUES (?, 'bipartite', ?, ?)
                ''', (entry_id, comp[0], comp[1]))
        
        conn.commit()
        conn.close()
        return entry_id
    
    def get_catalog_table(self, start_n=1, end_n=100):
        """Generate the catalog table as requested by research lead"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT nvalue, exact_components_desc 
            FROM MyNumber 
            WHERE nvalue BETWEEN ? AND ?
            ORDER BY nvalue
        ''', (start_n, end_n))
        
        results = cursor.fetchall()
        conn.close()
        
        catalog = []
        for n, components_desc in results:
            catalog.append({
                'n': n,
                'exact_components': components_desc if components_desc else 'None'
            })
        
        return catalog
    
    def find_by_exact_components(self, required_components):
        """
        Find n values that have all the specified exact components
        Example: find_by_exact_components([(1,8), (2,8)]) finds n with both (1,8) and (2,8)
        """
        return self.find_by_components(required_components)
    
    def get_by_n(self, n):
        """Retrieve complete data for a specific n value"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM MyNumber WHERE nvalue = ?', (n,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        # Get exact connections
        cursor.execute('''
            SELECT component_type, p1, p2 
            FROM ExactConnection 
            WHERE entry_id = ?
        ''', (result[0],))
        
        connections = cursor.fetchall()
        conn.close()
        
        return {
            'entry_id': result[0],
            'nvalue': result[1],
            # Zero divisor graph data
            'zvertices': json.loads(result[2]) if result[2] else [],
            'zedges': json.loads(result[3]) if result[3] else [],
            'zself_loops': json.loads(result[4]) if result[4] else [],
            'zvertices_count': result[5],
            'zedges_count': result[6],
            'z_structure': json.loads(result[7]) if result[7] else {},
            # Exact zero divisor graph data
            'ezvertices': json.loads(result[8]) if result[8] else [],
            'ezedges': json.loads(result[9]) if result[9] else [],
            'ezself_loops': json.loads(result[10]) if result[10] else [],
            'ezvertices_count': result[11],
            'ezedges_count': result[12],
            'ez_structure': json.loads(result[13]) if result[13] else {},
            # Component analysis
            'complete': result[14],
            'complete_bipartite': result[15],
            'exact_components_desc': result[16],
            'partition_count': result[17],
            'exact_components': connections
        }
    
    def find_by_components(self, required_components):
        """
        Find n values that have all the specified components
        required_components: list of tuples, e.g., [(1,8), (2,8)] or [(4,)] for clique
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build dynamic query based on required components
        query = '''
            SELECT DISTINCT mn.nvalue, mn.exact_components_desc
            FROM MyNumber mn
            WHERE 1=1
        '''
        params = []
        
        for i, comp in enumerate(required_components):
            if len(comp) == 1:  # Complete graph
                query += f'''
                    AND EXISTS (
                        SELECT 1 FROM ExactConnection ec
                        WHERE ec.entry_id = mn.entry_id 
                        AND ec.component_type = 'complete'
                        AND ec.p1 = ?
                        AND ec.p2 IS NULL
                    )
                '''
                params.append(comp[0])
            elif len(comp) == 2:  # Bipartite graph
                query += f'''
                    AND EXISTS (
                        SELECT 1 FROM ExactConnection ec
                        WHERE ec.entry_id = mn.entry_id 
                        AND ec.component_type = 'bipartite'
                        AND ec.p1 = ? AND ec.p2 = ?
                    )
                '''
                params.extend([comp[0], comp[1]])
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [{'n': row[0], 'exact_components': row[1]} for row in results]