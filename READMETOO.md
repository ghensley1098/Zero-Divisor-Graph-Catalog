# Zero Divisor Graph Catalog  
**Interactive Web Interface – User Guide**

---

## Overview

This guide shows **how to access** the **Zero Divisor Graph Catalog** from your local machine — **no installation required**.

The catalog runs on a **remote server** and is accessed via **SSH tunnel**. You will:
- Open an SSH tunnel
- Open `client_frontend.html` in your browser


---

## Prerequisites

| Requirement | Details |
|-----------|--------|
| **SSH Key** | `id_rsa` (or `.pem`) with access to the server, generated using Puttygen |
| **Locally Hosted Frontend** | `client_frontend.html` |
| **Web Browser** | Chrome, Firefox, or Edge |
| **Terminal** | Command Prompt (Windows), Terminal (Mac/Linux) |

---

## Step-by-Step Access

### Step 1: Download the Frontend

**Download** `client_frontend.html` to your local machine

---

### Step 2: Open SSH Tunnel

This forwards **your `localhost:5000`** → **server’s port 5000**

#### Windows (Command Prompt)
```
# Add your private key path and username/server address to this command
ssh -i "C:\path\to\your\private-key" -L 5000:localhost:5000 YourUsername@YourServer
```
#### Mac/Linux (Terminal)
```
# Add your private key path and username/server address to this command
ssh -i C:\path\to\your\private-key -L 5000:localhost:5000 YourUsername@YourServer
```
> Keep this window open — it’s your secure tunnel.

### Step 3: Start the Server (Only If Not Running)
In the SSH session, run:
```
cd /your/project/directory/

# Check if server is running
ps aux | grep server_app.py
```

- If you see python server_app.py → skip to Step 4
- If not → start it:
```
nohup python server_app.py > logs/server.log 2>&1 &
echo "Server started"
```
- Only one person should do this.
- If "port 5000 busy" → someone else is running it. Proceed to the next step.

### Step 4: Open the Interface

1. **Double-click** `client_frontend.html` on your local machine
2. It runs on: `http://localhost:5000` → goes through tunnel → reaches server
3. You’re in!
---

## Using the Interface
| Feature | How To Use |
| --- | ---|
| Search n Range | Enter start_n and end_n  |
| Filter Components | Type: any int a; any ordered pair (a, b); wildcards supported via blank space (e.g. (a, ))| 
|Exact Match |Check box → must have only listed components |
| Generate Graph | Click button (only for n ≤ 5500) | 

| Export CSV | Click Download CSV to download the full database as a .csv file |
