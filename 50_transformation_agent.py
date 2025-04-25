import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import DataType
from weaviate.agents.classes import Operations
from weaviate.agents.transformation import TransformationAgent
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME, TECHNICAL_DOMAIN_CATEGORIES, ROOT_CAUSE_CATEGORIES, ACCESS_CONTEXT_CATEGORIES

weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_key = os.getenv("WEAVIATE_API_KEY")
load_dotenv()

client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url, auth_credentials=Auth.api_key(weaviate_key)
)

add_technical_complexity = Operations.append_property(
    property_name="technicalComplexity",
    data_type=DataType.INT,
    view_properties=["conversation"],
    instruction="""
    Rate the technical complexity of the user's forum post query
    on a scale from 1 to 5, where 1 is very simple and 5 is very complex.
    """,
)

add_technical_domain = Operations.append_property(
    property_name="technicalDomain",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Identify the primary technical domain of the user's forum post query.
    The answer must be one of the following:
    {TECHNICAL_DOMAIN_CATEGORIES.keys()}

    The definitions of the categories are as follows:
    {TECHNICAL_DOMAIN_CATEGORIES}

    Remember that the answer must be one of these categories:
    {TECHNICAL_DOMAIN_CATEGORIES.keys()}
    """,
)

add_root_cause_category = Operations.append_property(
    property_name="rootCauseCategory",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Based on the text, what was the fundamental issue behind the user's question? The answer must be one of the following categories:
    {ROOT_CAUSE_CATEGORIES.keys()}

    The definitions of the categories are as follows:
    {ROOT_CAUSE_CATEGORIES}
    For example, if the user was confused about how to use a specific feature of Weaviate, the answer should be "conceptual_misunderstanding".

    Remember that the answer must be one of these categories:
    {ROOT_CAUSE_CATEGORIES.keys()}
    """,
)

add_access_context = Operations.append_property(
    property_name="accessContext",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Based on the text, how was the user trying to access Weaviate? The answer must be one of the following categories:

    {ACCESS_CONTEXT_CATEGORIES.keys()}

    The definitions of the categories are as follows:
    {ACCESS_CONTEXT_CATEGORIES}
    For example, if the user was using the Weaviate Python client library, the answer should be "python_client".

    Remember that the answer must be one of these categories:
    {ACCESS_CONTEXT_CATEGORIES.keys()}
    """,
)

was_it_caused_by_outdated_stack = Operations.append_property(
    property_name="causedByOutdatedStack",
    data_type=DataType.BOOL,
    view_properties=["conversation", "title"],
    instruction="""
    Based on the text, was the user's question caused by an outdated version of Weaviate or its components, such as the client library being used?
    """,
)

was_it_a_documentation_gap = Operations.append_property(
    property_name="isDocumentationGap",
    data_type=DataType.BOOL,
    view_properties=["conversation", "title"],
    instruction="""
    Based on the text, identify whether the user's question was caused by a lack of documentation or unclear instructions regarding Weaviate.

    This does not include cases where the documentation exists, and the user did not find it, or did not read it.
    This also does not include cases where the user was asking about a feature that is not supported by Weaviate,
    or the user was asking about a feature that is not part of a first-party Weaviate product, such as a third-party integration or a custom implementation.
    This also does not include cases where there was a bug in the code, or the user was using an outdated version of Weaviate or its components.

    Only mark this as true if the user was asking about a feature or an aspect
    that is not covered by the documentation, or the documentation was unclear or incorrect.
    """,
)

create_summary = Operations.append_property(
    property_name="summary",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction="""
    Briefly summarize the user's question and the resolution provided (if any) in a few sentences.
    """,
)

ta = TransformationAgent(
    client=client,
    collection=COLLECTION_NAME,
    operations=[
        add_technical_complexity,
        add_technical_domain,
        add_root_cause_category,
        add_access_context,
        was_it_caused_by_outdated_stack,
        was_it_a_documentation_gap,
        create_summary
    ],
)

ta_response = ta.update_all()


def get_ta_status(agent_instance, workflow_id):
    # Rough code to check the status of the TA workflow
    import time
    from datetime import datetime, timezone

    while True:
        status = agent_instance.get_status(workflow_id=workflow_id)

        if status["status"]["state"] != "running":
            break

        # Parse start_time and make it timezone-aware (assuming it's in UTC)
        start = datetime.strptime(status["status"]["start_time"], "%Y-%m-%d %H:%M:%S")
        start = start.replace(tzinfo=timezone.utc)

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Calculate elapsed time
        elapsed = (now - start).total_seconds()

        print(f"Waiting... Elapsed time: {elapsed:.2f} seconds")
        time.sleep(10)

    # Calculate total time
    if status["status"]["total_duration"]:
        total = status["status"]["total_duration"]
    else:
        start = datetime.strptime(status["status"]["start_time"], "%Y-%m-%d %H:%M:%S")
        end = (
            datetime.now()
            if not status["status"]["end_time"]
            else datetime.strptime(status["status"]["end_time"], "%Y-%m-%d %H:%M:%S")
        )
        total = (end - start).total_seconds()

    print(f"Total time: {total:.2f} seconds")
    print(status)


get_ta_status(agent_instance=ta, workflow_id=ta_response.workflow_id)


client.close()
