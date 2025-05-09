import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.aggregate import GroupByAggregate
from weaviate.classes.generate import GenerativeConfig
from weaviate.classes.query import Filter
import os
from dotenv import load_dotenv
from helpers import COLLECTION_NAME
import re
from colorama import init, Fore, Style

# Initialize colorama for colored terminal output
init()

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

analysis_props = [
    "technicalComplexity",
    "technicalDomain",
    "rootCauseCategory",
    "accessContext",
    "causedByOutdatedStack",
    "isDocumentationGap"
]

for prop in analysis_props:

    response = collection.aggregate.over_all(
        group_by=GroupByAggregate(prop=prop)
    )
    print(f"\nProperty: {prop}")
    for group in response.groups:
        print(f"Value: {group.grouped_by} Count: {group.total_count}")


prop = "technicalDomain"
response = collection.aggregate.over_all(
    group_by=GroupByAggregate(prop=prop),
    filters=Filter.by_property(name="rootCauseCategory").equal("conceptual_misunderstanding")
)

print(f"\nProperty: {prop}")
for group in response.groups:
    print(f"Value: {group.grouped_by} Count: {group.total_count}")


response = collection.generate.fetch_objects(
    filters=(
        Filter.by_property(name="rootCauseCategory").equal("conceptual_misunderstanding") &
        Filter.by_property(name="technicalDomain").equal("queries")
    ),
    limit=100,
    generative_provider=GenerativeConfig.anthropic(model="claude-3-7-sonnet-latest"),
    grouped_task="""
    From these Weaviate Forum post conversations, identify 3-5 most common things
    that we can help users to understand better about Weaviate queries.
    If possible, also provide a count of each type in the sample.
    """,
    grouped_properties=["summary", "title"]
)

print(f"\n{response.generative.text}")






# response = collection.generate.fetch_objects(
#     filters=(
#         Filter.by_property(name="isDocumentationGap").equal(True)
#     ),
#     limit=5,
#     generative_provider=GenerativeConfig.anthropic(
#         model="claude-3-7-sonnet-latest",
#     ),
#     single_prompt="""
#     For this query, what update to the documentation would have helped the user to solve their problem
#     before asking the question?

#     Here is the conversation:
#     {conversation}
#     """
# )

# print("Examples:")
# for o in response.objects:
#     print("\n" + "-" * 50)
#     print(f"Object ID: {o.uuid}")
#     print(f"Title: {Fore.CYAN}{o.properties['title']}{Style.RESET_ALL}")

#     print(f"{Fore.GREEN}\n== ANALYSIS =={Style.RESET_ALL}")
#     print(f"Technical Complexity: {o.properties['technicalComplexity']}")
#     print(f"Root Cause Category: {o.properties['rootCauseCategory']}")
#     print(f"Access Context: {o.properties['accessContext']}")
#     print(f"Caused By Outdated Stack: {o.properties['causedByOutdatedStack']}")
#     print(f"Is Documentation Gap: {o.properties['isDocumentationGap']}")

#     print(f"{Fore.GREEN}\n== SUMMARY =={Style.RESET_ALL}")
#     print(f"{Fore.LIGHTMAGENTA_EX}{o.generative.text}{Style.RESET_ALL}")

#     conversation = o.properties['conversation']

#     # First normalize all types of line endings
#     conversation = conversation.replace('\r\n', '\n').replace('\r', '\n')

#     # Clean up excess whitespace around newlines without removing paragraph breaks
#     conversation = re.sub(r'[ \t]+\n', '\n', conversation)  # Remove trailing spaces before newlines
#     conversation = re.sub(r'\n[ \t]+', '\n', conversation)  # Remove leading spaces after newlines

#     # Replace sequences of 3 or more newlines with exactly two newlines
#     conversation = re.sub(r'\n{3,}', '\n\n', conversation)

#     # Remove new lines at the beginning and end
#     conversation = conversation.strip()

#     limit = 200
#     print(f"{Fore.GREEN}\nConversation (first {limit} chars):{Style.RESET_ALL}")
#     print(f"{Fore.LIGHTBLACK_EX}{conversation[:limit]}{Style.RESET_ALL}...")

client.close()
