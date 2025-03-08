# processors/pull_to_seat.py
import requests
import yaml
import streamlit as st
from pathlib import Path
from typing import Literal

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
ALLOWED_VALUES = ["Yes", "No", "CONFLICT", "PARTIAL", "NOT_FOUND"]

def analyze(text: str) -> Literal["Yes", "No", "CONFLICT", "PARTIAL", "NOT_FOUND", "ERROR"]:
    """Analyze combined documents for pull-to-seat requirement"""
    try:
        # Load configuration
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['pull_to_seat']
        
        # Prepare API request
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        system_prompt = f"""
        {config['system_prompt']}
        
        COMBINED ANALYSIS RULES:
        1. Analyze ALL documents together
        2. Return 'Yes' if ANY document mentions pull-to-seat requirement
        3. Return 'No' if ALL documents explicitly state no pull-to-seat
        4. Return 'CONFLICT' for contradictory information between documents
        5. Return 'PARTIAL' if some docs mention but not all
        6. Consider indirect references across documents
        7. Respond ONLY in the specified format
        """
        
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt.strip()
                },
                {
                    "role": "user",
                    "content": f"COMBINED DOCUMENTS CONTENT:\n{text[:30000]}"  # Limit to 30k chars
                }
            ],
            "temperature": 0.2,
            "max_tokens": 512,
            "top_p": 0.9
        }

        # Execute API call
        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        # Process response
        raw_result = response.json()['choices'][0]['message']['content'].strip()
        cleaned_result = raw_result.split("Pull-To-Seat:")[-1].split("\n")[0].strip().replace('"', '')
        
        # Validate output
        if cleaned_result in ALLOWED_VALUES:
            return cleaned_result
        return "NOT_FOUND"
        
    except requests.exceptions.Timeout:
        st.error("Analysis timed out - reduce file size or number of documents")
        return "ERROR"
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return "ERROR"
    except KeyError as e:
        st.error(f"Missing data in response: {str(e)}")
        return "ERROR"
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return "ERROR"

__all__ = ['analyze']