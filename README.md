
# Zero Divisor Graph Catalog  
**A Research Tool for Ring Theory & Graph Theory**


## Overview

The **Zero Divisor Graph Catalog** is a comprehensive system for computing, storing, analyzing, and visualizing **zero divisor graphs** in the rings **Zₙ** (integers modulo n).

### What It Does
For any **n**, it computes:
- **Zero divisors**: pairs (x,y) such that x·y ≡ 0 (mod n)
- **Exact zero divisors**: pairs where ann(x) = ann(ann(y))
- **Graph components**: connected components of the exact zero divisor graph
  - **Complete cliques** Kₖ
  - **Complete bipartite graphs** Kₐ,₆
- **Interactive frontend**: search, filter, generate graphs
- **High-quality PNG export** via `graph_generator.py`

### Key Features
| Feature | Description |
|-------|-----------|
| **Dual Graphs** | Zero divisor graph + exact zero divisor graph |
| **Component Search** | Find all n with K₄, or K₁,₈, etc. |
| **Scalable Storage** | Full graphs for n ≤ 6150, summaries for n > 6150 |
| **Interactive UI** | `client_frontend.html` + Flask API |
| **Publication-Ready Graphs** | 20×20 inch, optimized spring layout |
| **CSV Export** | Full catalog download |

---

## Prerequisites
```
python
pip
sqlite3
```

## Installation

```
cd /home/project/Research-Project
pip install flask flask-cors networkx matplotlib pandas
```

## Database Setup & Population
### Step 1: Initialize the Database
```
python init_database.py
```
- Creates `zero_divisor_catalog.db`
- Sets up two tables:
    - MyNumber: main data (n, structures, counts)
    - ExactConnection: component types and sizes

### Step 2: Populate the Database
```
# a = any starting integer, b = any ending integer
python populate_db.py a b

# OR
# Run the job in the background (non-interactive for remote population)
nohup python populate_db.py 6151 10000 > logs/populate.log 2>&1 &
```

### Storage Modes
|n Range | Storage |
|---|---|
| n ≤ 6150 | "Full vertices edges, self-loops (JSON)" |
| n > 6150 | "Only component summary (""0"" for large fields)" |
>Use tail -f logs/populate.log to monitor progress.

### Step 3: Verify Data
```
sqlite3 zero_divisor_catalog.db "SELECT nvalue, exact_components_desc FROM MyNumber LIMIT 5;"
```
Example:
```
6|(1,2),(1,3),(2,3)
8|(1,2),(1,4),(2,4)
```
## Running the System
### Option A: Remote Server (Production Environment)
*Note, for this method, all files EXCEPT `client_frontend.html` should be uploaded to your server.
```
# cd into project directory
# Start API
nohup python server_app.py > logs/server.log 2>&1 &
```
> Users connect via SSH tunnel → see READMETOO.md

---

### Option B: Local Development
*All files should be stored locally in one directory.
```
# pip install all requirements
# Start API locally
python server_app.py
```
- Runs on http://127.0.0.1:5000
- Open `client_frontend.html` → connects automatically
---
## Script Reference
| Script | Command | Purpose |
| --- | --- | --- |
| init_database.py | python init_database.py | Create DB |
populate_db.py | python populate_db.py a b | Add Zₙ data for range (a, b) |
| server_app.py | nohup python server_app.py & | Non-Interactive Production API |
| app.py | python server_app.py | Local/Interactive API |
| graph_generator.py | python graph_generator.py zero a | Generate zero divisor graph of n = a |
| graph_generator.py | python graph_generator.py exact a | Generate exact zero divisor graph of n = a |
| graph_generator.py | python graph_generator.py exact a -s | Save PNG |
| catalog.py | python catalog.py catalog 100 | Export CSV |
| analyze_components.py | python analyze_components.py | Find large cliques, mixed types |
| query_structures.py | python query_structures.py | View raw JSON for entry attributes |
| delete_entry.py | python delete_entry.py a | Remove entry n = a |

## API Endpoints
| Route | Method | Params | Purpose |
| --- | --- | --- | --- |
| /api/health | GET | — | Server status |
| /api/entries | GET | start_n, end_n, components, exact_match | Search & filter | 
| /api/export/csv | GET | — | Download full catalog |
| /api/graph/<n> | GET| n ≤ 5500 | Get graph JSON
---

## Database Schema
### MyNumber Table
```
nvalue, z_structure, ez_structure, exact_components_desc,
zvertices_count, zedges_count, partition_count, complete, complete_bipartite
```
### ExactConnection Table
```
entry_id, component_type ('complete'/'bipartite'), p1, p2
```

## Graph Generation
```
# Zero divisor graph (20×20 inch)
python graph_generator.py zero 24

# Exact zero divisor graph (subplots)
python graph_generator.py exact 24 -s
```
**OR**

The `client_frontend.html` interface contains a `**Generate Graph**` button that will construct the graphs within the browser.

## Monitoring & Management
### Check if server_app.py is running
```
ps aux | grep server_app.py
```
### Check population progress
```
tail -f logs/populate.log
```

## User Access

- **Frontend:** `client_frontend.html`
- **Instructions:** See `README.md` and `READMETOO.md`
- **SSH Tunnel:** Required for remote access



## Customization
### Customize Graph Storage Limit (n ≤ X)
**By default:**
- **n ≤ 6150:** Full graph structures (vertices, edges, self-loops) are stored
- **n > 6150:** Only component summaries; (`"0"`) to save space, no edge/vertex data

**To change this threshold:**
- Edit `populate_db.py`
- Find and replace all instances of `6150` with your desired threshold
- Save your changes

### Change the Deployment Server
**To run the catalog on a different server:**
1. Go to line 368 in `client_frontend.html`:
```
# Replace SERVER_NAME.DOMAIN.ORG to your server address
<strong>Server:</strong> SERVER_NAME.DOMAIN.ORG:5000
```
> **Do NOT change** `SERVER_BASE_URL` in `client_frontend.html` — it must stay `localhost:5000` (SSH tunnel handles routing).

## Troubleshooting
| Issue | Fix |
| --- | --- |
| 500 on graph load | Ensure n ≤ 5500 and z_structure != "0" |
| DB locked | Only one writer at a time |
| Port 5000 busy | pkill -f server_app.py |
|No data for n | Run populate_db.py |

## Contact
*gmhensley26@gmail.com*