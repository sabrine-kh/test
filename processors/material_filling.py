import requests
import yaml
import streamlit as st
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"

def analyze(text):
    """Analyze COMBINED text from multiple documents for material filling"""
    try:
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)['attributes']['material_filling']
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        # Modified system prompt for multi-document analysis
        system_prompt = f"""
        {config['system_prompt']}
        
        SPECIAL INSTRUCTIONS FOR COMBINED ANALYSIS:
        - Analyze content from MULTIPLE DOCUMENTS together
        - Resolve conflicts using most frequent occurrence
        - Return 'CONFLICT' if contradictory info found
        - Consider partial mentions across documents
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
                    "content": f"COMBINED DOCUMENT CONTENT:\n{text}"
                }
            ],
            "temperature": 0.2,  # Lower temp for more consistent results
            "max_tokens": 512
        }

        response = requests.post(
            "https://api.fireworks.ai/inference/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Add timeout for reliability
        )
        response.raise_for_status()
        
        result = response.json()
        raw_output = result['choices'][0]['message']['content'].strip()
        
        # Post-processing validation
        if "Material Filling:" in raw_output:
            return raw_output.split("Material Filling:")[-1].strip()
        return raw_output
        
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return "NETWORK_ERROR"
    except KeyError as e:
        st.error(f"Response parsing error: {str(e)}")
        return "PARSE_ERROR"
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return "ANALYSIS_FAILED"