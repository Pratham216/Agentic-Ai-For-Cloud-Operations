from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import openstack
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def parse_user_input(user_input):
    """Parse natural language into structured OpenStack commands"""
    prompt = ChatPromptTemplate.from_template("""
    Analyze this OpenStack request:
    {request}
    
    Return JSON with:
    - intent (create/delete/resize/query)
    - entity_type (VM/volume/network)
    - parameters (name, size, etc.)
    - needs_confirmation (true/false)
    
    Example:
    Input: "Create a medium VM named 'db-server' with 8GB RAM"
    Output: {{"intent":"create","entity_type":"VM","parameters":{{"name":"db-server","ram":"8GB"}},"needs_confirmation":false}}
    """)
    return (prompt | llm).invoke({"request": user_input})

def extract_json(gemini_response):
    """Extract JSON from Gemini's response"""
    try:
        # Handle both code-block and raw JSON responses
        content = gemini_response.content
        if '```json' in content:
            json_str = content.split('```json\n')[1].split('\n```')[0]
        elif '```' in content:
            json_str = content.split('```\n')[1].split('\n```')[0]
        else:
            json_str = content.strip()
        return json.loads(json_str)
    except (IndexError, json.JSONDecodeError) as e:
        print(f"Error parsing response: {e}")
        return None

def map_to_openstack_actions(parsed_input):
    """Map parsed input to OpenStack API calls"""
    if not parsed_input:
        return None
        
    conn = openstack.connect(
        auth_url="https://api-ap-south-mum-1.openstack.acecloudhosting.com:5000",
        username="Hackathon_AIML_1",
        password="Hackathon_AIML_1@567",
        project_name="your_project",
        user_domain_name="Default",
        project_domain_name="Default"
    )
    
    actions = []
    
    if parsed_input["intent"] == "create" and parsed_input["entity_type"] == "VM":
        # Convert RAM to flavor
        ram_gb = int(parsed_input["parameters"]["ram"].replace("GB", ""))
        flavor = "S.4" if ram_gb == 4 else "M.8" if ram_gb == 8 else "L.16"
        
        actions.append({
            "api": "compute",
            "operation": "create_server",
            "params": {
                "name": parsed_input["parameters"]["name"],
                "flavor": flavor,
                "image": "ubuntu-20.04"
            }
        })
    
    return actions

if __name__ == "__main__":
    test_input = "Resize dev‑box to flavor M.8"
    
    try:
        # Step 1: Parse user input
        response = parse_user_input(test_input)
        print("Raw Gemini Response:", response.content)
        
        # Step 2: Extract JSON
        parsed = extract_json(response)
        
        if not parsed:
            print("Failed to parse the input")
            exit(1)
            
        print("Parsed Output:", parsed)
        
        # Step 3: Map to OpenStack actions
        actions = map_to_openstack_actions(parsed)
        print("Generated Actions:", actions)
        
    except Exception as e:
        print(f"Error: {e}")