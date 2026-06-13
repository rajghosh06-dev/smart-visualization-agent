from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import os
import json
import logging
from core.parser import parse_prompt, llm_status, llm_error, MODEL_NAME
from core.visualization import generate_chart

router = APIRouter()
logger = logging.getLogger("smart_vis_agent")

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_df_from_file(filename: str) -> pd.DataFrame:
    """Load a DataFrame from the local data folder."""
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Dataset {filename} not found.")
    
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == ".csv":
            return pd.read_csv(file_path)
        elif ext in [".xls", ".xlsx"]:
            return pd.read_excel(file_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload CSV or Excel.")
    except Exception as e:
        logger.error(f"Error reading file {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read dataset: {str(e)}")

@router.get("/", response_class=FileResponse)
async def read_root():
    """Serve the main SPA dashboard."""
    return FileResponse("app/templates/index.html")

@router.get("/api/llm-status")
async def get_llm_status():
    """Retrieve background LLM loading status and compatibility metrics."""
    from core.parser import check_system_compatibility
    compatibility = check_system_compatibility()
    return {
        "status": llm_status,
        "model_name": MODEL_NAME,
        "error": llm_error,
        "compatibility": compatibility
    }

@router.post("/api/llm-download")
async def trigger_llm_download():
    """Explicitly trigger downloading of the local LLM model."""
    from core.parser import init_llm, llm_status
    if llm_status in ["Ready", "Loading"]:
        return {"message": f"LLM is already in status: {llm_status}", "status": llm_status}
    init_llm(force_download=True)
    return {"message": "LLM download initiated in background.", "status": "Loading"}

@router.get("/api/datasets")
async def list_datasets():
    """List all available datasets in the data folder."""
    try:
        files = []
        for file in os.listdir(DATA_DIR):
            if file.endswith((".csv", ".xlsx", ".xls")):
                path = os.path.join(DATA_DIR, file)
                size = os.path.getsize(path)
                files.append({"name": file, "size": size})
        return {"datasets": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list datasets: {str(e)}")

@router.get("/api/datasets/{filename}")
async def get_dataset_details(filename: str):
    """Retrieve column info and preview rows for a dataset that exists locally."""
    try:
        df = get_df_from_file(filename)
        
        # Build column info with datatypes
        col_types = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            if "int" in dtype or "float" in dtype:
                col_type = "numeric"
            elif "date" in dtype or "datetime" in dtype:
                col_type = "datetime"
            else:
                col_type = "categorical"
            col_types.append({"name": col, "type": col_type})
            
        # Get preview rows (first 5 rows converted to simple objects)
        preview_data = df.head(5).fillna("").to_dict(orient="records")
        
        return {
            "filename": filename,
            "columns": col_types,
            "row_count": len(df),
            "preview": preview_data
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting dataset details for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load dataset details: {str(e)}")

@router.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """Upload a dataset, parse its columns, and return preview data."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV and Excel are allowed.")
    
    save_path = os.path.join(DATA_DIR, file.filename)
    try:
        # Save file locally
        with open(save_path, "wb") as f:
            f.write(await file.read())
            
        # Load file to extract preview and column info
        df = get_df_from_file(file.filename)
        
        # Build column info with datatypes
        col_types = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            if "int" in dtype or "float" in dtype:
                col_type = "numeric"
            elif "date" in dtype or "datetime" in dtype:
                col_type = "datetime"
            else:
                col_type = "categorical"
            col_types.append({"name": col, "type": col_type})
            
        # Get preview rows (first 5 rows converted to simple objects)
        preview_data = df.head(5).fillna("").to_dict(orient="records")
        
        return {
            "filename": file.filename,
            "columns": col_types,
            "row_count": len(df),
            "preview": preview_data
        }
    except Exception as e:
        # Cleanup file if saving/reading failed
        if os.path.exists(save_path):
            os.remove(save_path)
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload dataset: {str(e)}")

@router.post("/api/visualize")
async def visualize(
    prompt: str = Form(...),
    dataset: str = Form(...),
    mode: str = Form("hybrid"),
    override_chart_type: str = Form(None),
    override_x: str = Form(None),
    override_y: str = Form(None)
):
    """
    Main visualization endpoint. Takes a prompt, resolves visualization parameters
    using LLM/Heuristic, generates a Plotly figure, and returns chart JSON.
    Supports overrides for manual tuning.
    """
    # 1. Load data
    df = get_df_from_file(dataset)
    columns = df.columns.tolist()
    
    # 2. Parse Prompt
    parsed = {}
    if override_chart_type or override_x or override_y:
        # User manual override
        parsed = {
            "chart_type": override_chart_type or "bar",
            "x": override_x or columns[0],
            "y": override_y.split(",") if override_y and "," in override_y else override_y,
            "parser_used": "manual override"
        }
    else:
        # Auto-parse
        parsed = parse_prompt(prompt, columns, mode=mode)
        
    # Check if multiple y values were parsed/provided
    # (Clean list format if parsed as string representation of list)
    if isinstance(parsed.get("y"), str) and parsed["y"].startswith("["):
        try:
            parsed["y"] = json.loads(parsed["y"].replace("'", '"'))
        except:
            pass

    # 3. Generate Chart
    try:
        fig = generate_chart(df, parsed)
        
        # Serialize plotly figure to JSON
        plotly_json = json.loads(fig.to_json())
        
        return {
            "chart_config": parsed,
            "plotly_data": plotly_json
        }
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to build visualization: {str(e)}")
