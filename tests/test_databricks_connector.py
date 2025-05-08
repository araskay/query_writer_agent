import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.sql.elements import TextClause
from query_writer.db_connector.databricks_connector import DatabricksConnector


class TestDatabricksConnector(unittest.TestCase):
    """Unit tests for the DatabricksConnector class."""

    def setUp(self):
        """Set up test environment before each test case."""
        # Set environment variables for testing
        self.env_patcher = patch.dict('os.environ', {
            'DATABRICKS_SERVER_HOSTNAME': 'test-hostname',
            'DATABRICKS_HTTP_PATH': 'test-http-path',
            'DATABRICKS_TOKEN': 'test-token',
            'DATABRICKS_CATALOG': 'test-catalog',
            'DATABRICKS_SCHEMA': 'test-schema'
        })
        self.env_patcher.start()
        
        # Create the connector instance
        self.connector = DatabricksConnector()

    def tearDown(self):
        """Clean up after each test case."""
        self.env_patcher.stop()

    def test_init(self):
        """Test the initialization of DatabricksConnector with environment variables."""
        self.assertEqual(self.connector.host, 'test-hostname')
        self.assertEqual(self.connector.http_path, 'test-http-path')
        self.assertEqual(self.connector.access_token, 'test-token')
        self.assertEqual(self.connector.catalog, 'test-catalog')
        self.assertEqual(self.connector.schema, 'test-schema')

    @patch('query_writer.db_connector.databricks_connector.create_engine')
    def test_get_engine(self, mock_create_engine):
        """Test the get_engine method to ensure it properly configures a SQLAlchemy engine."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        engine = self.connector.get_engine()
        
        # Verify the output
        self.assertEqual(engine, mock_engine)
        
        # Verify the correct connection string is used
        expected_conn_string = f"databricks://token:test-token@test-hostname?http_path=test-http-path&catalog=test-catalog&schema=test-schema"
        mock_create_engine.assert_called_once_with(expected_conn_string)

    @patch('query_writer.db_connector.databricks_connector.create_engine')
    @patch('query_writer.db_connector.databricks_connector.text')
    def test_run_query(self, mock_text, mock_create_engine):
        """Test the run_query method to ensure queries are executed correctly."""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        mock_text_clause = MagicMock(spec=TextClause)
        
        mock_text.return_value = mock_text_clause
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value = mock_result
        mock_create_engine.return_value = mock_engine

        test_query = "SELECT * FROM test_table"
        result = self.connector.run_query(test_query)
        
        # Verify the text function was called with the query
        mock_text.assert_called_once_with(test_query)
        
        # Verify that the query was executed with the text clause
        mock_connection.execute.assert_called_once_with(mock_text_clause)
        
        # Verify the result
        self.assertEqual(result, mock_result)

    @patch('query_writer.db_connector.databricks_connector.create_engine')
    def test_run_query_with_invalid_query(self, mock_create_engine):
        """Test the run_query method with an invalid query to ensure proper error handling."""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        
        mock_connection.execute.side_effect = Exception("Invalid SQL query")
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine
        
        # Call the method and expect an exception
        with self.assertRaises(Exception) as context:
            self.connector.run_query("INVALID SQL")
        
            # Verify the error message
            self.assertTrue("Invalid SQL query" in str(context.exception))


if __name__ == '__main__':
    unittest.main()