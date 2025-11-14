# query_structures.py
from database import ZeroDivisorDatabase
import json

# def display_available_entries():
#     """Show all available n values in the database"""
#     db = ZeroDivisorDatabase()
#     conn = db._get_connection()
#     cursor = conn.cursor()
    
#     cursor.execute('SELECT nvalue FROM MyNumber ORDER BY nvalue')
#     results = cursor.fetchall()
#     conn.close()
    
#     if results:
#         n_values = [row[0] for row in results]
#         print(f"\nAvailable n values in database: {n_values}")
#         return n_values
#     else:
#         print("\nNo entries found in database. Please run populate_db.py first.")
#         return []

def query_structure_values(n_values):
    """Query and display the actual structure attribute values for specified n values"""
    db = ZeroDivisorDatabase()
    
    print(f"\n=== STRUCTURE ATTRIBUTE VALUES FOR n = {n_values} ===\n")
    
    for n in n_values:
        data = db.get_by_n(n)
        if data:
            print(f"Z_{n}:")
            print(f"  Zero Divisor Graph:")
            print(f"    Vertices: {sorted(data['z_structure']['vertices'])}")
            print(f"    Edges: {sorted(data['z_structure']['edges'])}")
            print(f"    Vertex count: {data['zvertices_count']}")
            print(f"    Edge count: {data['zedges_count']}")
            print(f"  Exact Zero Divisor Graph:")
            print(f"    Vertices: {sorted(data['ez_structure']['vertices'])}")
            print(f"    Edges: {sorted(data['ez_structure']['edges'])}")
            print(f"    Vertex count: {data['ezvertices_count']}")
            print(f"    Edge count: {data['ezedges_count']}")
            print(f"  Components: {data['exact_components_desc']}")
            print(f"  Partition count: {data['partition_count']}")
            print("-" * 60)
        else:
            print(f"Z_{n}: No data found")
            print("-" * 60)

def query_raw_structure_json(n):
    """Query and display the raw JSON structure for a specific n"""
    db = ZeroDivisorDatabase()
    
    conn = db._get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT nvalue, z_structure, ez_structure, exact_components_desc 
        FROM MyNumber WHERE nvalue = ?
    ''', (n,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        nval, z_struct, ez_struct, comp_desc = result
        print(f"\nRAW STRUCTURE DATA for Z_{nval}:")
        print(f"Zero Divisor Structure JSON: {z_struct}")
        print(f"Exact Zero Divisor Structure JSON: {ez_struct}")
        print(f"Components Description: {comp_desc}")
        
        # Parse and display formatted
        print(f"\nFORMATTED STRUCTURE for Z_{nval}:")
        z_parsed = json.loads(z_struct)
        ez_parsed = json.loads(ez_struct)
        
        print(f"Zero Divisor Graph:")
        print(f"  Vertices: {sorted(z_parsed['vertices'])}")
        print(f"  Edges: {sorted(z_parsed['edges'])}")
        print(f"Exact Zero Divisor Graph:")
        print(f"  Vertices: {sorted(ez_parsed['vertices'])}")
        print(f"  Edges: {sorted(ez_parsed['edges'])}")
    else:
        print(f"No data found for Z_{n}")

def get_user_choice():
    """Get user input for which entries to query"""
    print("Choose query option:")
    print("1. Query specific n values")
    print("2. Query all available n values")
    print("3. Query range of n values")
    print("4. View raw JSON for specific n")
    print("5. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            if choice in ['1', '2', '3', '4', '5']:
                return choice
            else:
                print("Please enter a number between 1 and 5")
        except KeyboardInterrupt:
            print("\nExiting...")
            return '5'

def get_specific_n_values():
    """Get specific n values from user"""
    while True:
        try:
            input_str = input("\nEnter n values to query (comma-separated, e.g., 6,8,10): ").strip()
            if input_str.lower() == 'back':
                return None
            n_values = [int(x.strip()) for x in input_str.split(',')]
            return n_values
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None

def get_range_values():
    """Get range from user"""
    while True:
        try:
            start = input("Enter start n: ").strip()
            if start.lower() == 'back':
                return None
            end = input("Enter end n: ").strip()
            if end.lower() == 'back':
                return None
            return list(range(int(start), int(end) + 1))
        except ValueError:
            print("Invalid input. Please enter numbers.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None

def get_single_n():
    """Get single n value from user"""
    while True:
        try:
            n_str = input("\nEnter n value to view raw JSON: ").strip()
            if n_str.lower() == 'back':
                return None
            return int(n_str)
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None

def main():
    """Main interactive function"""
    print("=" * 70)
    print("ZERO DIVISOR GRAPH STRUCTURE QUERY TOOL")
    print("=" * 70)
    
    # Show available entries first
    # available_entries = display_available_entries()
    # if not available_entries:
    #     return
    
    while True:
        choice = get_user_choice()
        
        if choice == '1':  # Query specific n values
            n_values = get_specific_n_values()
            if n_values is not None:
                query_structure_values(n_values)
                
        elif choice == '2':  # Query all available
            query_structure_values(available_entries)
            
        elif choice == '3':  # Query range
            n_values = get_range_values()
            if n_values is not None:
                # Filter to only available entries in range
                available_in_range = [n for n in n_values if n in available_entries]
                if available_in_range:
                    query_structure_values(available_in_range)
                else:
                    print("No data available for the specified range.")
                    
        elif choice == '4':  # Raw JSON for specific n
            n = get_single_n()
            if n is not None:
                if n in available_entries:
                    query_raw_structure_json(n)
                else:
                    print(f"No data available for Z_{n}")
                    
        elif choice == '5':  # Exit
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()