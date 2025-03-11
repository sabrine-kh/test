import requests
import yaml
import streamlit as st
from pathlib import Path
from typing import Literal

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text: str) -> Literal[str]:
    """Extract row count information"""
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['number_of_rows']
            
        headers = {"Authorization": f"Bearer {config['api_key']}", "Content-Type": "application/json"}
        
        payload = {
            "model": config['model'],
            "messages": [
                {"role": "system", "content": config['system_prompt']},
                {"role": "user", "content": f"COMBINED DOCUMENTS:\n{text[:30000]}"}
            ],
            "temperature": 0.3,
            "max_tokens": 512,
            "top_p": 0.9
        }

        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        raw_result = response.json()['choices'][0]['message']['content'].strip()
        return raw_result.split("Number Of Rows:")[-1].split("\n")[0].strip() if "Number Of Rows:" in raw_result else "0"
        
    except Exception as e:
        st.error(f"Row count analysis failed: {str(e)}")
        return "ANALYSIS_ERROR"

__all__ = ['analyze']