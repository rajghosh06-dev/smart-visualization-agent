import pytest
import pandas as pd
from core.parser import parse_prompt_heuristics, parse_prompt
from core.visualization import generate_chart

# Mock columns mirroring the sample dataset
COLUMNS = [
    "code", "state", "category", "total exports", "beef", "pork", 
    "poultry", "dairy", "fruits fresh", "fruits proc", "total fruits", 
    "veggies fresh", "veggies proc", "total veggies", "corn", "wheat", "cotton"
]

@pytest.fixture
def sample_df():
    """Create a small mock DataFrame mimicking the structure of sample.csv."""
    data = {
        "code": ["AL", "AK", "AZ"],
        "state": ["Alabama", "Alaska", "Arizona"],
        "category": ["state", "state", "state"],
        "total exports": [1390.63, 13.31, 1463.17],
        "poultry": [481.0, 0.0, 0.0],
        "dairy": [4.06, 0.19, 105.48],
        "corn": [34.9, 0.0, 7.3],
        "wheat": [70.0, 0.0, 48.7],
        "cotton": [317.61, 0.0, 423.95]
    }
    return pd.DataFrame(data)

def test_parse_exports_by_state():
    prompt = "Show total exports by state"
    result = parse_prompt_heuristics(prompt, COLUMNS)
    assert result["chart_type"] == "bar"
    assert result["x"] == "state"
    assert result["y"] == "total exports"

def test_parse_scatter_poultry_vs_exports():
    prompt = "Scatter plot poultry vs total exports"
    result = parse_prompt_heuristics(prompt, COLUMNS)
    assert result["chart_type"] == "scatter"
    assert result["x"] == "poultry"
    assert result["y"] == "total exports"

def test_parse_line_dairy():
    prompt = "Line chart of dairy production"
    result = parse_prompt_heuristics(prompt, COLUMNS)
    assert result["chart_type"] == "line"
    assert result["x"] == "state"  # Fallback to categorical column
    assert result["y"] == "dairy"

def test_parse_compare_corn_wheat():
    prompt = "Compare corn and wheat exports"
    result = parse_prompt_heuristics(prompt, COLUMNS)
    assert result["chart_type"] == "bar"
    assert result["x"] == "state"
    assert "corn" in result["y"]
    assert "wheat" in result["y"]

def test_parse_histogram_cotton():
    prompt = "Histogram of cotton values"
    result = parse_prompt_heuristics(prompt, COLUMNS)
    assert result["chart_type"] == "histogram"
    assert result["x"] == "cotton"
    assert result["y"] is None

def test_chart_generation(sample_df):
    # Test single series chart generation
    parsed_single = {"chart_type": "bar", "x": "state", "y": "total exports"}
    fig_single = generate_chart(sample_df, parsed_single)
    assert fig_single is not None
    assert fig_single.layout.title.text == "Bar Chart: total exports vs state"
    
    # Test multi-series chart generation
    parsed_multi = {"chart_type": "line", "x": "state", "y": ["corn", "wheat"]}
    fig_multi = generate_chart(sample_df, parsed_multi)
    assert fig_multi is not None
    assert "corn, wheat vs state" in fig_multi.layout.title.text

    # Test histogram chart generation
    parsed_hist = {"chart_type": "histogram", "x": "cotton", "y": None}
    fig_hist = generate_chart(sample_df, parsed_hist)
    assert fig_hist is not None

def test_get_suggested_prompts():
    from core.parser import get_suggested_prompts
    df_sample = pd.read_csv("data/sample.csv")
    suggestions_sample = get_suggested_prompts(df_sample)
    assert len(suggestions_sample) == 5
    assert "Show total exports by state" in suggestions_sample
    assert "Histogram of cotton values" in suggestions_sample

    df_sample2 = pd.read_csv("data/sample2.csv")
    suggestions_sample2 = get_suggested_prompts(df_sample2)
    assert len(suggestions_sample2) == 5
    assert "Show pop by country" in suggestions_sample2
    assert "Scatter plot lifeExp vs gdpPercap" in suggestions_sample2
