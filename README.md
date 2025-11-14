# Zero Divisor Graph Catalog Database

A comprehensive system for generating, storing, and querying zero divisor graphs and exact zero divisor graphs for modular arithmetic rings Z_n. The system uses SQLite for portable data storage and allows for efficient graph generation from stored structures.
Features

    Dual Graph Generation: Generate both zero divisor graphs AND exact zero divisor graphs for any n

    High-Quality Visualization: Uses optimized spring layouts with large, readable graphs (20x20 inches) and proper component separation

    Database Storage: Store both graph structures and components in a portable SQLite database

    Fast Graph Rendering: Generate graphs instantly from stored structures without recalculation

    Component Filtering: Find numbers n that contain specific graph components (cliques or bipartite graphs)

    Catalog Generation: Create tables displaying n values with their exact components

    Interactive Querying: Explore structure data interactively

    Scalable: Easily extendable to large n values with efficient storage

# Project Structure
```
Research-Project/
├── database.py    
├── init_database.py         
├── populate_db.py           
├── graph_generator.py       
├── query_structures.py      
├── analyze_components.py    
├── test_enhanced_queries.py 
├── catalog.py               
├── zero_divisor_catalog.db  
├── requirements.txt         
└── README.md                
```
# Installation

Clone or download the project files

Install required dependencies:
 
```
pip install -r requirements.txt
```
# Quick Start
### Step 1: Initialize the Database
```
python init_database.py
```
This creates the SQLite database with the proper schema.
### Step 2: Populate with Data
```
# Populate n=1 to 100
python populate_db.py 1 100

# Populate specific range
python populate_db.py 1 50
```
### Step 3: Generate High-Quality Graphs
```
# Generate zero divisor graph (large 20x20 layout)
python graph_generator.py zero 12

# Generate exact zero divisor graph (separated components)
python graph_generator.py exact 12

# Save graphs to PNG files
python graph_generator.py zero 12 -s
python graph_generator.py exact 12 -s
```
# Detailed Usage
## Database Initialization
```
python init_database.py

    Creates zero_divisor_catalog.db SQLite database

    Sets up MyNumber and ExactConnection tables with enhanced schema

    Includes proper indexes for fast querying
```

## Data Population
```
# Populate default range
python populate_db.py 1 100

# Populate custom range
python populate_db.py 50 150
python populate_db.py 200 300

# Add more entries incrementally
python populate_db.py 101 200

The population script calculates and stores:

    Zero divisor graphs: Vertices, edges, and structure

    Exact zero divisor graphs: Vertices, edges, and structure

    Component analysis: Complete and bipartite components

    Component descriptions: In format "(1,8),(2,4),(2,4),(2,8)"
```

## Graph Generation

### Zero Divisor Graphs (20x20 inch layout, optimized spring algorithm):
```
python graph_generator.py zero 6
python graph_generator.py zero 12
python graph_generator.py zero 24
python graph_generator.py zero 48 -s  # Save to file
```
### Exact Zero Divisor Graphs (separated components in subplots):
```
python graph_generator.py exact 6
python graph_generator.py exact 12  
python graph_generator.py exact 24
python graph_generator.py exact 48 -s  # Save to file
```

### Graph Features:

    Large 20x20 inch figures for readability

    Optimized spring layout prevents node clustering

    Red node labels with bold font for visibility

    Gray edges with proper transparency

    Exact graphs show components in separate subplots

    Kamada-Kawai layout for component aesthetics

## Catalog and Search

### Display Catalog Table:
```
python graph_generator.py catalog 20
python graph_generator.py catalog 50
python graph_generator.py catalog 100
```

### Search by Components:
```
# Find numbers with specific bipartite component
python graph_generator.py search "(1,8)"

# Find numbers with specific clique
python graph_generator.py search "4"

# Find numbers with multiple components
python graph_generator.py search "(1,8)" "(2,8)"
```

## Interactive Structure Exploration

### Explore stored graph structures:
```
python query_structures.py
```

Interactive features:

    View all available n values

    Query specific n values or ranges

    See both zero divisor and exact zero divisor structures

    View raw JSON data

### Find interesting entries:
```
python analyze_components.py
```

Shows:

    Numbers with most components

    Largest bipartite graphs

    Largest cliques

    Numbers with diverse component types

### Database Schema MyNumber Table

    entry_id (PK): Auto-incrementing primary key

    nvalue: The modulus n for Z_n

    zvertices, zedges: Zero divisor graph data (JSON)

    z_structure: Zero divisor graph structure for fast rendering (JSON)

    ezvertices, ezedges: Exact zero divisor graph data (JSON)

    ez_structure: Exact zero divisor graph structure for fast rendering (JSON)

    exact_components_desc: Component description like "(1,8),(2,4),(2,4),(2,8)"

    partition_count: Number of connected components

ExactConnection Table

    connection_id (PK): Auto-incrementing primary key

    entry_id (FK): Reference to MyNumber

    component_type: 'complete' or 'bipartite'

    p1, p2: Parameters (for bipartite: p1, p2; for complete: p1, NULL)

Component Notation

    (k,) or k: Complete graph (clique) K_k

    (a,b): Complete bipartite graph K_{a,b}

Component Filtering:
```
# "provide a list of n such that (1,8) and (2,8) are among the exact components"
results = db.find_by_exact_components([(1, 8), (2, 8)])
# Returns n=48, among others
```

## Graph Quality Features

The system produces publication-quality graphs:

### Zero Divisor Graphs:

    20×20 inch figure size

    Tuned spring layout: k = 2.5/√n, 100 iterations

    Large nodes (size 2000) with light blue color

    Bold red labels (font size 14)

    Gray edges with width 1.5 and alpha 0.6

### Exact Zero Divisor Graphs:

    Components displayed in separate subplots

    Kamada-Kawai layout for each component

    Light green nodes (size 1500)

    Black bold labels (font size 12)

    Automatic grid arrangement

### Performance Notes

    Stored Structures: Both graph types generated instantly from structures

    High-Quality Rendering: Optimized layouts prevent clustering even for dense graphs

    Population: Initial calculation can be intensive for large n

    Query Performance: Indexed for fast component-based searching

    Storage: SQLite database is portable and efficient (~100KB for n=1-100)

### Tree Diagram Support

The database structure supports creating tree diagrams where:

    Leaves: Exact components (K_a, K_{b,c})

    Branches: Exact zero divisor graphs

    Roots: Zero divisor graphs

## Common Workflows

### Research Analysis
```

# 1. Find interesting numbers
python analyze_components.py

# 2. Explore their structures
python query_structures.py

# 3. Generate publication-quality graphs
python graph_generator.py exact 48 -s
python graph_generator.py zero 48 -s

# 4. Search for patterns
python graph_generator.py search "(1,8)" "(2,8)"
```

### Incremental Research
```
# Start with small range

python populate_db.py 1 50

# Analyze and generate graphs
python graph_generator.py catalog 50
python analyze_components.py

# Expand research
python populate_db.py 51 100
python graph_generator.py catalog 100
```

# Troubleshooting

**Database errors:** Delete zero_divisor_catalog.db and rerun init_database.py

**Missing dependencies:** Run pip install -r requirements.txt

**Graph generation fails:** Ensure database is populated for that n value

**Small/clustered graphs:** Use graph_generator.py (not the old graph_from_structure.py)

**Structure queries:** Use python query_structures.py to inspect stored data
# Requirements
```
networkx>=3.0
matplotlib>=3.5
pandas>=1.4
```