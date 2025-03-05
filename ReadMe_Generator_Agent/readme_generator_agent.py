import os
import ast
import openai
from uagents import Agent, Context, Model

# Set your OpenAI API key here
OPENAI_API_KEY = "your-api-key"

class ReadmeOutput(Model):
    readme: str

readme_agent = Agent(name='ReadmeGenerator', port=5050)

def extract_code_details(file_path: str) -> dict:
    """Extracts classes, functions, docstrings, and dependencies from the given Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        tree = ast.parse(code)
        classes, functions, dependencies = [], [], []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node, clean=True) or "No description available"
                })
            elif isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "docstring": ast.get_docstring(node, clean=True) or "No description available",
                    "params": [arg.arg for arg in node.args.args],
                    "returns": ast.unparse(node.returns) if node.returns else "Unknown"
                })
        
        return {"classes": classes, "functions": functions, "dependencies": dependencies}
    except Exception as e:
        return {"error": str(e)}

def generate_readme(file_path: str) -> str:
    """Generates a README.md file using OpenAI API."""
    code_details = extract_code_details(file_path)
    if "error" in code_details:
        return f"Error extracting code details: {code_details['error']}"
    
    functions_str = "\n".join(
        [f"- {func['name']}({', '.join(func['params'])}) -> {func['returns']}\n  {func['docstring']}" for func in code_details['functions']]
    ) if code_details['functions'] else "None"
    
    classes_str = "\n".join(
        [f"- {cls['name']}: {cls['docstring']}" for cls in code_details['classes']]
    ) if code_details['classes'] else "None"
    
    dependencies_str = ", ".join(code_details['dependencies']) if code_details['dependencies'] else "None"
    
    prompt = f"""
    Generate a professional README.md file for the following Python project:
    
    ![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
    ![tag:automation](https://img.shields.io/badge/automation-3D8BD3)
    
    ## Agent Name: {os.path.basename(file_path).replace('.py', '')}
    
    ## Description
    Provide a concise description of what this project does.
    
    ## Input Data Model
    Define the expected input data format. Describe the input class model code short snippet.
    
    ## Output Data Model
    Define the output data format. Describe the input class model code short snippet.
    
    ## Features
    List key features of the project.
    
    ## Dependencies
    {dependencies_str}
    
    ## Installation
    Steps to install the dependencies and run the project. check imports given in .py file on top and accordingly mention what all packages to install and how.
    
    ## Functions
    {functions_str}
    
    ## Usage
    Instructions on how to use the project.
    
    """
    
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes professional README.md files."},
            {"role": "user", "content": prompt}
        ]
    )
    
    readme_content = response.choices[0].message.content
    
    readme_path = os.path.join(os.path.dirname(file_path), "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return f"README.md saved at {readme_path}"

if __name__ == "__main__":
    file_path = input("Enter the path of the Python file: ").strip()
    if os.path.isfile(file_path):
        result = generate_readme(file_path)
        print(result)
    else:
        print("Invalid file path. Please provide a valid Python file.")
