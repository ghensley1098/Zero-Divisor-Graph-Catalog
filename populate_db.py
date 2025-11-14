# populate_db.py
from database import ZeroDivisorDatabase
from catalog import get_zero_divisors, get_exact_zero_divisors, get_exact_components
import sys
import json

def calculate_graph_data(n):
    """Calculate graph data, but store "0" for vertex/edge lists when n > 6150"""
    zero_divisors = get_zero_divisors(n)
    exact_zero_divisors = get_exact_zero_divisors(n, zero_divisors)
    comps = get_exact_components(n, exact_zero_divisors)

    # For n > 6150, store "0" for all the list data
    if n > 6150:
        # Calculate component counts only (minimal computation)
        complete_count = sum(1 for comp in comps if len(comp) == 1)
        bipartite_count = sum(1 for comp in comps if len(comp) == 2)

        # Component description string
        comp_desc = ','.join(
            str(comp[0]) if len(comp) == 1 else f'({comp[0]},{comp[1]})'
            for comp in comps
        )

        graph_data = {
            # Store "0" for all list data to save space
            'zvertices': '0',
            'zedges': '0',
            'zself_loops': '0',
            'zvertices_count': 0,
            'zedges_count': 0,
            'z_structure': '0',

            'ez_vertices': '0',
            'ez_edges': '0',
            'ez_self_loops': '0',
            'ez_vertices_count': 0,
            'ez_edges_count': 0,
            'ez_structure': '0',

            # Component analysis
            'complete': complete_count,
            'complete_bipartite': bipartite_count,
            'exact_components': comps,
            'partition_count': len(comps),
            'comp_desc': comp_desc
        }

        return graph_data

    else:
        # For n <= 6150, use the original logic

        z_vertices = set()
        z_edges = set()
        z_self_loops = set()

        for x, y in zero_divisors:
            if x == 0 or y == 0:
                continue

            z_vertices.add(x)
            z_vertices.add(y)

            if x == y:
                z_self_loops.add(x)
                z_edges.add((x, x))
            else:
                z_edges.add(tuple(sorted((x, y))))

        ez_vertices = set()
        ez_edges = set()
        ez_self_loops = set()
        ezd_pairs = set(exact_zero_divisors)

        for x, y in exact_zero_divisors:
            if x == 0 or y == 0:
                continue

            if x == y:
                ez_self_loops.add(x)
                ez_edges.add((x, x))
            elif (y, x) in ezd_pairs:
                ez_vertices.add(x)
                ez_vertices.add(y)
                ez_edges.add(tuple(sorted((x, y))))

        z_vertices.update(z_self_loops)
        ez_vertices.update(ez_self_loops)

        complete_count = sum(1 for comp in comps if len(comp) == 1)
        bipartite_count = sum(1 for comp in comps if len(comp) == 2)

        comp_desc = ','.join(
            str(comp[0]) if len(comp) == 1 else f'({comp[0]},{comp[1]})'
            for comp in comps
        )

        graph_data = {
            'zvertices': json.dumps(list(z_vertices)),
            'zedges': json.dumps([list(pair) for pair in z_edges]),
            'zself_loops': json.dumps(list(z_self_loops)),
            'zvertices_count': len(z_vertices),
            'zedges_count': len(z_edges),
            'z_structure': json.dumps({
                'vertices': list(z_vertices),
                'edges': [list(pair) for pair in z_edges],
                'self_loops': list(z_self_loops)
            }),

            'ez_vertices': json.dumps(list(ez_vertices)),
            'ez_edges': json.dumps([list(pair) for pair in ez_edges]),
            'ez_self_loops': json.dumps(list(ez_self_loops)),
            'ez_vertices_count': len(ez_vertices),
            'ez_edges_count': len(ez_edges),
            'ez_structure': json.dumps({
                'vertices': list(ez_vertices),
                'edges': [list(pair) for pair in ez_edges],
                'self_loops': list(ez_self_loops)
            }),

            'complete': complete_count,
            'complete_bipartite': bipartite_count,
            'exact_components': comps,
            'partition_count': len(comps),
            'comp_desc': comp_desc
        }

        return graph_data

def populate_database(start_n=6151, end_n=10000):
    """Populate database with data from start_n to end_n (storage optimized for n > 6150)"""
    db = ZeroDivisorDatabase()

    print(f"Populating database from n={start_n} to n={end_n}...")
    print("For n > 6150: storing '0' for vertex/edge lists to save space")

    for n in range(start_n, end_n + 1):
        try:
            print(f"Processing Z_{n}...")
            graph_data = calculate_graph_data(n)
            db.insert_number_data(n, graph_data)

            comp_desc = graph_data['comp_desc']
            storage_mode = "optimized" if n > 6150 else "full"
            print(f"  ✓ Added Z_{n}: {comp_desc} ({storage_mode} storage)")

        except Exception as e:
            print(f"  ✗ Error processing Z_{n}: {e}")

    print("Database population complete!")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        start_n = int(sys.argv[1])
        end_n = int(sys.argv[2])
    elif len(sys.argv) == 2:
        start_n = int(sys.argv[1])
        end_n = start_n + 100  # Default to next 100 numbers
    else:
        start_n = 6151
        end_n = 6250