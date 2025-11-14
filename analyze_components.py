# analyze_components.py
from database import ZeroDivisorDatabase

def analyze_interesting_entries():
    """Find entries with interesting/non-trivial components"""
    db = ZeroDivisorDatabase()
    conn = db._get_connection()
    cursor = conn.cursor()
    
    print("INTERESTING ENTRIES ANALYSIS")
    print("=" * 60)
    
    # Find entries with the most components
    print("\n1. Entries with most components:")
    cursor.execute('''
        SELECT nvalue, partition_count, exact_components_desc 
        FROM MyNumber 
        WHERE partition_count > 0 
        ORDER BY partition_count DESC 
        LIMIT 10
    ''')
    results = cursor.fetchall()
    for n, count, comps in results:
        print(f"  Z_{n}: {count} components - {comps}")
    
    # Find entries with largest bipartite components
    print("\n2. Entries with largest bipartite components:")
    cursor.execute('''
        SELECT nvalue, p1, p2, exact_components_desc 
        FROM MyNumber mn
        JOIN ExactConnection ec ON mn.entry_id = ec.entry_id
        WHERE ec.component_type = 'bipartite'
        ORDER BY (p1 + p2) DESC 
        LIMIT 10
    ''')
    results = cursor.fetchall()
    for n, p1, p2, comps in results:
        print(f"  Z_{n}: K_{{{p1},{p2}}} - Full: {comps}")
    
    # Find entries with largest cliques
    print("\n3. Entries with largest cliques:")
    cursor.execute('''
        SELECT nvalue, p1, exact_components_desc 
        FROM MyNumber mn
        JOIN ExactConnection ec ON mn.entry_id = ec.entry_id
        WHERE ec.component_type = 'complete' AND ec.p2 IS NULL
        ORDER BY p1 DESC 
        LIMIT 10
    ''')
    results = cursor.fetchall()
    for n, p1, comps in results:
        print(f"  Z_{n}: K_{p1} - Full: {comps}")
    
    # Find entries with multiple component types
    print("\n4. Entries with diverse components (mix of complete and bipartite):")
    cursor.execute('''
        SELECT nvalue, 
               COUNT(DISTINCT component_type) as type_count,
               exact_components_desc
        FROM MyNumber mn
        JOIN ExactConnection ec ON mn.entry_id = ec.entry_id
        GROUP BY nvalue
        HAVING type_count > 1
        ORDER BY type_count DESC, partition_count DESC
        LIMIT 10
    ''')
    results = cursor.fetchall()
    for n, type_count, comps in results:
        print(f"  Z_{n}: {type_count} component types - {comps}")
    
    conn.close()

def find_by_component_pattern(pattern_type, value):
    """Find entries with specific component patterns"""
    db = ZeroDivisorDatabase()
    
    if pattern_type == "bipartite_sum":
        # Find bipartite components where a+b = value
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT nvalue, p1, p2, exact_components_desc
            FROM MyNumber mn
            JOIN ExactConnection ec ON mn.entry_id = ec.entry_id
            WHERE ec.component_type = 'bipartite' AND (p1 + p2) = ?
            ORDER BY nvalue
        ''', (value,))
        results = cursor.fetchall()
        conn.close()
        
        print(f"\nBipartite components with sum {value}:")
        for n, p1, p2, comps in results:
            print(f"  Z_{n}: K_{{{p1},{p2}}} - {comps}")
    
    elif pattern_type == "clique_size":
        # Find cliques of specific size
        conn = db._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT nvalue, exact_components_desc
            FROM MyNumber mn
            JOIN ExactConnection ec ON mn.entry_id = ec.entry_id
            WHERE ec.component_type = 'complete' AND ec.p1 = ? AND ec.p2 IS NULL
            ORDER BY nvalue
        ''', (value,))
        results = cursor.fetchall()
        conn.close()
        
        print(f"\nComplete components of size {value}:")
        for n, comps in results:
            print(f"  Z_{n}: {comps}")

if __name__ == "__main__":
    analyze_interesting_entries()
    
    # Example pattern searches
    find_by_component_pattern("bipartite_sum", 10)  # Find K_{a,b} where a+b=10
    find_by_component_pattern("clique_size", 4)     # Find K_4 components