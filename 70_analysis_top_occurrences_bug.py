import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.query import Metrics
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")

load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_key),
)

collection = client.collections.get(COLLECTION_NAME)

responses = []

for i in range(10):
    response = collection.aggregate.over_all(
        return_metrics=Metrics("technicalDomain").text(
            top_occurrences_count=True,
            top_occurrences_value=True,
            min_occurrences=0  # Threshold minimum count
        )
    )

    if response.properties["technicalDomain"] not in responses:
        responses.append(response.properties["technicalDomain"])
        print(f"Response {i}: {response.properties['technicalDomain']}")
    else:
        print("Duplicate response found, skipping.")
        pass

print(len(responses))

client.close()
