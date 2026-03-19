import os
import json
import azure.functions as func
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    # 1. Initialize Cosmos Client (use environment variables for security)
    endpoint = os.environ["COSMOS_DB_ENDPOINT"]
    key = os.environ["COSMOS_DB_KEY"]
    client = CosmosClient(endpoint, key)

    # 2. Connect to database
    database_name = "stats"
    container_name = "VisitorDB"
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # 3. Retrieve the current counter item
    item = container.read_item(item="main-counter", partition_key="main-counter")
    
    # 4. Increment the count
    current_count = item.get("count", 0) 
    item["count"] = current_count + 1

    # 5. Save the updated item back to Cosmos DB
    container.replace_item(item="main-counter", body=item)

    # 6. Return the new count to the website
    return func.HttpResponse(
        json.dumps({"count": item["count"]}),
        mimetype="application/json",
        status_code=200
    )
