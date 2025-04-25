import weaviate
from weaviate.classes.init import Auth
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME
import pandas as pd

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

objs = []

for o in collection.iterator(
    return_properties=[
        "title",
        "date_created",
        "has_accepted_answer",
        "topic_id",
        # Created by the Transformation Agent
        "technicalComplexity",
        "technicalDomain",
        "rootCauseCategory",
        "accessContext",
        "causedByOutdatedStack",
        "isDocumentationGap",
        "summary"
    ]
):
    objs.append(o.properties)

df = pd.DataFrame(objs)
df.to_csv("data/transformed_data.csv", index=False)

client.close()
