import re
import json
import logging
import threading
from gpt4all import GPT4All

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smart_vis_agent")

MODEL_NAME = "orca-mini-3b-gguf2-q4_0.gguf"
model_instance = None
llm_status = "Not Started"
llm_error = None

def load_llm_in_background():
    """Load the GPT4All model in a background thread to avoid blocking server startup."""
    global model_instance, llm_status, llm_error
    llm_status = "Loading"
    try:
        logger.info(f"Loading local LLM model: {MODEL_NAME}...")
        # Download and load the model inside the project's dedicated models directory
        import os
        model_path = os.path.join("core", "models")
        os.makedirs(model_path, exist_ok=True)
        model_instance = GPT4All(model_name=MODEL_NAME, model_path=model_path, allow_download=True)
        llm_status = "Ready"
        logger.info("Local LLM model is ready and loaded!")
    except Exception as e:
        llm_status = "Failed"
        llm_error = str(e)
        logger.error(f"Failed to load local LLM model: {e}")

def init_llm():
    """Trigger background loading of the local LLM."""
    thread = threading.Thread(target=load_llm_in_background, daemon=True)
    thread.start()

def parse_prompt_heuristics(prompt: str, columns: list):
    """
    A smart rule-based NLP parser that extracts chart type and column mapping.
    Runs instantly with 0MB RAM/CPU footprint.
    """
    prompt_lower = prompt.lower()
    
    # 1. Determine Chart Type
    chart_type = "bar"  # Default
    if any(k in prompt_lower for k in ["scatter", "correlation", "relationship", "vs", "versus"]):
        chart_type = "scatter"
    elif any(k in prompt_lower for k in ["line", "trend", "evolution", "growth", "over time"]):
        chart_type = "line"
    elif any(k in prompt_lower for k in ["histogram", "distribution", "freq", "frequency", "density", "spread"]):
        chart_type = "histogram"
    elif any(k in prompt_lower for k in ["pie", "share", "percentage", "proportion"]):
        chart_type = "pie"
    elif any(k in prompt_lower for k in ["bar", "column", "compare", "chart"]):
        chart_type = "bar"

    # 2. Extract Column Mentions
    matched_cols = []
    # Sort columns by length descending to match longer multi-word columns first (e.g. "total exports" before "exports")
    sorted_cols = sorted(columns, key=len, reverse=True)
    
    # Normalize prompt text for matching
    cleaned_prompt = re.sub(r'[^\w\s]', ' ', prompt_lower)
    words = cleaned_prompt.split()
    
    for col in sorted_cols:
        col_lower = col.lower()
        col_clean = re.sub(r'[^\w\s]', ' ', col_lower)
        # Match full column name in prompt
        if col_lower in prompt_lower or col_clean in cleaned_prompt:
            matched_cols.append(col)
        else:
            # Match if all words of the column are in the prompt
            col_tokens = col_clean.split()
            if col_tokens and all(token in words for token in col_tokens):
                matched_cols.append(col)
                
    # If no columns matched, try matching individual tokens with stop-word filter
    if not matched_cols:
        stop_words = {"and", "or", "of", "in", "by", "vs", "chart", "plot", "show", "compare", "values", "production", "total"}
        for col in sorted_cols:
            col_clean = re.sub(r'[^\w\s]', ' ', col.lower())
            col_tokens = col_clean.split()
            meaningful_tokens = [t for t in col_tokens if t not in stop_words]
            if meaningful_tokens and any(t in words for t in meaningful_tokens):
                matched_cols.append(col)

    # De-duplicate matches preserving order of appearance in the prompt
    unique_matched = []
    for c in matched_cols:
        if c not in unique_matched:
            unique_matched.append(c)
            
    # Sort matched columns by where they appear in the prompt
    def get_match_index(col):
        col_lower = col.lower()
        idx = prompt_lower.find(col_lower)
        if idx != -1:
            return idx
        # If not found directly, find index of any word of the column
        for word in re.sub(r'[^\w\s]', ' ', col_lower).split():
            if word:
                idx = prompt_lower.find(word)
                if idx != -1:
                    return idx
        return len(prompt_lower)

    unique_matched.sort(key=get_match_index)
            
    # Helper to identify categorical column defaults with priority
    cat_keywords = {"state", "code", "country", "name", "category", "year", "date", "month", "label"}
    cat_cols = [c for c in columns if c.lower() in cat_keywords]
    
    # Priority ranking for defaults (state/name/country are preferred over abbreviations like code)
    priority_cats = ["state", "name", "country", "code", "category", "year", "date"]
    default_cat = None
    for p_cat in priority_cats:
        matched = [c for c in cat_cols if c.lower() == p_cat]
        if matched:
            default_cat = matched[0]
            break
            
    if not default_cat:
        default_cat = cat_cols[0] if cat_cols else (columns[0] if columns else None)
    
    x = None
    y = None
    
    if chart_type == "histogram":
        # Histograms take a single column
        x = unique_matched[0] if unique_matched else (columns[-1] if columns else None)
        y = None
    elif chart_type == "scatter":
        if len(unique_matched) >= 2:
            x = unique_matched[0]
            y = unique_matched[1]
        elif len(unique_matched) == 1:
            x = unique_matched[0]
            remaining = [c for c in columns if c != x]
            y = remaining[0] if remaining else None
        else:
            x = default_cat
            remaining = [c for c in columns if c != x]
            y = remaining[0] if remaining else None
    else:
        # bar, line, pie
        # Check if user is asking to compare multiple columns (e.g. "compare corn and wheat")
        numeric_matched = [c for c in unique_matched if c not in cat_cols]
        
        # If multiple numeric columns are mentioned, configure as comparison
        if len(numeric_matched) >= 2:
            x = default_cat
            y = numeric_matched  # Y is a list of series
        elif len(unique_matched) == 2:
            col1, col2 = unique_matched[0], unique_matched[1]
            if col1 in cat_cols and col2 not in cat_cols:
                x = col1
                y = col2
            elif col2 in cat_cols and col1 not in cat_cols:
                x = col2
                y = col1
            else:
                x = col1
                y = col2
        elif len(unique_matched) == 1:
            val = unique_matched[0]
            if val in cat_cols:
                x = val
                remaining = [c for c in columns if c not in cat_cols]
                y = remaining[0] if remaining else None
            else:
                x = default_cat
                y = val
        else:
            x = default_cat
            remaining = [c for c in columns if c not in cat_cols]
            y = remaining[0] if remaining else None
            
    return {
        "chart_type": chart_type,
        "x": x,
        "y": y,
        "parser_used": "heuristic"
    }

def parse_prompt_llm(prompt: str, columns: list):
    """
    Parse prompt using local GPT4All LLM.
    """
    global model_instance
    if not model_instance:
        raise RuntimeError("LLM model is not loaded yet")
        
    system_prompt = (
        "You are an AI data visualization assistant.\n"
        f"Available columns in the dataset: {columns}\n"
        "Supported chart types: 'bar', 'line', 'scatter', 'histogram', 'pie'.\n"
        "Map the user prompt to the available columns. Return ONLY a JSON object with these keys:\n"
        "{\n"
        "  \"chart_type\": \"bar\" | \"line\" | \"scatter\" | \"histogram\" | \"pie\",\n"
        "  \"x\": \"column_name_for_x_axis\",\n"
        "  \"y\": \"column_name_for_y_axis_or_list_of_columns\"\n"
        "}\n"
        "Do not include any extra text, code blocks, or explanations."
    )
    
    user_prompt = f"Prompt: {prompt}"
    
    try:
        with model_instance.chat_session(system_prompt):
            response = model_instance.generate(user_prompt, max_tokens=150, temp=0.1)
            
        logger.info(f"LLM Response: {response}")
        
        # Extract JSON substring
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            parsed = json.loads(response.strip())
            
        chart_type = parsed.get("chart_type", "bar")
        x = parsed.get("x")
        y = parsed.get("y")
        
        # Ensure column validations
        if x not in columns:
            x = None
            
        if isinstance(y, list):
            y = [col for col in y if col in columns]
            if not y:
                y = None
        else:
            if y not in columns:
                y = None
                
        return {
            "chart_type": chart_type,
            "x": x,
            "y": y,
            "parser_used": "llm"
        }
    except Exception as e:
        logger.error(f"Error parsing LLM response or generating: {e}")
        return None

def parse_prompt(prompt: str, columns: list, mode: str = "hybrid") -> dict:
    """
    Main entry point for parsing prompts.
    Supports modes: "hybrid" (LLM if ready, otherwise heuristic), "heuristic", "llm"
    """
    global model_instance, llm_status
    
    if mode == "heuristic":
        return parse_prompt_heuristics(prompt, columns)
        
    if mode == "llm":
        if llm_status == "Ready" and model_instance:
            res = parse_prompt_llm(prompt, columns)
            if res:
                return res
        raise RuntimeError(f"LLM parser requested but LLM is not ready. Status: {llm_status}")
        
    # Hybrid mode (default)
    if llm_status == "Ready" and model_instance:
        try:
            res = parse_prompt_llm(prompt, columns)
            if res:
                return res
        except Exception as e:
            logger.warning(f"LLM parsing failed, falling back to heuristics: {e}")
            
    # Fallback to heuristics
    result = parse_prompt_heuristics(prompt, columns)
    if llm_status == "Loading":
        result["parser_used"] = "heuristic (LLM loading...)"
    elif llm_status == "Failed":
        result["parser_used"] = "heuristic (LLM failed to load)"
    else:
        result["parser_used"] = "heuristic"
    return result
