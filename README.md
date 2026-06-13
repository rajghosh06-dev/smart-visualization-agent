# Smart Visualization Agent

An offline-first, local AI-powered dashboard designed to ingest tabular datasets (CSV and Microsoft Excel formats) and generate interactive visualizations directly from natural language prompts. This project runs entirely offline on local hardware, ensuring data privacy and zero cloud execution costs.

---

## Technical Overview

The **Smart Visualization Agent** integrates a FastAPI backend with a modern, responsive single-page application (SPA) frontend. User queries are interpreted using a hybrid parsing pipeline that combines a local quantized Large Language Model (LLM) with a highly optimized, rule-based heuristic processor. Interactive visualizations are generated server-side using Plotly and rendered client-side.

### Key Architecture Components

*   **FastAPI Backend Server**: Exposes asynchronous endpoints for listing files, uploading new datasets, retrieving system metrics (such as local LLM download/loading status), and performing natural language visualization parsing.
*   **Hybrid Parser Coordinator (`core/parser.py`)**:
    *   *Local LLM Inference*: Integrates the `gpt4all` Python SDK to run the quantized 3B-parameter `orca-mini-3b-gguf2-q4_0.gguf` model. To prevent server blocks, the model downloads and loads asynchronously in a background thread.
    *   *Rule-Based NLP Engine*: A zero-setup, zero-RAM keyword mapping processor that utilizes regex token matching and data-type priority mapping (e.g. categorical vs. numeric) to resolve chart parameters instantly. Serves as a 100% reliable fallback during offline execution or model loading.
*   **Visualizer Engine (`core/visualization.py`)**: Uses Plotly Express to generate chart configurations (supporting bar, line, scatter, histogram, and pie charts). Applies a custom dark-mode design system to match the user interface.
*   **Single-Page Interface**: Built with high-fidelity glassmorphism panels, glowing indicator states, a live spreadsheet viewer, manual overrides, and a visual history card for restoring previous charts.

---

## Directory Structure

```
smart-visualization-agent/
│
├── app/                     # Web Application Layer
│   ├── static/              # Static Frontend Assets
│   │   ├── script.js        # DOM events, uploader, chart restoration, manual overrides
│   │   └── style.css        # Dashboard styling system, glassmorphism layout, animations
│   ├── templates/           # HTML Templates
│   │   └── index.html       # Single-Page Dashboard structure
│   ├── main.py              # Application entry point & lifespan events
│   └── routes.py            # API routes (upload, visualize, dataset listing, status)
│
├── core/                    # Computational & Inference Layer
│   ├── parser.py            # Natural language processing (LLM & heuristic NLP parser)
│   └── visualization.py     # Plotly Express engine & design customization
│
├── data/                    # Dataset Storage Directory
│   ├── sample.csv           # Default US Exports dataset
│   └── sample2.csv          # Secondary comparison dataset
│
├── tests/                   # Verification Layer
│   └── test_parser.py       # pytest test suite
│
├── requirements.txt         # Project Dependencies list
└── README.md                # Documentation
```

---

## System Requirements

*   **Operating System**: Windows 10/11, macOS (10.15+), or Linux (Ubuntu 20.04+).
*   **Python**: Version 3.9 or higher (Tested on Python 3.14).
*   **System RAM**: 8 GB minimum (16 GB recommended for optimal local LLM performance).
*   **Disk Space**: ~2.5 GB of free space (required for downloading the local quantized LLM model).

---

## Installation & Setup

Follow these steps to configure the environment and run the application locally.

### 1. Set Up and Activate Virtual Environment
Use the global Python virtual environment configured for your workspace:
```powershell
# On Windows (PowerShell)
& "C:\MyEnv\Scripts\Activate.ps1"
```

### 2. Install Project Dependencies
Run `pip` to install the package requirements listed in `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 3. Launch the Application Server
Run the FastAPI development server using `uvicorn`:
```powershell
uvicorn app.main:app --reload
```

The application will launch on your local host: **`http://127.0.0.1:8000`**

---

## Operating Instructions & Workflow

1.  **Ingest Dataset**:
    *   Select a pre-loaded sample dataset (like `sample.csv` or `sample2.csv`) from the sidebar.
    *   Alternatively, drag and drop a custom CSV or Excel (`.xlsx`/`.xls`) file into the drop zone.
2.  **Verify Schema**:
    *   The **Dataset Preview** panel at the bottom will render the first 5 rows and indicate column data types (categorical vs. numeric).
3.  **Submit Visual Query**:
    *   Type a natural language command into the prompt input box and hit **Generate Chart** (or press Enter).
    *   *Example Queries*:
        *   `Show total exports by state` (renders a bar chart)
        *   `Scatter plot poultry vs total exports` (renders a scatter plot)
        *   `Line chart of dairy production` (renders a line plot)
        *   `Compare corn and wheat exports` (renders a grouped multi-series comparison chart)
        *   `Histogram of cotton values` (renders a distribution histogram)
4.  **Local LLM Syncing**:
    *   Upon application startup, the local LLM (`orca-mini-3b-gguf2-q4_0.gguf`) begins downloading in the background.
    *   The sidebar indicator status displays **LLM: Loading...** while downloading and **LLM: Ready** once loaded.
    *   If the LLM is loading or download fails, the agent uses the heuristic NLP engine immediately. You can manually force the parsing mode using the headers button group.
5.  **Refine & Correct**:
    *   If the agent maps an incorrect column or chart type, expand the **Manual Chart Adjustments** panel to override and select your axes directly.
6.  **Toggle History**:
    *   Click on any past query in the **Session History** list to instantly reload the chart.

---

## Running the Verification Suite

Unit tests verify that column mapping and chart parameters are generated correctly. To run the automated test suite, execute:
```powershell
python -m pytest tests/
```
