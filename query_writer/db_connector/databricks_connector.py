import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables from .env file
load_dotenv()

class DatabricksConnector:
    """
    A connector class for establishing connections to Databricks
    
    This class handles authentication and connection management for Databricks
    using environment variables for configuration.

    Environment Variables:
        - DATABRICKS_SERVER_HOSTNAME: The hostname of the Databricks server.
        - DATABRICKS_HTTP_PATH: The HTTP path for the Databricks connection.
        - DATABRICKS_TOKEN: The access token for authentication.
        - DATABRICKS_CATALOG: The catalog to use in the connection.
        - DATABRICKS_SCHEMA: The schema to use in the connection.
    Example:
        >>> connector = DatabricksConnector()
        >>> engine = connector.get_engine()
        >>> result = connector.run_query("SELECT * FROM my_table LIMIT 5")
        >>> for row in result:
        >>>     print(row)
    """
    
    def __init__(self):
        """
        Initialize the Databricks connector with configuration from environment variables.
        """
        self.host = os.getenv("DATABRICKS_SERVER_HOSTNAME")
        self.http_path = os.getenv("DATABRICKS_HTTP_PATH")
        self.access_token = os.getenv("DATABRICKS_TOKEN")
        self.catalog = os.getenv("DATABRICKS_CATALOG")
        self.schema = os.getenv("DATABRICKS_SCHEMA")

    def get_engine(self):
        """
        Create and return a SQLAlchemy engine for Databricks connections.
        
        Returns:
            sqlalchemy.engine.Engine: A configured SQLAlchemy engine for Databricks.
        """
        return create_engine(
            f"databricks://token:{self.access_token}@{self.host}?http_path={self.http_path}&catalog={self.catalog}&schema={self.schema}"
        )

    def run_query(self, query):
        """
        Execute a SQL query against Databricks.
        
        Args:
            query (str): The SQL query to execute.
            
        Returns:
            sqlalchemy.engine.CursorResult: The result of the executed query.
        """
        with self.get_engine().connect() as connection:
            result = connection.execute(text(query))
            return result
