# Smart Visualization Agent - User Guide

Welcome to the **Smart Visualization Agent** guide! This document explains how to use the dashboard, load datasets, write prompts, toggle themes, and customize layouts.

---

## 1. Loading Datasets

The dashboard parses CSV and Microsoft Excel files. There are two ways to load your tables:

### Option A: Use the Web Uploader
1. Drag and drop any `.csv`, `.xlsx`, or `.xls` file directly over the dashed upload area in the left sidebar.
2. Alternatively, click **Drag & drop or browse** to open the browser file picker and select your file.
3. The dashboard will upload, process, and automatically select the file.

### Option B: Copy Files Directly to the Data Folder
1. Locate your files on your computer.
2. Copy and paste them into the project's `data/` directory (located at the root level of this repository).
3. Refresh the web browser page. The sidebar will automatically discover and display the files in the list!

*Once loaded, click on any dataset in the sidebar list to make it the active dataset. The **Dataset Preview** table at the bottom will load the first 5 rows and display column data types (categorical vs. numeric).*

---

## 2. Phrasing Natural Language Queries

The agent parses natural language commands to extract the chart type and coordinates (X and Y columns).

### Supported Visualizations
*   **Bar Chart**: Best for comparisons of numeric values across categories.
*   **Line Chart**: Great for trends over time or sequential categories.
*   **Scatter Plot**: Perfect for correlating two numeric variables.
*   **Histogram**: Displays the distribution of a single numeric column.
*   **Pie Chart**: Represents proportions of a whole (best for single series).

### Example Prompt Guide
Here are examples showing how to frame prompts to target columns:
*   *Simple Bar*: `"Show total exports by state"`
*   *Multi-Series Bar*: `"Compare corn and wheat exports"` (creates grouped bars for `corn` and `wheat` columns)
*   *Correlation Scatter*: `"Scatter plot poultry vs total exports"`
*   *Trend Line*: `"Line chart of dairy production"`
*   *Distribution Histogram*: `"Histogram of cotton values"`

### Column Matching Logic
If your dataset column names contain spaces or abbreviations (e.g. `Total_Exports` or `exports_2026`), the parser uses semantic keyword matches to align them. If the parser makes an incorrect guess, you can override it.

---

## 3. Manual Adjustments & Overrides

If you want to manually tune a chart or correct a parser column mapping:
1. Click the **Manual Chart Adjustments** panel to expand it.
2. Select your desired **Chart Type** (Bar, Line, Scatter, etc.) from the dropdown.
3. Choose the column for the **X-Axis**.
4. Select one or more columns for the **Y-Axis** (hold `Ctrl` or `Cmd` to select multiple columns for comparative charts).
5. Click **Apply Adjustments**. The chart will re-render instantly.

---

## 4. Layout Controls: Collapsible Sidebar

To maximize your chart viewing area, especially on smaller screens:
*   Click the **double-chevron left icon (`<<`)** inside the top-left brand header. The sidebar will slide closed, allowing the visualization canvas to occupy the full width of the browser.
*   The Plotly chart **automatically scales and resizes** to fit the expanded container instantly.
*   To restore the sidebar, click the **double-chevron right icon (`>>`)** in the main content header.

---

## 5. Theme Controls: Dark & Light Mode

You can toggle between Dark (default) and Light theme layouts using the button in the top header:
*   Click the **Moon / Sun icon** button at the top-right next to the mode selectors.
*   **UI Components Transition**: All glassmorphic backgrounds, input selects, borders, buttons, and preview tables adapt automatically using CSS variables.
*   **Dynamic Plotly Update**: Since Plotly renders inside canvas/SVG containers, the dashboard dynamically restyles the gridlines, legend boxes, title text, and tick mark colors on the fly using `Plotly.relayout` so the chart stays fully legible and looks premium.

---

## 6. Understanding LLM States & Heuristics

The dashboard checks your machine compatibility at startup:
1.  **Checking...**: System compatibility metrics are running diagnostics.
2.  **Not Installed**: Hardware checks passed, but the 1.98 GB model weights are missing. Click **Download Model** to download it in the background.
3.  **Loading...**: The model is downloading/loading into memory.
4.  **Ready**: Local LLM mode is active.
5.  **Unsupported**: Hardware checks (CPU AVX features, RAM, disk) failed. The system **automatically locks into Heuristic Mode** to protect your machine's resources while keeping 100% of the charting functionality functional.
