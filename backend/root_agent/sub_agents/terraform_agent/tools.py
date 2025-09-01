from google.adk.tools import ToolContext
import google.genai.types as types

import uuid

async def save_terraform_file(filename: str, content: str, tool_context: ToolContext) -> dict:
    """
    Saves the provided content as a Terraform configuration file.

    Args:
        filename: The name of the file to save (e.g., 'main').
        content: The complete Terraform code to write to the file.
    
    Returns:
        A dict consist of the status, filename and the url of the file when uploaded to GCS bucket
    """
    try:
        unique_id = uuid.uuid4()
        # Ensure the filename ends with .tf
        base_name = filename.strip('.tf')
        file_path = f"{base_name}_{unique_id}.tf"
        
        with open(file_path, "wb") as f:
            f.write(content.encode('utf-8'))
        
        # Read the file content as bytes and return it
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        artifact = types.Part(
            inline_data=types.Blob(
                data=file_bytes,
                mime_type="text/plain"
            )
        )
        
        await tool_context.save_artifact(
            filename=file_path,
            artifact=artifact
        )
        
        return {"status": "success", "filename": file_path, "url": f"https://storage.googleapis.com/helloaihackathon_2025_autoarch_backend_specific/autoarch/{tool_context._invocation_context.user_id}/{tool_context._invocation_context.session.id}/{file_path}"}

    except Exception as e:
        return f"An error occurred while saving the file: {str(e)}"


async def saveTFCodeToDBSession(terraform_code: str, tool_context: ToolContext) -> str:
    """
    Save JSON to a state with key "terraform_code".
    
    Args:
        terraform_code: the plain text of terraform code with proper formatting

    Returns:
        A string indicating success or failure.
    """
    try:
        tool_context.state["terraform_code"] = terraform_code
        return "Terraform Code Saved Successfully"
    except Exception as e:
        return f"Error: {str(e)}"