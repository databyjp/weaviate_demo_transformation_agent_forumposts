import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.generate import GenerativeConfig
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_key),
    headers={
        "X-Anthropic-Api-Key": anthropic_key,
    }
)

collection = client.collections.get(COLLECTION_NAME)

response = collection.generate.fetch_objects(
    limit=30,
    grouped_task="""
    Using this sample of Weaviate Forum post conversations and common sense,
    catagorize these forum posts for support topics into 5-10 categories.
    We will use them on a larger dataset, so please make sure the categories are general enough.
    Write each category also into a snake case format, like 'data_import'.
    """,
    generative_provider=GenerativeConfig.anthropic(
        model="claude-3-7-sonnet-latest"
    )
)

print(response.generative.text)

client.close()
