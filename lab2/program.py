
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os
from dotenv import load_dotenv
import traceback


# setting openai configuration details
load_dotenv()


# Helper: safe env read
def env(name):
    v = os.getenv(name)
    if not v:
        print(f"Warning: environment variable {name} is not set or empty")
    return v


# Connect to your Azure AI Foundry project
PROJECT_CONN = env("PROJECT_CONNECTION_STRING")
project_client = None
if PROJECT_CONN:
    try:
        project_client = AIProjectClient.from_connection_string(
            credential=DefaultAzureCredential(),
            conn_str=PROJECT_CONN,
        )
    except Exception:
        print("Failed to create AIProjectClient from connection string:")
        traceback.print_exc()


# Get your embedding deployment client name (this is the connection name in the workspace)
aoai_conn = env("AOAI_CONNECTION_STRING")
print(f"Using AOAI connection: {aoai_conn}")
embedding_deployment_name = env('EMBEDDING_MODEL_DEPLOYMENT_NAME')
print(f"Using embedding deployment: {embedding_deployment_name}")


def list_connections():
    if not project_client:
        print("No project client available to list connections.")
        return []
    try:
        conns = [c.name if hasattr(c, 'name') else getattr(c, 'connection_name', str(c)) for c in project_client.connections.list()]
        print("Available connections in this project:")
        for c in conns:
            print(" -", c)
        return conns
    except Exception:
        print("Failed to list connections:")
        traceback.print_exc()
        return []


embeddings_client = None
if project_client and embedding_deployment_name:
    try:
        # The SDK's get_embeddings_client expects the connection_name as a keyword-only argument.
        embeddings_client = project_client.inference.get_embeddings_client(connection_name=aoai_conn)
    except Exception as e:
        print("Failed to get embeddings client for connection_name=", aoai_conn)
        print(type(e).__name__ + ":", e)
        # Provide diagnostics
        list_connections()


if embeddings_client is None:
    print("No embeddings client available. Exiting.")
    raise SystemExit(1)


# Call it
response = embeddings_client.embed(
    model=embedding_deployment_name,
    input=["Azure AI Foundry lets you manage LLM deployments easily!"]
)

# Extract result
embedding = response.data[0].embedding
print(f"Got embedding of dimension {len(embedding)}")


