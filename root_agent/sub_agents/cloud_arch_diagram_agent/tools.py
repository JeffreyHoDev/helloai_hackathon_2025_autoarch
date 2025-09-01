from google.adk.tools import ToolContext
import google.genai.types as types
import ast
import os
import base64
import traceback
import subprocess
import sys

# async def save_image_to_artifact(base64_string: str, tool_context: ToolContext) -> str:
#     """
#     Processes a received Content object, saves file artifacts, and returns a list
#     of new artifacts created from the received data.
    
#     Args:
#         base64_string: The Base64 encoded string of the file.
    
#     Returns:
#         A string of success or error.
#     """

#     try:
#         file_bytes = base64.b64decode(base64_string)
#         output_filename = f"received_file_{os.urandom(4).hex()}.png"
#         image_artifact = types.Part.from_bytes(
#             data=file_bytes,
#             mime_type="image/png"
#         )
#         version = await tool_context.save_artifact(filename=output_filename, artifact=image_artifact)
#         return f"Success-Version {version}"
#     except Exception as e:
#         return f"Failed to save image to artifact: {str(e)}"


# def save_image_to_artifact(tool_context: ToolContext) -> str:
#     """
#     Finds and saves the first image artifact from the tool_context.
    
#     Args:
#         tool_context: The context containing artifacts from the tool call.
    
#     Returns:
#         A string of success or error.
#     """
#     for artifact in tool_context.artifacts:
#         if artifact.inline_data and artifact.inline_data.mime_type.startswith("image/"):
#             try:
#                 # The ADK has already handled the decoding for you.
#                 # The data is already in bytes format.
#                 file_bytes = artifact.inline_data.data
#                 output_filename = f"received_file_{os.urandom(4).hex()}.png"

#                 # Save the new artifact to the tool context.
#                 # This is the correct way to save the artifact for later use by your agent.
#                 version = tool_context.save_artifact(
#                     filename=output_filename,
#                     artifact=types.Part(
#                         inline_data=types.Blob(
#                             mime_type=artifact.inline_data.mime_type,
#                             data=file_bytes
#                         )
#                     )
#                 )

#                 # Return a success message
#                 return f"Success - Image saved to artifact with version {version}"
#             except Exception as e:
#                 return f"Failed to save image to artifact: {str(e)}"
    
#     return "Failed: No image artifact found in the tool context."

async def execute_python_code(code_string: str, tool_context: ToolContext) -> str:
    """
    Executes Python code, reads the generated image, and saves it to an artifact.
    
    Returns:
        A string indicating success or failure.
    """
    image_filename = "diagram.png"
    
    # Get the path to the current Python interpreter from the virtual environment
    python_executable = sys.executable

    try:
        # Run the Python code using the same interpreter as the agent
        subprocess.run(
            [python_executable, "-c", code_string],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        
        with open(image_filename, "rb") as f:
            image_bytes = f.read()
            
        image_artifact = types.Part(
            inline_data=types.Blob(
                data=image_bytes,
                mime_type="image/png"
            )
        )
        output_filename = f"received_file_{os.urandom(4).hex()}.png"
        version = await tool_context.save_artifact(
            filename=output_filename,
            artifact=image_artifact
        )
        
        return f"Success - Image saved to artifact with version {version}. Filename: {output_filename}"
    
    except subprocess.CalledProcessError as e:
        return f"Python code execution failed with error: {e.stderr}"
    except FileNotFoundError:
        return f"Error: Code executed but the file '{image_filename}' was not found."
    except Exception as e:
        error_details = traceback.format_exc()
        return f"An unexpected error occurred: {str(e)}\n{error_details}"
    finally:
        # Clean up the generated image file to avoid clutter.
        if os.path.exists(image_filename):
            os.remove(image_filename)