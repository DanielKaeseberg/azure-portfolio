import unittest
from unittest.mock import patch, MagicMock
import azure.functions as func
import json
import os

from function_app import UpdateVisitorCount

class TestVisitorCounter(unittest.TestCase):
    # Create a fake HTTP request to send to the function
    def setUp(self):
        self.req = func.HttpRequest(
            method='GET',
            body=None,
            url='/api/visit',
            params={}
        )

    # Use @patch to intercept calls to CosmosClient so the real DB isn't hit.
    # We need the second line to create a fake CosmosDbConnectionString. UpdateVisitorCount checks
    # if that environment variable is set, so we make sure to set it to a dummy string.
    @patch('function_app.CosmosClient')
    @patch.dict(os.environ, {"CosmosDbConnectionString": "FakeConnection=String;"})
    def test_update_visitor_count_success(self, mock_cosmos_client):
        """
        Test the "Happy Path": Database exists, item exists, increment works.
        """
        # 1. Setup the Mock Database
        # We have to mock the chain: client -> database -> container -> patch_item
        mock_container = MagicMock()
        
        # When the function asks for a container, give it our fake one
        mock_cosmos_client.from_connection_string.return_value \
            .get_database_client.return_value \
            .get_container_client.return_value = mock_container

        # 2. Define what the fake DB returns when we call 'patch_item'
        mock_container.patch_item.return_value = {'id': 'main-counter', 'count': 42}

        # 3. Run the Function
        response = UpdateVisitorCount(self.req)
        
        # 4. Assertions (The Grading)
        # Did it return 200 OK?
        self.assertEqual(response.status_code, 200)
        
        # Did it return the count from our fake DB (42)?
        body = json.loads(response.get_body())
        self.assertEqual(body['count'], 42)

    @patch('function_app.CosmosClient')
    @patch.dict(os.environ, {"CosmosDbConnectionString": "FakeConnection=String;"})
    def test_first_visitor_creation(self, mock_cosmos_client):
        """
        Test the "Cold Start": Database item doesn't exist yet, needs creation.
        """
        from azure.cosmos.exceptions import CosmosResourceNotFoundError

        mock_container = MagicMock()
        
        mock_cosmos_client.from_connection_string.return_value \
            .get_database_client.return_value \
            .get_container_client.return_value = mock_container

        # 1. Simulate the "Item Not Found" error when patching
        mock_container.patch_item.side_effect = CosmosResourceNotFoundError(message="Not Found")

        # 2. Run the Function
        response = UpdateVisitorCount(self.req)

        # 3. Verify it caught the error and created a new item
        mock_container.create_item.assert_called_once() # Must verify we tried to create it!
        
        body = json.loads(response.get_body())
        self.assertEqual(body['count'], 1)

    @patch.dict(os.environ, {}, clear=True) # Clear env vars to simulate missing key
    def test_missing_connection_string(self):
        """
        Test Configuration Error: What if the secret is missing?
        """
        response = UpdateVisitorCount(self.req)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Connection string", response.get_body().decode())

if __name__ == '__main__':
    unittest.main()