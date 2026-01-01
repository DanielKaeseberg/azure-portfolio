import logging
import json
import os
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

app = func.FunctionApp()

# URL: /api/visit
@app.route(route="visit", auth_level=func.AuthLevel.ANONYMOUS)
def UpdateVisitorCount(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing visitor count request.')

    # 1. Get the settings for the app, including secrets.
    # Set this in local.settings.json
    COSMOS_CONN_STR = os.environ.get('CosmosDbConnectionString')
    
    if not COSMOS_CONN_STR:
        return func.HttpResponse("Connection string not found", status_code=500)

    DATABASE_NAME = "VisitorDB"
    CONTAINER_NAME = "stats"
    COUNTER_ID = "main-counter"

    try:
        # 2. Connect to Cosmos DB
        client = CosmosClient.from_connection_string(COSMOS_CONN_STR)
        database = client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)

        # 3. ATOMIC INCREMENT
        # This sends a "Plus 1" instruction to the DB.
        updated_item = container.patch_item(
            item=COUNTER_ID,
            partition_key=COUNTER_ID,
            patch_operations=[
                {'op': 'incr', 'path': '/count', 'value': 1}
            ]
        )
        
        # Get the new number
        current_count = updated_item['count']

    except CosmosResourceNotFoundError:
        # 4. Handle First Run (If the item doesn't exist yet)
        logging.info("Counter not found, creating new one.")
        new_item = {
            'id': COUNTER_ID, 
            'count': 1
        }
        container.create_item(new_item)
        current_count = 1

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return func.HttpResponse(f"Database Error: {str(e)}", status_code=500)

    # 5. Return the result to the browser
    return func.HttpResponse(
        json.dumps({"count": current_count}),
        mimetype="application/json",
        status_code=200
    )