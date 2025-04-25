import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.generate import GenerativeConfig
import os
from dotenv import load_dotenv

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

collection_name = "ForumPost"

collection = client.collections.get(collection_name)

response = collection.query.fetch_objects(
    limit=50,
)

for o in response.objects:
    print(f"\nObject ID: {o.uuid}")
    for k, v in o.properties.items():
        if k == "conversation":
            v = v[:100] + "..."
        print(f"{k}: {v}")

client.close()
