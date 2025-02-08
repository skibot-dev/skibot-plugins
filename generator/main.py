import os
import json
import requests

approved_issues = []
plugins_list = []

def fetch_approved_issues():
    try:
        for page_number in range(1, 100):
            api_url = "https://api.github.com/repos/skibot-dev/skibot-plugins/issues"
            params = {
                "state": "open",
                "page": page_number,
                "per_page": 30
            }
            response = requests.get(url=api_url, params=params)
            
            if response.status_code == 200:
                page_data = response.json()
                if not page_data:
                    print(f"Reached empty page at {page_number}")
                    break
                
                for issue in page_data:
                    if any(label["name"] == "通过" for label in issue["labels"]):
                        approved_issues.append(issue)
            else:
                print(f"API request failed with status: {response.status_code}")
                break
                
    except Exception as error:
        print(f"Error fetching issues: {error}")

def extract_plugin_json(issue):
    body_content = issue.get("body")
    if not body_content:
        return None
    
    json_start = body_content.find("```json")
    json_end = body_content.find("```", json_start + 7)
    
    if json_start == -1 or json_end == -1:
        return None
    
    return body_content[json_start + 7 : json_end]

def parse_json_to_dict(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as error:
        print(f"JSON parsing failed: {error}")
        return None

if __name__ == "__main__":
    fetch_approved_issues()
    
    if not approved_issues:
        print("No approved issues found")
        exit()

    for issue in approved_issues:
        raw_json = extract_plugin_json(issue)
        if not raw_json:
            continue
            
        plugin_data = parse_json_to_dict(raw_json)
        if not plugin_data:
            continue
            
        plugin_entry = {
            "name": plugin_data["name"],
            "description": plugin_data["description"],
            "avatar": plugin_data["avatar"],
            "git-url": plugin_data["git-url"]
        }
        plugins_list.append(plugin_entry)

    os.makedirs("./data", exist_ok=True)
    with open("./data/plugins.json", "w", encoding="utf-8") as output_file:
        json.dump(plugins_list, output_file, ensure_ascii=False, indent=4)