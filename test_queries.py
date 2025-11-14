# test_queries.py
from database import ZeroDivisorDatabase

def run_test_queries():
    db = ZeroDivisorDatabase()
    
    print("=== TEST QUERIES ===\n")
    
    # Test 1: Get specific n value
    print("1. Data for Z_6:")
    data = db.get_by_n(6)
    if data:
        print(f"   Components: {len(data['exact_components'])}")
        print(f"   Structure vertices: {len(data['structure']['vertices'])}")
        print(f"   Structure edges: {len(data['structure']['edges'])}")
    else:
        print("   No data found")
    
    print("\n2. Data for Z_8:")
    data = db.get_by_n(8)
    if data:
        print(f"   Components: {len(data['exact_components'])}")
        print(f"   Structure vertices: {len(data['structure']['vertices'])}")
        print(f"   Structure edges: {len(data['structure']['edges'])}")
    else:
        print("   No data found")
    
    # Test 2: Find by components
    print("\n3. Numbers with specific components:")
    
    # Find numbers with K_4 (clique of size 4)
    results = db.find_by_components([(4,)])
    print(f"   Numbers with K_4: {[r['n'] for r in results]}")
    
    # Find numbers with specific bipartite components
    results = db.find_by_components([(1, 2)])
    print(f"   Numbers with K_{{1,2}}: {[r['n'] for r in results]}")
    
    # Test 3: Complex query - numbers with multiple components
    print("\n4. Complex component search:")
    # This would find numbers that have both specified components
    # (You'll need more data for meaningful results)
    
    print("\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    run_test_queries()