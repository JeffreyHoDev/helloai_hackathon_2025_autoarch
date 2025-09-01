from google.cloud import asset_v1
from google.adk.tools import ToolContext
import google.auth 
from google.auth import impersonated_credentials
import json

def list_gcp_project_resources(project_id: str, tool_context: ToolContext) -> list:
    """
    Lists all resources implemented in a specific Google Cloud Platform project
    using the Cloud Asset Inventory API.

    Args:
        project_id: The ID of the GCP project (e.g., "my-project-123").

    Returns:
        A list of resource dictionaries, where each dictionary represents an asset
        and contains its metadata. Returns an empty list if no resources are found
        or an error occurs.
    """
    try:
        impersonated_email = "agent-sa@subhadipmitra-pso.iam.gserviceaccount.com"

        # Create the credentials object that will be used to generate the impersonated credentials.
        # This could be your user credentials from 'gcloud auth application-default login'
        # or other credentials available in your environment.
        credentials, project = google.auth.default()


        sa_impersonated_credentials = impersonated_credentials.Credentials(
            source_credentials=credentials,
            target_principal=impersonated_email,
            target_scopes=["https://www.googleapis.com/auth/cloud-platform"], # The required scopes
            lifetime=3600,  # The lifetime of the short-lived access token, in seconds
        )

        # Initialize the Cloud Asset Inventory client.
        # The client automatically handles authentication if running in a GCP
        # environment with appropriate permissions (e.g., 'roles/cloudasset.viewer').
        # If running locally, ensure your gcloud CLI is authenticated or
        # GOOGLE_APPLICATION_CREDENTIALS environment variable is set.
        client = asset_v1.AssetServiceClient(credentials=sa_impersonated_credentials)

        # Define the scope for the search. For a project, the format is "projects/{project_id}".
        scope = f"projects/{project_id}"

        print(f"Searching for all resources in project: {project_id}...")

        # Use the search_all_resources method. This method returns an iterable
        # (pager) that handles pagination automatically.
        # We are not specifying asset_types, so it will search for all supported
        # asset types.
        request = asset_v1.SearchAllResourcesRequest(
            scope=scope,
            # Optional: You can specify asset_types to filter the results.
            # For example: asset_types=["compute.googleapis.com/Instance", "storage.googleapis.com/Bucket"]
            # To get more detailed metadata, you might need to set 'content_type'.
            # However, search_all_resources provides a good overview.
        )

        all_resources = []
        # Iterate through the paginated responses
        for resource in client.search_all_resources(request=request):
            # Each 'resource' object contains various attributes like:
            # .name (full resource name), .asset_type, .project, .display_name,
            # .location, .state, .labels, .network_tags, etc.
            # Convert the resource object to a dictionary for easier handling.
            all_resources.append(asset_v1.ResourceSearchResult.to_dict(resource))
            print(f"Found resource: {resource.asset_type} - {resource.display_name} ({resource.name})")

        print(f"Finished searching. Found {len(all_resources)} resources in project {project_id}.")
        tool_context.state["resources_queried"] = all_resources
        return all_resources

    except Exception as e:
        print(f"An error occurred: {e}")
        return [{"error": str(e)}]