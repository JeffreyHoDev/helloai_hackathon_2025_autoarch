import os
import io
import base64

from dotenv import load_dotenv

import google.genai.types as types

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from lxml import etree
from google.adk.tools import ToolContext

import json
import matplotlib.pyplot as plt
import pandas as pd

import traceback
import subprocess
import sys


# --- Load Environment Variables (If ADK tools need them, e.g., API keys) ---
load_dotenv() # Create a .env file in the same directory if needed


async def generate_validation_report_from_markdown(content: str, json_input: dict, chart_type: str, tool_context: ToolContext) -> dict:
    """
    Parses scorecard data from JSON, generates a chart, and embeds it into a PDF
    along with Markdown content.

    Args:
        content (str): The full content of the validation report in Markdown format.
        json_input (dict): A JSON dictionary containing the scorecard data.
        chart_type (str): The type of chart to generate ('bar' or 'pie').

    Returns:
        dict: A dictionary containing the status and filename of the generated PDF.
    """
    try:
        scorecard_data = json_input.get("pillars", [])

        if not scorecard_data:
            raise ValueError("Error: JSON is missing the 'pillars' key or it is empty.")

        df = pd.DataFrame(scorecard_data)
        df.sort_values(by="score", ascending=False, inplace=True)

        plt.style.use('ggplot')
        fig, ax = plt.subplots(figsize=(10, 6))

        if chart_type == 'bar':
            ax.barh(df['pillar'], df['score'], color='skyblue')
            ax.set_title('Architecture Scorecard Pillar Scores')
            ax.set_xlabel('Score (out of 10)')
            ax.set_ylabel('Pillar')
            ax.set_xlim(0, 10)
            for index, value in enumerate(df['score']):
                ax.text(value + 0.2, index, str(value), va='center')
        elif chart_type == 'pie':
            ax.pie(df['score'], labels=df['pillar'], autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
            ax.axis('equal')
            ax.set_title('Pillar Score Distribution')
        else:
            raise ValueError("Error: Invalid chart_type. Please use 'bar' or 'pie'.")

        plt.tight_layout()

        # Save the figure to an in-memory buffer to get bytes
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()

        image_bytes = buffer.getvalue()
        encoded_image = base64.b64encode(image_bytes).decode('utf-8')

        # Construct the HTML <img> tag with the Base64 data
        image_tag = f'<img src="data:image/png;base64,{encoded_image}" alt="Scorecard Chart" style="max-width: 100%; height: auto;">'

        # Insert the image tag into the Markdown content after a specific heading.
        # This is more robust than simple concatenation.
        chart_insertion_point = "## Pillar Scores"
        if chart_insertion_point in content:
            content = content.replace(chart_insertion_point, f"{chart_insertion_point}\n\n{image_tag}\n\n")
        else:
            # Fallback if the heading is not found, prepend to the content
            content = f"{image_tag}\n\n{content}"

        current_architecture_artifact = await tool_context.load_artifact(filename="current_architecture.png")
        improved_architecture_artifact = await tool_context.load_artifact(filename="improved_architecture.png")

        current_architecture_bytes = current_architecture_artifact.inline_data.data
        improved_architecture_bytes = improved_architecture_artifact.inline_data.data

        encoded_current_architecture_image = base64.b64encode(current_architecture_bytes).decode('utf-8')
        encoded_improved_architecture_image = base64.b64encode(improved_architecture_bytes).decode('utf-8')
        
        current_architecture_image_tag = f'<img src="data:image/png;base64,{encoded_current_architecture_image}" alt="Current Architecture diagram" style="max-width: 100%; height: auto;">'
        improved_architecture_image_tag = f'<img src="data:image/png;base64,{encoded_improved_architecture_image}" alt="Improved Architecture diagram" style="max-width: 100%; height: auto;">'
        

        current_architecture_insertion_point = "## Current Architecture"
        parts = content.split(current_architecture_insertion_point, 1)

        if len(parts) > 1:
            # If the heading is found, insert the chart between the parts.
            content = f"{parts[0]}{current_architecture_insertion_point}\n\n{current_architecture_image_tag}\n\n{parts[1]}"
        else:
            # If the heading is not found, prepend the chart to the content.
            content = f"{current_architecture_image_tag}\n\n{content}"

        improved_architecture_insertion_point = "## Improved Architecture"
        parts = content.split(improved_architecture_insertion_point, 1)

        if len(parts) > 1:
            # If the heading is found, insert the chart between the parts.
            content = f"{parts[0]}{improved_architecture_insertion_point}\n\n{improved_architecture_image_tag}\n\n{parts[1]}"
        else:
            # If the heading is not found, prepend the chart to the content.
            content = f"{improved_architecture_image_tag}\n\n{content}"

        # 1. Convert Markdown to HTML
        html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])

        # 2. Add inline CSS for styling the HTML
        css_string = """
        @page { size: A4; margin: 0.5in; }
        body { font-family: 'Helvetica', sans-serif; font-size: 12pt; line-height: 1.5; color: #333333; }
        img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
        h1 { font-size: 24pt; color: #2a4365; text-align: center; margin-top: 1em; padding-bottom: 0.2em; border-bottom: 2px solid #e2e8f0; }
        h2 { font-size: 18pt; color: #4a5568; margin-top: 1.5em; margin-bottom: 0.5em; }
        h3 { font-size: 16pt; color: #718096; margin-top: 1.5em; margin-bottom: 0.5em; }
        h4 { font-size: 14pt; color: #a0aec0; margin-top: 1.5em; margin-bottom: 0.5em; }
        p { margin-top: 0.5em; margin-bottom: 1em; text-align: justify; }
        table { border-collapse: collapse; width: 100%; margin-top: 1em; margin-bottom: 1em; }
        th, td { border: 1px solid #e2e8f0; padding: 8px; text-align: left; }
        th { background-color: #4a5568; color: white; font-weight: bold; }
        tr:nth-child(even) { background-color: #f7fafc; }
        code { font-family: 'Courier New', Courier, monospace; background-color: #e2e8f0; padding: 2px 4px; border-radius: 4px; }
        pre { background-color: #e2e8f0; padding: 10px; border-radius: 8px; overflow-x: auto; }
        """

        # Create the complete HTML document
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Generated PDF</title>
            <style>{css_string}</style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # 3. Use WeasyPrint to render the HTML to PDF
        font_config = FontConfiguration()
        html = HTML(string=full_html, base_url='.')
        pdf_bytes = html.write_pdf(stylesheets=[CSS(string=css_string, font_config=font_config)])

        session_id = tool_context._invocation_context.session.id
        unique_id = os.urandom(4).hex()
        output_filename = f"{session_id}_{unique_id}_validation_report.pdf"

        # Create the ADK artifact with the correct MIME type
        artifact = types.Part(
            inline_data=types.Blob(
                data=pdf_bytes,
                mime_type="application/pdf"
            )
        )

        await tool_context.save_artifact(
            filename=output_filename,
            artifact=artifact
        )

        return {"status": "success", "filename": output_filename}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"status": "failed", "error": str(e)}

    

async def execute_python_code(code_string: str, type_architecture: str, tool_context: ToolContext) -> str:
    """
    Executes Python code, reads the generated image, and saves it to an artifact.
    
    Args:
        code_string: The Python code to be executed.
        type_architecture: either "current_architecture' or 'improved_architecture'. Will be used as filename for reference.

    Returns:
        A string indicating success or failure.
    """
    image_filename = f"diagram.png"

    
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
        output_filename = f"{type_architecture}.png"
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