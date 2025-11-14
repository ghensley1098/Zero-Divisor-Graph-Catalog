import networkx as nx
import matplotlib.pyplot as plt
import sys
import math
import pandas as pd

def get_zero_divisors(n):
    """
    Finds all zero divisor pairs in Z_n using a brute-force approach.
    A pair (x, y) is a zero divisor pair if x*y % n == 0.
    """
    zero_divisors = []
    for x in range(n):
        for y in range(n):
            if (x * y) % n == 0:
                zero_divisors.append((x, y))
    return zero_divisors

def get_ann(x, n, zero_divisors):
    """
    Calculates ann(x) for a given x in Z_n.
    ann(x) is the set of all y such that (x, y) is a zero divisor pair.
    """
    ann_x = set()
    for a, b in zero_divisors:
        if a == x:
            ann_x.add(b)
    return ann_x

def get_ann_of_set(s, n, zero_divisors):
    """
    Calculates ann({x, y, z, ...}) for a given set in Z_n.
    This is the intersection of ann(i) for all i in the set.
    """
    if not s:
        return set(range(n))
    
    ann_sets = [get_ann(i, n, zero_divisors) for i in s]
    
    intersection = ann_sets[0]
    for i in range(1, len(ann_sets)):
        intersection = intersection.intersection(ann_sets[i])
        
    return intersection

def get_exact_zero_divisors(n, zero_divisors):
    """
    Finds all exact zero divisor pairs (x, y) in Z_n.
    (x, y) is an exact zero divisor pair if ann(x) == ann(ann(y)).
    """
    exact_zero_divisors = []
    all_anns = {i: get_ann(i, n, zero_divisors) for i in range(n)}
    all_ann_anns = {i: get_ann_of_set(all_anns[i], n, zero_divisors) for i in range(n)}

    for x in range(n):
        for y in range(n):
            if all_anns[x] == all_ann_anns[y]:
                exact_zero_divisors.append((x, y))
    return exact_zero_divisors

def draw_zero_divisor_graph(n, zero_divisors, save_graph=False):
    """
    Generates a readable and organized zero divisor graph, especially for dense cases.
    Uses a tuned spring layout to prevent node and edge clutter.
    """
    G = nx.Graph()
    nodes_with_edges = set()
    edges = set()
    self_loops_nodes = set()

    for x, y in zero_divisors:
        if x == 0 or y == 0:
            continue
        
        nodes_with_edges.add(x)
        nodes_with_edges.add(y)
        if x == y:
            self_loops_nodes.add(x)
        else:
            edges.add(tuple(sorted((x, y))))

    G.add_nodes_from(sorted(list(nodes_with_edges)))
    G.add_edges_from(list(edges))

    if not G.nodes():
        print(f"Z_{n} has no non-zero zero divisors. Graph is empty.")
        return

    # Use a much larger figure to give the graph space
    plt.figure(figsize=(20, 20))
    
    pos = {}
    if G.number_of_nodes() > 0:
        # Use a tuned spring layout for better aesthetics in dense graphs
        # k controls the optimal distance between nodes. Larger k = more spread.
        # iterations ensures the layout settles into a stable position.
        # seed ensures the layout is the same every time.
        k_val = 2.5 / math.sqrt(G.number_of_nodes())
        pos = nx.spring_layout(G, k=k_val, iterations=100, seed=42)
    
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    nx.draw_networkx_edges(G, pos, width=1.5, alpha=0.6, edge_color='gray')
    nx.draw_networkx_labels(G, pos, font_size=14, font_color='red', font_weight='bold')

    # Draw self-loops manually as clean arcs
    ax = plt.gca()
    for node in self_loops_nodes:
        if node in pos:
            # A fixed radius in data coordinates works well with spring_layout's normalization
            arc = plt.Circle(pos[node], 0.05, color='gray', fill=False, lw=1.5, alpha=0.6)
            ax.add_patch(arc)

    plt.title(f"Zero Divisor Graph Γ(Z_{n})", fontsize=22)
    plt.axis('off')
    plt.tight_layout()

    if save_graph:
        plt.savefig(f"zero_divisor_graph_Z_{n}.png", bbox_inches='tight')
        print(f"Zero divisor graph saved as zero_divisor_graph_Z_{n}.png")
    else:
        plt.show()

def draw_exact_zero_divisor_graph(n, exact_zero_divisors, save_graph=False):
    """
    Generates the exact zero divisor graph with separated components for clarity.
    Uses an undirected graph to represent the symmetric relationship.
    """
    G = nx.Graph() # Use an undirected graph as relationship is symmetric
    nodes_with_edges = set()
    edges_to_add = set()

    # Create a lookup for quick check of symmetric pairs
    ezd_pairs = set(exact_zero_divisors)

    for x, y in exact_zero_divisors:
        if x == 0 or y == 0 or x == y:
            continue
        
        # Add edge only if the relationship is symmetric
        if (y, x) in ezd_pairs:
            edge = tuple(sorted((x, y)))
            if edge not in edges_to_add:
                nodes_with_edges.add(x)
                nodes_with_edges.add(y)
                edges_to_add.add(edge)

    G.add_nodes_from(sorted(list(nodes_with_edges)))
    G.add_edges_from(list(edges_to_add))
    
    if not G.nodes():
        print(f"Z_{n} has no non-trivial symmetric exact zero divisors. Graph is empty.")
        return

    # Find and draw connected components in separate subplots
    components = list(nx.connected_components(G))
    num_components = len(components)
    
    if num_components == 0:
        return

    # Arrange subplots in a grid
    cols = int(math.ceil(math.sqrt(num_components)))
    rows = int(math.ceil(num_components / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(8 * cols, 8 * rows), squeeze=False)
    axes = axes.flatten()

    fig.suptitle(f"Exact Zero Divisor Graph for Z_{n}", fontsize=20)

    for i, comp_nodes in enumerate(components):
        comp = G.subgraph(comp_nodes).copy()
        ax = axes[i]
        pos = nx.kamada_kawai_layout(comp)
        
        nx.draw_networkx_nodes(comp, pos, ax=ax, node_color='lightgreen', node_size=1500)
        nx.draw_networkx_edges(comp, pos, ax=ax, width=1.5, alpha=0.8, edge_color='gray')
        nx.draw_networkx_labels(comp, pos, ax=ax, font_size=12, font_color='black', font_weight='bold')
        ax.axis('off')

    # Hide any unused subplots
    for i in range(num_components, len(axes)):
        axes[i].axis('off')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if save_graph:
        plt.savefig(f"exact_zero_divisor_graph_Z_{n}.png", bbox_inches='tight')
        print(f"Exact zero divisor graph saved as exact_zero_divisor_graph_Z_{n}.png")
    else:
        plt.show()

def get_exact_components(n, exact_zero_divisors):
    G = nx.Graph()
    nodes_with_edges = set()
    edges_to_add = set()

    ezd_pairs = set(exact_zero_divisors)

    for x, y in exact_zero_divisors:
        if x == 0 or y == 0 or x == y:
            continue
        
        if (y, x) in ezd_pairs:
            edge = tuple(sorted((x, y)))
            if edge not in edges_to_add:
                nodes_with_edges.add(x)
                nodes_with_edges.add(y)
                edges_to_add.add(edge)

    G.add_nodes_from(sorted(list(nodes_with_edges)))
    G.add_edges_from(list(edges_to_add))
    
    component_descs = []
    components = list(nx.connected_components(G))

    for comp_nodes in components:
        if not comp_nodes:
            continue
        sub = G.subgraph(comp_nodes)
        num_nodes = sub.number_of_nodes()
        num_edges = sub.number_of_edges()

        # Check if clique
        if num_edges == num_nodes * (num_nodes - 1) // 2:
            component_descs.append((num_nodes,))
            continue

        # Check if complete bipartite
        if nx.is_bipartite(sub):
            color = nx.bipartite.color(sub)
            A = [node for node in sub if color[node] == 0]
            B = [node for node in sub if color[node] == 1]
            a, b = len(A), len(B)
            expected = a * b
            if num_edges == expected:
                component_descs.append((min(a, b), max(a, b)))
                continue

        # If neither, log warning
        print(f"Warning: Unknown component type for n={n}, nodes={comp_nodes}")

    # Sort the descriptions for consistent order
    component_descs.sort(key=lambda t: (len(t), t))
    return component_descs

def build_catalog(max_n=100):
    catalog = []
    for n in range(2, max_n + 1):
        zero_divisors = get_zero_divisors(n)
        exact_zero_divisors = get_exact_zero_divisors(n, zero_divisors)
        comps = get_exact_components(n, exact_zero_divisors)
        comp_str = ','.join(
            str(t[0]) if len(t) == 1 else f'({t[0]},{t[1]})' for t in comps
        )
        catalog.append({
            'n': n,
            'exact_components': comp_str if comp_str else 'None',
            'components': comps  # For filtering
        })
    df = pd.DataFrame(catalog)
    return df

def filter_df(df, required_comps):
    """
    Filter the DataFrame to include only rows where all required_comps
    are present in the 'components' list.
    required_comps: list of tuples, e.g., [(1,8), (2,8)]
    """
    def has_all(row):
        for req in required_comps:
            if req not in row['components']:
                return False
        return True
    filtered = df[df.apply(has_all, axis=1)]
    return filtered

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 catalog.py <mode> [args]")
        print("Modes:")
        print("  graph <n> [-s]: Generate graphs for a specific n (as before)")
        print("  catalog <max_n>: Build and print catalog up to max_n")
        print("  filter <max_n> <comp1> <comp2> ...: Build catalog and filter for components")
        print("    Components format: '4' for cliques, '(1,8)' for bipartite")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "graph":
        try:
            n = int(sys.argv[2])
        except:
            print("Error: Provide n as integer.")
            sys.exit(1)
        save_graph = '-s' in sys.argv
        print(f"Generating graphs for Z_{n}...")
        zero_divisors = get_zero_divisors(n)
        exact_zero_divisors = get_exact_zero_divisors(n, zero_divisors)
        print("Drawing Zero Divisor Graph...")
        draw_zero_divisor_graph(n, zero_divisors, save_graph)
        print("Drawing Exact Zero Divisor Graph...")
        draw_exact_zero_divisor_graph(n, exact_zero_divisors, save_graph)
        print("Done.")

    elif mode == "catalog":
        try:
            max_n = int(sys.argv[2])
        except:
            max_n = 100
        print(f"Building catalog up to {max_n}...")
        df = build_catalog(max_n)
        print(df[['n', 'exact_components']])
        df.to_csv(f"catalog_up_to_{max_n}.csv", index=False)
        print(f"Catalog saved to catalog_up_to_{max_n}.csv")

    elif mode == "filter":
        try:
            max_n = int(sys.argv[2])
            comp_strs = sys.argv[3:]
        except:
            print("Error: Provide max_n and components.")
            sys.exit(1)
        required_comps = []
        for s in comp_strs:
            if '(' in s:
                a, b = map(int, s.strip('()').split(','))
                required_comps.append((min(a,b), max(a,b)))
            else:
                required_comps.append((int(s),))
        print(f"Building catalog up to {max_n} and filtering for {comp_strs}...")
        df = build_catalog(max_n)
        filtered = filter_df(df, required_comps)
        print(filtered[['n', 'exact_components']])

    else:
        print("Unknown mode.")
        sys.exit(1)