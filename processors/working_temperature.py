import requests
import yaml
import streamlit as st
from pathlib import Path
from typing import Literal

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text: str) -> Literal[str]:
    """Extract working temperature from combined documents"""
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['working_temperature']
            
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system", 
                    "content": config['system_prompt']
                },
                {
                    "role": "user",
                    "content": f"COMBINED DOCUMENTS:\n{text[:30000]}"
                }
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
        
        if "Working Temperature:" in raw_result:
            return raw_result.split("Working Temperature:")[-1].split("\n")[0].strip()
        return "NOT FOUND"
        
    except Exception as e:
        st.error(f"Working temperature analysis failed: {str(e)}")
        return "ANALYSIS_ERROR"

__all__ = ['analyze']