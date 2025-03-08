# processors/pull_to_seat.py
import requests
import yaml
import streamlit as st
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text):
    """Analyze text for pull-to-seat attribute"""
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['pull_to_seat']
            
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
        
        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
        
    except Exception as e:
        st.error(f"Pull-to-seat analysis failed: {str(e)}")
        return "ERROR"

# Explicitly expose the analyze function
__all__ = ['analyze']