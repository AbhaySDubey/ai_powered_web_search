import pandas as pd
import requests
import json
from openai import OpenAI, RateLimitError
import re

def serp_search(query, api_key, num_res=5):
    url = 'https://serpapi.com/search'
    params = {
        'q': query,
        'api_key': api_key,
        'num': num_res,
        'engine': 'google'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        if response.status_code == 429:
            return {"status": "error", "message": "SERP API rate limit exceeded. Please try again later."}
        elif response.status_code == 401:
            return {"status": "error", "message": "SERP API quota exhausted or invalid API key."}
            
        json_response = response.json()
        
        # Validate response structure
        if not json_response or 'error' in json_response:
            return {
                "status": "error",
                "message": json_response.get('error', 'Empty response from SERP API')
            }
            
        return {
            "status": "success",
            "data": json_response
        }
            
    except requests.exceptions.HTTPError as e:
        return {"status": "error", "message": f"SERP API error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}


def extract_info(response, query, api_key):
    if response.get("status") == "error":
        return response
        
    client = OpenAI(
        api_key=api_key,
        base_url='https://api.x.ai/v1',
    )
    
    # Clean and format the JSON response
    json_responses_str = json.dumps(response.get("data", response), indent=4)
    
    try:
        completion = client.chat.completions.create(
            model='grok-beta',
            messages=[
                {
                    "role": "system", 
                    "content": """"
                    You are Grok, a chatbot meant to extract relevant info from a bunch of JSON responses that are part of search results. Your task is to deliver 2 responses:
                    1. a json response that answers the prompt
                    2. a summary of the answer for the prompt.
                    """
                },
                {
                    "role": "user", 
                    "content": f'Based on the {query} search the results from {json_responses_str}'
                },
            ],
        )
        
        response_content = completion.choices[0].message.content
        
        # Improved regex pattern for JSON array extraction
        json_match = re.search(r'\[[\s\S]*?\]', response_content)
        if json_match:
            try:
                json_str = json_match.group(0)
                json_list = json.loads(json_str)
            except json.JSONDecodeError:
                json_list = []
        else:
            json_list = []
        
        # Extract summary with multiple patterns
        summary = ""
        patterns = ['2.', 'Summary:', 'summary:']
        for pattern in patterns:
            if pattern in response_content:
                summary = response_content.split(pattern, 1)[1].strip()
                break
            
        return {
            "status": "success",
            "extracted_data": json_list,
            "summary": summary
        }
        
    except RateLimitError:
        return {
            "status": "error", 
            "message": "API Limit for Grok AI exhausted. Please try again later or with a different API key."
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"An error occurred during extraction: {str(e)}"
        }
        

def ddg_search(query):
    url = 'https://api.duckduckgo.com/'
    params = {
        'q': query,
        'format': 'json',
        'no_redirect': 1,
        'no_html': 1,
        'skip_disambig': 1
    }
    response = requests.get(url, params=params)
    return response.json()