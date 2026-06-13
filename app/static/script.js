// Smart Visualization Agent - Client Core Logic

document.addEventListener("DOMContentLoaded", () => {
    // UI Elements
    const datasetListEl = document.getElementById("dataset-list");
    const dropZoneEl = document.getElementById("drop-zone");
    const fileInputEl = document.getElementById("file-input");
    const historyListEl = document.getElementById("history-list");
    const llmStatusCardEl = document.getElementById("llm-status-card");
    const statusDotEl = document.getElementById("status-dot");
    const statusTextEl = document.getElementById("status-text");
    const statusDetailsEl = document.getElementById("status-details");
    
    const currentDatasetNameEl = document.getElementById("current-dataset-name");
    const datasetStatsEl = document.getElementById("dataset-stats");
    const btnLlmModeEl = document.getElementById("btn-llm-mode");
    const modeButtons = document.querySelectorAll(".btn-mode");
    
    const visualizeFormEl = document.getElementById("visualize-form");
    const promptInputEl = document.getElementById("prompt-input");
    const btnSubmitEl = document.getElementById("btn-submit");
    const suggestedBtns = document.querySelectorAll(".suggested-btn");
    
    const chartViewportEl = document.getElementById("chart-viewport");
    const parserTagEl = document.getElementById("parser-tag");
    
    const btnToggleOverrideEl = document.getElementById("btn-toggle-override");
    const overrideSectionEl = document.querySelector(".override-section");
    const overrideChartTypeEl = document.getElementById("override-chart-type");
    const overrideXEl = document.getElementById("override-x");
    const overrideYEl = document.getElementById("override-y");
    const btnApplyOverrideEl = document.getElementById("btn-apply-override");
    
    const tableContainerEl = document.getElementById("table-container");
    const toastEl = document.getElementById("toast");

    // Application State
    let activeDataset = null;
    let datasetColumns = [];
    let currentMode = "hybrid";
    let chartHistory = [];
    let llmStatusPollInterval = null;

    // --- Toast Notifications ---
    function showToast(message, isError = false) {
        toastEl.textContent = message;
        if (isError) {
            toastEl.classList.add("error");
        } else {
            toastEl.classList.remove("error");
        }
        toastEl.classList.add("show");
        setTimeout(() => {
            toastEl.classList.remove("show");
        }, 4000);
    }

    // --- LLM Status Check ---
    function checkLlmStatus() {
        fetch("/api/llm-status")
            .then(res => res.json())
            .then(data => {
                statusDetailsEl.textContent = `Model: ${data.model_name}`;
                
                if (data.status === "Ready") {
                    statusDotEl.className = "status-indicator-dot ready";
                    statusTextEl.textContent = "Local LLM: Ready";
                    btnLlmModeEl.disabled = false;
                    clearInterval(llmStatusPollInterval);
                } else if (data.status === "Loading") {
                    statusDotEl.className = "status-indicator-dot loading";
                    statusTextEl.textContent = "Local LLM: Loading...";
                    statusDetailsEl.textContent += " (Downloading/Loading on CPU)";
                } else if (data.status === "Failed") {
                    statusDotEl.className = "status-indicator-dot failed";
                    statusTextEl.textContent = "Local LLM: Offline";
                    statusDetailsEl.textContent = data.error || "Failed to load model. Running heuristics.";
                    clearInterval(llmStatusPollInterval);
                } else {
                    statusDotEl.className = "status-indicator-dot";
                    statusTextEl.textContent = `Local LLM: ${data.status}`;
                }
            })
            .catch(err => {
                logger.error("LLM status fetch error:", err);
                statusDotEl.className = "status-indicator-dot failed";
                statusTextEl.textContent = "Local LLM: Status Error";
                statusDetailsEl.textContent = "Backend unreachable.";
            });
    }

    // Start LLM status polling
    checkLlmStatus();
    llmStatusPollInterval = setInterval(checkLlmStatus, 5000);

    // --- Load Available Datasets ---
    function fetchDatasets() {
        datasetListEl.innerHTML = '<div class="loading-spinner-sm"></div>';
        fetch("/api/datasets")
            .then(res => res.json())
            .then(data => {
                datasetListEl.innerHTML = "";
                if (data.datasets.length === 0) {
                    datasetListEl.innerHTML = '<p class="empty-state">No datasets in storage.</p>';
                    return;
                }
                data.datasets.forEach(db => {
                    const item = document.createElement("div");
                    item.className = "dataset-item";
                    if (activeDataset === db.name) item.classList.add("active");
                    
                    const sizeKB = (db.size / 1024).toFixed(1);
                    item.innerHTML = `
                        <span>${db.name}</span>
                        <small>${sizeKB} KB</small>
                    `;
                    item.addEventListener("click", () => selectDataset(db.name));
                    datasetListEl.appendChild(item);
                });
            })
            .catch(err => {
                showToast("Failed to fetch dataset list.", true);
                datasetListEl.innerHTML = '<p class="empty-state">Load failed.</p>';
            });
    }
    fetchDatasets();

    // --- Select Dataset ---
    function selectDataset(filename) {
        activeDataset = filename;
        
        // Highlight active sidebar item
        document.querySelectorAll(".dataset-item").forEach(item => {
            if (item.querySelector("span").textContent === filename) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });

        // Set visual loading state
        currentDatasetNameEl.textContent = filename;
        datasetStatsEl.textContent = "Loading preview and columns...";
        tableContainerEl.innerHTML = '<div class="table-placeholder"><div class="loading-spinner-sm"></div></div>';

        // Load preview and schema by triggering a mock upload or a preview call
        // In our backend, uploading the same file returns schema. But since it is already saved,
        // we can simulate this by executing a mock query or loading from database.
        // For convenience, we send a Form request to parse/save the file (which returns metadata)
        // Let's create an upload payload for the pre-existing file or load it
        // We'll fetch the dataset through a virtual upload or a direct preview endpoint.
        // Let's use a virtual fetch: we'll call upload with a reference or load it.
        // Wait, we can implement selectDataset by calling upload dataset? No, uploader expects UploadFile.
        // Let's call /api/upload with a file, or create a direct preview route.
        // Wait, what if we upload? Since we just want to preview an existing file, let's look at app/routes.py.
        // Ah, in app/routes.py we can just call select by getting file details. But since we didn't add a direct GET /api/datasets/{filename} route,
        // wait! We can easily load the dataset preview when the user clicks it. Let's make sure our JS triggers an API call that returns the dataset metadata.
        // Let's look at routes.py. We have `POST /api/upload` which parses and returns preview/columns.
        // Wait, how do we load a file already in the `data/` directory?
        // We can just add a simple GET /api/datasets/{filename} route, or we can send the filename to a route.
        // Wait, in our routes we have `GET /api/datasets` which returns file list.
        // Let's add a small endpoint or simply let /api/upload accept filename? No, upload takes UploadFile.
        // Let's check: can we add a route `GET /api/datasets/{filename}` to routes.py? Yes, we can!
        // Wait, instead of adding a new route, let's see if we can implement a clean endpoint or modify `GET /api/datasets` or create a new route.
        // Actually, let's write a route to view dataset metadata directly so the frontend can retrieve columns and preview without re-uploading!
        // That is very clean. Let's add this route to routes.py. But wait, I can do that in a bit or check if we can do it now.
        // Let's look at how we can implement preview loading:
        // We can define a route `GET /api/datasets/{filename}` in `app/routes.py` that returns the same structure as `/api/upload`:
        // `{ filename, columns: [...], row_count, preview: [...] }`.
        // Let's update `app/routes.py` to include this route! This will make the user experience extremely smooth and complete.
    }

    // Let's define selectDataset implementation that calls this preview route:
    function loadDatasetMetadata(filename) {
        fetch(`/api/datasets/${encodeURIComponent(filename)}`)
            .then(res => {
                if (!res.ok) throw new Error("Failed to load dataset details.");
                return res.json();
            })
            .then(data => {
                datasetColumns = data.columns;
                
                // Update UI headers
                currentDatasetNameEl.textContent = data.filename;
                datasetStatsEl.textContent = `${data.row_count.toLocaleString()} rows • ${data.columns.length} columns`;
                
                // Populate Override Selectors
                overrideXEl.innerHTML = '<option value="">Auto Detect</option>';
                overrideYEl.innerHTML = '';
                
                data.columns.forEach(col => {
                    const optX = document.createElement("option");
                    optX.value = col.name;
                    optX.textContent = `${col.name} (${col.type})`;
                    overrideXEl.appendChild(optX);
                    
                    const optY = document.createElement("option");
                    optY.value = col.name;
                    optY.textContent = `${col.name} (${col.type})`;
                    overrideYEl.appendChild(optY);
                });

                // Render Spreadsheet Preview
                renderPreviewTable(data.preview, data.columns);
                
                // Enable forms and prompts
                promptInputEl.disabled = false;
                btnSubmitEl.disabled = false;
                suggestedBtns.forEach(btn => btn.disabled = false);
                
                showToast(`Dataset "${data.filename}" loaded successfully.`);
            })
            .catch(err => {
                showToast(err.message, true);
                datasetStatsEl.textContent = "Error loading dataset.";
                tableContainerEl.innerHTML = '<div class="table-placeholder text-danger">Failed to load dataset.</div>';
            });
    }

    selectDataset = function(filename) {
        activeDataset = filename;
        // Highlight active sidebar item
        document.querySelectorAll(".dataset-item").forEach(item => {
            const spanText = item.querySelector("span").textContent;
            if (spanText === filename) {
                item.classList.add("active");
            } else {
                item.classList.remove("active");
            }
        });
        loadDatasetMetadata(filename);
    };

    function renderPreviewTable(rows, columns) {
        if (!rows || rows.length === 0) {
            tableContainerEl.innerHTML = '<div class="table-placeholder">No preview available</div>';
            return;
        }
        
        let html = '<table><thead><tr>';
        columns.forEach(col => {
            html += `<th>${col.name} <small style="display:block;font-weight:normal;opacity:0.6;">${col.type}</small></th>`;
        });
        html += '</tr></thead><tbody>';
        
        rows.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const val = row[col.name] !== undefined ? row[col.name] : '';
                html += `<td>${val}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        
        tableContainerEl.innerHTML = html;
    }

    // --- File Drag & Drop + Upload ---
    dropZoneEl.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZoneEl.classList.add("drag-over");
    });

    dropZoneEl.addEventListener("dragleave", () => {
        dropZoneEl.classList.remove("drag-over");
    });

    dropZoneEl.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZoneEl.classList.remove("drag-over");
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });

    fileInputEl.addEventListener("change", () => {
        if (fileInputEl.files.length > 0) {
            uploadFile(fileInputEl.files[0]);
        }
    });

    function uploadFile(file) {
        const formData = new FormData();
        formData.append("file", file);
        
        datasetStatsEl.textContent = "Uploading file...";
        tableContainerEl.innerHTML = '<div class="table-placeholder"><div class="loading-spinner-sm"></div></div>';
        
        fetch("/api/upload", {
            method: "POST",
            body: formData
        })
        .then(res => {
            if (!res.ok) throw new Error("Upload failed. Check format.");
            return res.json();
        })
        .then(data => {
            showToast(`Uploaded ${data.filename} successfully!`);
            // Fetch dataset list again to update sidebar
            fetchDatasets();
            // Load this dataset immediately
            selectDataset(data.filename);
        })
        .catch(err => {
            showToast(err.message, true);
            fetchDatasets(); // refresh list
        });
    }

    // --- Parse Mode Selector ---
    modeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            modeButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            currentMode = btn.getAttribute("data-mode");
        });
    });

    // --- Suggested Prompts click ---
    suggestedBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const promptText = btn.getAttribute("data-prompt");
            promptInputEl.value = promptText;
            // Submit form automatically
            visualizeFormEl.requestSubmit();
        });
    });

    // --- Collapsible Override Toggle ---
    btnToggleOverrideEl.addEventListener("click", () => {
        overrideSectionEl.classList.toggle("open");
    });

    // --- Submit Visualization Query ---
    visualizeFormEl.addEventListener("submit", (e) => {
        e.preventDefault();
        if (!activeDataset) {
            showToast("Please select a dataset first.", true);
            return;
        }
        
        const prompt = promptInputEl.value.trim();
        if (!prompt) return;
        
        generateChart(prompt);
    });

    // --- Apply Manual Overrides ---
    btnApplyOverrideEl.addEventListener("click", () => {
        if (!activeDataset) {
            showToast("Please select a dataset first.", true);
            return;
        }
        
        // Use overrides directly
        const chartType = overrideChartTypeEl.value;
        const xVal = overrideXEl.value;
        
        // Multi-select Y
        const selectedY = Array.from(overrideYEl.selectedOptions).map(opt => opt.value);
        const yVal = selectedY.join(",");
        
        if (!chartType && !xVal && !yVal) {
            showToast("Set at least one override parameter.", true);
            return;
        }

        generateChart("Manual Override Adjustments", {
            chartType,
            x: xVal,
            y: yVal
        });
    });

    function generateChart(prompt, overrides = null) {
        // Show loader in viewport
        chartViewportEl.innerHTML = `
            <div class="viewport-placeholder">
                <div class="loading-spinner"></div>
                <p style="margin-top: 12px;">Agent is analyzing prompt...</p>
                <small>${overrides ? 'Applying overrides' : 'Calling parser engine: ' + currentMode}</small>
            </div>
        `;
        parserTagEl.style.display = "none";
        
        const formData = new FormData();
        formData.append("prompt", prompt);
        formData.append("dataset", activeDataset);
        formData.append("mode", currentMode);
        
        if (overrides) {
            if (overrides.chartType) formData.append("override_chart_type", overrides.chartType);
            if (overrides.x) formData.append("override_x", overrides.x);
            if (overrides.y) formData.append("override_y", overrides.y);
        }

        fetch("/api/visualize", {
            method: "POST",
            body: formData
        })
        .then(res => {
            if (!res.ok) throw new Error("Failed to process visualization query.");
            return res.json();
        })
        .then(data => {
            const config = data.chart_config;
            const plotlyData = data.plotly_data;

            // Render Plotly Chart
            chartViewportEl.innerHTML = "";
            Plotly.newPlot(chartViewportEl, plotlyData.data, plotlyData.layout, {
                responsive: true,
                displayModeBar: true,
                displaylogo: false
            });

            // Update Parser Mode tag
            parserTagEl.textContent = config.parser_used.toUpperCase();
            parserTagEl.className = `tag tag-parser ${config.parser_used.includes("llm") ? "tag-llm" : ""}`;
            parserTagEl.style.display = "inline-block";

            // Sync Override UI Inputs with what was parsed/rendered
            overrideChartTypeEl.value = config.chart_type;
            overrideXEl.value = config.x || "";
            
            // Highlight Y columns
            Array.from(overrideYEl.options).forEach(opt => {
                if (Array.isArray(config.y)) {
                    opt.selected = config.y.includes(opt.value);
                } else {
                    opt.selected = opt.value === config.y;
                }
            });

            // Add to session history
            addToHistory(prompt, activeDataset, config, plotlyData);
            
            showToast("Visualization rendered successfully!");
        })
        .catch(err => {
            showToast(err.message, true);
            chartViewportEl.innerHTML = `
                <div class="viewport-placeholder text-danger">
                    <svg class="placeholder-icon" style="color:#ef4444;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <p style="margin-top: 12px; font-weight:600;">Failed to render chart</p>
                    <small>${err.message}</small>
                </div>
            `;
        });
    }

    // --- Session History management ---
    function addToHistory(prompt, dataset, config, plotlyData) {
        // Prevent duplicate consecutive entries
        if (chartHistory.length > 0 && chartHistory[0].prompt === prompt && chartHistory[0].dataset === dataset) {
            return;
        }

        const entry = { prompt, dataset, config, plotlyData };
        chartHistory.unshift(entry); // add to top
        
        // Limit history to 10 items
        if (chartHistory.length > 10) {
            chartHistory.pop();
        }

        renderHistory();
    }

    function renderHistory() {
        historyListEl.innerHTML = "";
        if (chartHistory.length === 0) {
            historyListEl.innerHTML = '<p class="empty-state">No charts generated yet.</p>';
            return;
        }

        chartHistory.forEach((item, index) => {
            const el = document.createElement("div");
            el.className = "history-item";
            el.title = `${item.prompt} (${item.dataset})`;
            el.innerHTML = `<strong>${item.config.chart_type.toUpperCase()}</strong>: ${item.prompt}`;
            el.addEventListener("click", () => restoreHistoryItem(index));
            historyListEl.appendChild(el);
        });
    }

    function restoreHistoryItem(index) {
        const item = chartHistory[index];
        if (!item) return;

        // If dataset is different, select it first, then render
        if (activeDataset !== item.dataset) {
            activeDataset = item.dataset;
            loadDatasetMetadata(item.dataset);
        }

        promptInputEl.value = item.prompt;

        // Render Plotly Chart
        chartViewportEl.innerHTML = "";
        Plotly.newPlot(chartViewportEl, item.plotlyData.data, item.plotlyData.layout, {
            responsive: true,
            displayModeBar: true,
            displaylogo: false
        });

        // Update tags and inputs
        parserTagEl.textContent = item.config.parser_used.toUpperCase();
        parserTagEl.style.display = "inline-block";
        overrideChartTypeEl.value = item.config.chart_type;
        overrideXEl.value = item.config.x || "";
        
        Array.from(overrideYEl.options).forEach(opt => {
            if (Array.isArray(item.config.y)) {
                opt.selected = item.config.y.includes(opt.value);
            } else {
                opt.selected = opt.value === item.config.y;
            }
        });

        showToast("Restored chart from history.");
    }
});
