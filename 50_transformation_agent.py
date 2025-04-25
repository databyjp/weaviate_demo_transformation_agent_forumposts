import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import DataType
from weaviate.agents.classes import Operations
from weaviate.agents.transformation import TransformationAgent
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME

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

technical_domains = {
    "server_setup": "Setup and configuration of the Weaviate database server",
    "ingestion": "Ingesting data into Weaviate, including collection configuration, creation and data import such as batch imports",
    "queries": "Querying Weaviate, including vector, keyword, and hybrid queries",
    "deployment": "Deployment of Weaviate, including Docker, Kubernetes, and cloud deployment",
    "security": "Security-related issues, including authentication, authorization, and data protection",
    "integration": "About integrating Weaviate with other systems or tools",
    "others": "Others not covered by the above categories"
}

add_technical_domain = Operations.append_property(
    property_name="technicalDomain",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Identify the primary technical domain of the user's forum post query.
    The answer must be one of the following:
    {technical_domains.keys()}

    The definitions of the categories are as follows:
    {technical_domains}

    Remember that the answer must be one of these categories:
    {technical_domains.keys()}
    """,
)

root_cause_categories = {
    "conceptual_misunderstanding": "A misunderstanding of Weaviate's underlying concepts or specific functionality",
    "incorrect_configuration": "Incorrect configuration of Weaviate or its components",
    "incorrect_usage": "Incorrect usage of Weaviate, such as incorrect API calls or queries",
    "data_modeling": "Issues related to data modeling, such as schema design or data relationships",
    "performance": "Performance-related issues, such as slow queries or high resource usage",
    "bug_or_limit": "A bug or limitation in Weaviate, not allowing the user to do what they wanted",
    "other": "Others not covered by the above categories"
}

add_root_cause_category = Operations.append_property(
    property_name="rootCauseCategory",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Based on the text, what was the fundamental issue behind the user's question? The answer must be one of the following categories:
    {root_cause_categories.keys()}

    The definitions of the categories are as follows:
    {root_cause_categories}
    For example, if the user was confused about how to use a specific feature of Weaviate, the answer should be "conceptual_misunderstanding".

    Remember that the answer must be one of these categories:
    {root_cause_categories.keys()}
    """,
)

access_context_categories = {
    "python_client": "Using the offcial Weaviate Python client library",
    "ts_client": "Using the offcial Weaviate JavaScript/TypeScript client library",
    "go_client": "Using the offcial Weaviate Go/Golang client library",
    "java_client": "Using the offcial Weaviate Java client library",
    "cloud_console": "Through the Weaviate Cloud console",
    "llm_framework": "Through an LLM framework, such as LangChain or LlamaIndex",
    "rest_api": "Using the Weaviate REST API directly, including GraphQL queries",
    "other": "Others not covered by the above categories"
}

add_access_context = Operations.append_property(
    property_name="accessContext",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction=f"""
    Based on the text, how was the user trying to access Weaviate? The answer must be one of the following categories:

    {access_context_categories.keys()}

    The definitions of the categories are as follows:
    {access_context_categories}
    For example, if the user was using the Weaviate Python client library, the answer should be "python_client".

    Remember that the answer must be one of these categories:
    {access_context_categories.keys()}
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
    Based on the text, identify whether the user's question was caused by a lack of documentation or unclear instructions.

    This does not include cases where the documentation exists, and the user did not find it, or did not read it.
    This also does not include cases where there was a bug in the code, or the user was using an outdated version of Weaviate or its components.

    Only mark this as true if the user was asking about a feature or an aspect
    that is not covered by the documentation, or the documentation was unclear or incorrect.
    """,
)

summary = Operations.append_property(
    property_name="summary",
    data_type=DataType.TEXT,
    view_properties=["conversation", "title"],
    instruction="""
    Summarize the user's question and the solution provided in a few sentences, like this:
    {
        "question": "<SUMMARY OF THE QUESTION>",
        "solution": "<SUMMARY OF THE SOLUTION>"
    }

    If there was no solution provided, set "solution": None.
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
