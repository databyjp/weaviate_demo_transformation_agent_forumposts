import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.init import Auth
from weaviate.util import generate_uuid5
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from tqdm import tqdm

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")
load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_key)
)

collection_name = "ForumPost"

if client.collections.exists(collection_name):
    confirmation = input(
        f"Collection '{collection_name}' already exists. Do you want to delete it? (y/n): "
    )
    if confirmation.lower() == "y":
        client.collections.delete(collection_name)
    else:
        print("Exiting without deleting the collection.")
        client.close()
        exit()

client.collections.create(
    collection_name,
    description="This collection contains conversations from the Weaviate Forum.",
    properties=[
        Property(
            name="user_id",
            description="Unique identifier for the user creating the thread.",
            data_type=DataType.INT
        ),
        Property(
            name="conversation",
            description="Text of the entire forum conversation thread.",
            data_type=DataType.TEXT
        ),
        Property(
            name="date_created",
            description="Date and time when the thread was first created.",
            data_type=DataType.DATE
        ),
        Property(
            name="has_accepted_answer",
            description="Whether the thread has an accepted answer.",
            data_type=DataType.BOOL
        ),
        Property(
            name="title",
            description="Title text of the forum thread.",
            data_type=DataType.TEXT
        ),
        Property(
            name="topic_id",
            description="Unique identifier for the topic of the thread.",
            data_type=DataType.INT
        ),
    ],
    vectorizer_config=[
        Configure.NamedVectors.text2vec_weaviate(
            name="default",
            source_properties=["conversation", "title"]
        ),
        Configure.NamedVectors.text2vec_weaviate(
            name="title",
            source_properties=["title"]
        ),
    ],
)

with open("data/simplified_posts.json", "r") as f:
    data = json.load(f)

data = data[:100]  # Limit to 10 for testing

posts = client.collections.get(collection_name)

with posts.batch.fixed_size(200) as batch:
    # Add objects to the batch
    for i, row in tqdm(enumerate(data)):
        row["date_created"] = datetime.fromisoformat(row["date_created"]).replace(tzinfo=timezone.utc)
        batch.add_object(
            properties=row,
            uuid=generate_uuid5(row["topic_id"])
        )

if posts.batch.failed_objects:
    for obj in posts.batch.failed_objects[:5]:
        print(f"Failed to add object {obj['row_id']}: {obj.message}")

print(len(posts))

client.close()
