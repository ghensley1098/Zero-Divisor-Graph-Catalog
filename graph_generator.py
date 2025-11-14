# graph_generator.py
import networkx as nx
import matplotlib.pyplot as plt
import json
import math
from database import ZeroDivisorDatabase

def generate_zero_divisor_graph(n, db_path="zero_divisor_catalog.db", save_graph=False):
    """Generate the normal zero divisor graph from stored structure using the original algorithm's layout"""
    db = ZeroDivisorDatabase(db_path)
    data = db.get_by_n(n)
    
    if not data:
        print(f"No data found for Z_{n}")
        return
    
    structure = data['z_structure']
    _generate_zero_divisor_graph_from_structure(
        structure, 
        f"Zero Divisor Graph Γ(Z_{n})",
        save_graph
    )

def generate_exact_zero_divisor_graph(n, db_path="zero_divisor_catalog.db", save_graph=False):
    """Generate the exact zero divisor graph from stored structure using the original algorithm's layout"""
    db = ZeroDivisorDatabase(db_path)
    data = db.get_by_n(n)
    
    if not data:
        print(f"No data found for Z_{n}")
        return
    
    structure = data['ez_structure']
    _generate_exact_zero_divisor_graph_from_structure(
        structure, 
        f"Exact Zero Divisor Graph for Z_{n}\nComponents: {data['exact_components_desc']}",
        save_graph
    )

def _generate_zero_divisor_graph_from_structure(structure_data, title, save_graph=False):
    """
    Generate zero divisor graph using the original algorithm's high-quality layout
    WITH SELF-LOOP COLORING (but no visual loop edges)
    """
    G = nx.Graph()
    
    # Add vertices and edges from structure, but FILTER OUT SELF-LOOP EDGES for display
    G.add_nodes_from(structure_data.get('vertices', []))
    
    # Only add non-self-loop edges to the graph for visualization
    edges_to_display = [edge for edge in structure_data.get('edges', []) if edge[0] != edge[1]]
    G.add_edges_from(edges_to_display)
    
    # Get self-loop vertices
    self_loop_vertices = set(structure_data.get('self_loops', []))
    
    if not G.nodes():
        print("Graph is empty.")
        return

    # Use the original algorithm's layout settings
    plt.figure(figsize=(20, 20))
    
    pos = {}
    if G.number_of_nodes() > 0:
        # Use the original tuned spring layout for better aesthetics
        k_val = 2.5 / math.sqrt(G.number_of_nodes())
        pos = nx.spring_layout(G, k=k_val, iterations=100, seed=42)
    
    # Color nodes: light orange for self-loops, light blue for others
    node_colors = []
    for node in G.nodes():
        if node in self_loop_vertices:
            node_colors.append('lightcoral')  # Light orange/red for self-loops
        else:
            node_colors.append('lightblue')
    
    # Use original styling
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000)
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=14, font_color='red', font_weight='bold')

    plt.title(title, fontsize=22)
    plt.axis('off')
    plt.tight_layout()

    if save_graph:
        filename = f"zero_divisor_graph_Z_{title.split('_')[1].split(')')[0]}.png"
        plt.savefig(filename, bbox_inches='tight')
        print(f"Zero divisor graph saved as {filename}")
    else:
        plt.show()

def _generate_exact_zero_divisor_graph_from_structure(structure_data, title, save_graph=False):
    """
    Generate exact zero divisor graph using the original algorithm's high-quality layout
    WITH SELF-LOOP COLORING (but no visual loop edges) and separate components in subplots
    """
    G = nx.Graph()
    
    # Add vertices and edges from structure, but FILTER OUT SELF-LOOP EDGES for display
    G.add_nodes_from(structure_data.get('vertices', []))
    
    # Only add non-self-loop edges to the graph for visualization
    edges_to_display = [edge for edge in structure_data.get('edges', []) if edge[0] != edge[1]]
    G.add_edges_from(edges_to_display)
    
    # Get self-loop vertices
    self_loop_vertices = set(structure_data.get('self_loops', []))
    
    if not G.nodes():
        print("Graph is empty.")
        return

    # Find and draw connected components in separate subplots (original algorithm style)
    components = list(nx.connected_components(G))
    num_components = len(components)
    
    if num_components == 0:
        return

    # Arrange subplots in a grid (original algorithm settings)
    cols = int(math.ceil(math.sqrt(num_components)))
    rows = int(math.ceil(num_components / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(8 * cols, 8 * rows), squeeze=False)
    axes = axes.flatten()

    fig.suptitle(title, fontsize=20)

    for i, comp_nodes in enumerate(components):
        comp = G.subgraph(comp_nodes).copy()
        ax = axes[i]
        pos = nx.kamada_kawai_layout(comp)  # Original algorithm uses kamada_kawai for components
        
        # Color nodes: light orange for self-loops, light green for others
        node_colors = []
        for node in comp.nodes():
            if node in self_loop_vertices:
                node_colors.append('lightcoral')  # Light orange/red for self-loops
            else:
                node_colors.append('lightgreen')
        
        # Use original styling for components
        nx.draw_networkx_nodes(comp, pos, ax=ax, node_color=node_colors, node_size=1500)
        nx.draw_networkx_edges(comp, pos, ax=ax, width=1.5, alpha=0.8, edge_color='gray')
        nx.draw_networkx_labels(comp, pos, ax=ax, font_size=12, font_color='black', font_weight='bold')
        ax.axis('off')

    # Hide any unused subplots
    for i in range(num_components, len(axes)):
        axes[i].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if save_graph:
        filename = f"exact_zero_divisor_graph_Z_{title.split('_')[4]}.png"
        plt.savefig(filename, bbox_inches='tight')
        print(f"Exact zero divisor graph saved as {filename}")
    else:
        plt.show()

def display_catalog(start_n=1, end_n=100):
    """Display the catalog table as requested by research lead"""
    db = ZeroDivisorDatabase()
    catalog = db.get_catalog_table(start_n, end_n)
    
    print("\n" + "="*80)
    print(f"CATALOG: Zero Divisor Graphs and Exact Components (n={start_n} to {end_n})")
    print("="*80)
    print(f"{'n':<6} {'Exact Components':<40}")
    print("-" * 80)
    
    for item in catalog:
        print(f"{item['n']:<6} {item['exact_components']:<40}")
    
    print("="*80)
    return catalog

def search_by_components(component_list):
    """Search for numbers with specific exact components"""
    db = ZeroDivisorDatabase()
    results = db.find_by_exact_components(component_list)
    
    print(f"\nSEARCH RESULTS for components: {component_list}")
    print("="*50)
    
    if results:
        for result in results:
            print(f"n = {result['n']}: {result['exact_components']}")
    else:
        print("No results found.")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python graph_generator.py zero <n> [-s]    # Generate zero divisor graph")
        print("  python graph_generator.py exact <n> [-s]    # Generate exact zero divisor graph")  
        print("  python graph_generator.py catalog [end]     # Display catalog (1 to end)")
        print("  python graph_generator.py search <comp>     # Search by components")
        print("\nExamples:")
        print("  python graph_generator.py zero 6")
        print("  python graph_generator.py exact 8 -s") 
        print("  python graph_generator.py catalog 20")
        print("  python graph_generator.py search '(1,2)'")
        print("  python graph_generator.py search '(1,2)' '(2,)'")
        sys.exit(1)
    
    command = sys.argv[1]
    save_flag = '-s' in sys.argv
    
    if command == "zero" and len(sys.argv) > 2:
        n = int(sys.argv[2])
        generate_zero_divisor_graph(n, save_graph=save_flag)
        
    elif command == "exact" and len(sys.argv) > 2:
        n = int(sys.argv[2])
        generate_exact_zero_divisor_graph(n, save_graph=save_flag)
        
    elif command == "catalog":
        end_n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        display_catalog(1, end_n)
        
    elif command == "search" and len(sys.argv) > 2:
        components = []
        for comp_str in sys.argv[2:]:
            if comp_str == '-s':
                continue
            if '(' in comp_str:
                # Bipartite component like (1,8)
                a, b = map(int, comp_str.strip('()').split(','))
                components.append((a, b))
            else:
                # Complete component like 4
                components.append((int(comp_str),))
        search_by_components(components)
        
    else:
        print("Invalid command")