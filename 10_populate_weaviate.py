import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.init import Auth
from weaviate.util import generate_uuid5
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
from tqdm import tqdm
from helpers import COLLECTION_NAME

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")
load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_key)
)

with open("data/simplified_posts.json", "r") as f:
    data = json.load(f)

if COLLECTION_NAME == "ForumPostSmall":
    data = data[:20]

if client.collections.exists(COLLECTION_NAME):
    confirmation = input(
        f"Collection '{COLLECTION_NAME}' already exists. Do you want to delete it? (y/n): "
    )
    if confirmation.lower() == "y":
        client.collections.delete(COLLECTION_NAME)
    else:
        print("Exiting without deleting the collection.")
        client.close()
        exit()

client.collections.create(
    COLLECTION_NAME,
    description="This collection contains conversations from the Weaviate Forum.",
    properties=[
        Property(
            name="user_id",
            description="Unique identifier for the user creating the thread.",
            data_type=DataType.INT
        ),
        Property(
            name="conversation",
            description="Text of the entire forum conversation thread, truncated to 20,000 characters maximum for context limit.",
            data_type=DataType.TEXT,
        ),
        Property(
            name="conversation_full",
            description="Full text of the entire forum conversation thread.",
            data_type=DataType.TEXT,
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
            source_properties=["conversation_full", "title"]
        ),
        Configure.NamedVectors.text2vec_weaviate(
            name="title",
            source_properties=["title"]
        ),
    ],
    replication_config=Configure.replication(factor=3),
    inverted_index_config=Configure.inverted_index(
        index_null_state=True,
        index_timestamps=True,
    )
)

posts = client.collections.get(COLLECTION_NAME)

with posts.batch.fixed_size(200) as batch:
    # Add objects to the batch
    for i, row in tqdm(enumerate(data)):
        row["date_created"] = datetime.fromisoformat(row["date_created"]).replace(tzinfo=timezone.utc)
        if len(row["conversation"]) > 20000:
            row["conversation"] = row["conversation"][:10000] + '...' + row["conversation"][-10000:]
        row["conversation_full"] = row["conversation"]
        batch.add_object(
            properties=row,
            uuid=generate_uuid5(row["topic_id"])
        )

if posts.batch.failed_objects:
    for obj in posts.batch.failed_objects[:5]:
        print(f"Failed to add object {obj['row_id']}: {obj.message}")

print(len(posts))

client.close()
