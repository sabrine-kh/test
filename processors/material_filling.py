import requests
import yaml
import streamlit as st
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text):
    """Analyze text for material filling attribute"""
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)['attributes']['material_filling']
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config['model'],
        "messages": [
            {"role": "system", "content": config['system_prompt']},
            {"role": "user", "content": text}
        ],
        "temperature": 0.3
    }
    
    try:
        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"Material Filling analysis failed: {str(e)}")
        return "ERROR"