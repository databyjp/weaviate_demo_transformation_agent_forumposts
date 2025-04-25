# COLLECTION_NAME = "ForumPostSmall"  # For smaller collection
COLLECTION_NAME = "ForumPost"  # Full-size collection

TECHNICAL_DOMAIN_CATEGORIES = {
    "server_setup": "Setup and configuration of the Weaviate database server",
    "ingestion": "Ingesting data into Weaviate, including collection configuration, creation and data import such as batch imports",
    "queries": "Querying Weaviate, including vector, keyword, and hybrid queries",
    "deployment": "Deployment of Weaviate, including Docker, Kubernetes, and cloud deployment",
    "security": "Security-related issues, including authentication, authorization, and data protection",
    "integration": "About integrating Weaviate with other systems or tools",
    "others": "Others not covered by the above categories"
}

ROOT_CAUSE_CATEGORIES = {
    "conceptual_misunderstanding": "A misunderstanding of Weaviate's underlying concepts or specific functionality",
    "incorrect_configuration": "Incorrect configuration of Weaviate or its components",
    "incorrect_usage": "Incorrect usage of Weaviate, such as incorrect API calls or queries",
    "data_modeling": "Issues related to data modeling, such as schema design or data relationships",
    "performance": "Performance-related issues, such as slow queries or high resource usage",
    "bug_or_limit": "A bug or limitation in Weaviate, not allowing the user to do what they wanted",
    "other": "Others not covered by the above categories"
}

ACCESS_CONTEXT_CATEGORIES = {
    "python_client": "Using the offcial Weaviate Python client library",
    "ts_client": "Using the offcial Weaviate JavaScript/TypeScript client library",
    "go_client": "Using the offcial Weaviate Go/Golang client library",
    "java_client": "Using the offcial Weaviate Java client library",
    "cloud_console": "Through the Weaviate Cloud console",
    "llm_framework": "Through an LLM framework, such as LangChain or LlamaIndex",
    "rest_api": "Using the Weaviate REST API directly, including GraphQL queries",
    "other": "Others not covered by the above categories"
}
