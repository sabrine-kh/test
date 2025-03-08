# processors/pull_to_seat.py
import requests
import yaml
import streamlit as st
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text):
    """Analyze COMBINED text from multiple documents for pull-to-seat attribute"""
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['pull_to_seat']
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Enhanced system prompt for multi-doc analysis
        system_prompt = f"""
        {config['system_prompt']}
        
        COMBINED ANALYSIS RULES:
        1. Consider information from ALL documents together
        2. Return 'Yes' if ANY document mentions pull-to-seat requirement
        3. Return 'No' if ALL documents explicitly state no pull-to-seat
        4. Return 'CONFLICT' if contradictory information exists
        5. Return 'PARTIAL' if some docs mention but not all
        6. Consider indirect references across documents
        """
        
        payload = {
            "model": config['model'],
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"COMBINED DOCUMENTS CONTENT:\n{text}"
                }
            ],
            "temperature": 0.25,  # More deterministic for combined analysis
            "max_tokens": 256,
            "top_p": 0.95
        }

        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=25  # Add timeout protection
        )
        response.raise_for_status()
        
        raw_result = response.json()['choices'][0]['message']['content'].strip()
        
        # Validate and format output
        if "Pull-To-Seat:" in raw_result:
            return raw_result.split("Pull-To-Seat:")[-1].strip()
        return raw_result

    except requests.exceptions.Timeout:
        st.error("Analysis timed out - try smaller documents or fewer files")
        return "TIMEOUT"
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {str(e)}")
        return "CONNECTION_ERROR"
    except KeyError as e:
        st.error(f"Response parsing failed: {str(e)}")
        return "PARSE_ERROR"
    except Exception as e:
        st.error(f"Unexpected analysis error: {str(e)}")
        return "ANALYSIS_FAILED"

__all__ = ['analyze']