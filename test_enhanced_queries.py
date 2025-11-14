# test_enhanced_queries.py
from database import ZeroDivisorDatabase
from graph_generator import display_catalog, search_by_components

def run_enhanced_queries():
    db = ZeroDivisorDatabase()
    
    print("=== ENHANCED TEST QUERIES ===\n")
    
    # Test 1: Display catalog
    print("1. Catalog for n=1 to 20:")
    catalog = display_catalog(1, 20)
    
    # Test 2: Search by components (research lead's example)
    print("\n2. Search for numbers with (1,2) component:")
    results = search_by_components([(1, 2)])
    
    # Test 3: Search for multiple components
    print("\n3. Search for numbers with both (1,2) and K_2:")
    results = search_by_components([(1, 2), (2,)])
    
    # Test 4: Get detailed data for specific n
    print("\n4. Detailed data for Z_6:")
    data = db.get_by_n(6)
    if data:
        print(f"   Zero divisor vertices: {len(data['zvertices'])}")
        print(f"   Zero divisor edges: {len(data['zedges'])}")
        print(f"   Exact zero divisor vertices: {len(data['ezvertices'])}")
        print(f"   Exact zero divisor edges: {len(data['ezedges'])}")
        print(f"   Components: {data['exact_components_desc']}")
    
    print("\n=== ALL ENHANCED TESTS COMPLETE ===")

if __name__ == "__main__":
    run_enhanced_queries()