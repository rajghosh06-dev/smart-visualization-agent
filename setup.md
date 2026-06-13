# Setup Instructions - Smart Visualization Agent

This guide provides detailed setup instructions to configure the environment, install required dependencies, and launch the **Smart Visualization Agent** server on your local machine.

---

## 1. Quick Start (Brief Setup)

For experienced developers, here is the quick copy-paste block to get the app running:

```powershell
# 1. Activate the environment (using your workspace environment)
& "C:\MyEnv\Scripts\Activate.ps1"

# 2. Install requirements
pip install -r requirements.txt

# 3. Start the FastAPI development server
uvicorn app.main:app --reload
```

*Open your web browser and navigate to **`http://127.0.0.1:8000`**.*

---

## 2. Detailed Prerequisites

Before setting up, ensure your machine satisfies the following hardware and software checks:

1.  **Python Version**: Python 3.9 up to Python 3.14 (fully verified and optimized for Python 3.14).
2.  **System RAM**: 
    *   *Minimum*: 8.0 GB (allows running in Rule-Based Heuristic Mode).
    *   *Recommended*: 16.0 GB (allows loading the quantized local LLM model safely in memory).
3.  **Storage Space**: ~2.5 GB of free space is required on the target drive to download and save the offline model weights.
4.  **CPU Extensions**: The CPU must support **AVX or AVX2** vector instructions (checked automatically at boot) for quantized local inference.

---

## 3. Step-by-Step Installation

### Step 1: Open the Project Directory
Launch your terminal (PowerShell is recommended on Windows) and navigate to the project directory:
```powershell
cd "D:\RAJ\GITHUB_REPOSITORY\Microsoft-AI-INNOVATION-STUDIO\smart-visualization-agent"
```

### Step 2: Activate the Virtual Environment
To keep your system python packages clean, activate the dedicated virtual environment:
```powershell
# Windows (PowerShell)
& "C:\MyEnv\Scripts\Activate.ps1"

# macOS / Linux (Terminal)
source /path/to/your/env/bin/activate
```

### Step 3: Install Required Packages
Install all libraries listed in the `requirements.txt` file. This installs FastAPI, Uvicorn, Pandas, OpenPyXL (for Excel support), Plotly, and GPT4All:
```powershell
pip install -r requirements.txt
```

### Step 4: Model Ingestion (Offline Setup)
The coordinator expects the model file to reside inside `core/models/`.
*   **Automatic Download**: When the server is running, system compatibility checks are run. If your machine passes, a **Download Model** button appears in the sidebar. Click it to trigger an asynchronous background download of `orca-mini-3b-gguf2-q4_0.gguf` (1.98 GB).
*   **Manual Download**: If you prefer, download the quantized `orca-mini-3b-gguf2-q4_0.gguf` model from the official GPT4All repository and place it directly in the `/core/models/` folder.

---

## 4. Running the Dashboard

Launch the ASGI server using `uvicorn`:
```powershell
uvicorn app.main:app --reload
```
*   `--reload`: Automatically restarts the server when code files are modified.
*   `--host 0.0.0.0` (Optional): Allows other devices on your local Wi-Fi/Ethernet network to access the dashboard.

### Accessing the Web Application
Open your web browser and enter the address:
```
http://127.0.0.1:8000
```

---

## 5. Troubleshooting & Diagnostics

*   **AVX Support Warning**: If the dashboard states *Local LLM: Unsupported (Hardware AVX Missing)*, your CPU cannot run llama.cpp models. The dashboard automatically switches to **Rule-Based Heuristic Mode**. You do not need to do anything; data visualization prompts will still generate charts instantly using the heuristic engine.
*   **NVIDIA CUDA ModNotFound (0x7e) Warnings**: If you see CUDA warnings in your terminal logs during startup, they are harmless scans performed by the model engine. It will gracefully fall back to CPU AVX execution.
*   **Port 8000 Blocked**: If another process is using port 8000, start the server on a custom port:
    ```powershell
    uvicorn app.main:app --reload --port 8080
    ```
