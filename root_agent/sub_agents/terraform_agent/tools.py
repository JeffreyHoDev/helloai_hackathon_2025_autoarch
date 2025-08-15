from google.adk.tools import ToolContext
import google.genai.types as types

import uuid

async def save_terraform_file(filename: str, content: str, tool_context: ToolContext) -> str:
    """
    Saves the provided content as a Terraform configuration file.

    Args:
        filename: The name of the file to save (e.g., 'main').
        content: The complete Terraform code to write to the file.
    
    Returns:
        A confirmation message indicating the file was saved.
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
        
    except Exception as e:
        return f"An error occurred while saving the file: {str(e)}"
