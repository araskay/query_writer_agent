from dotenv import load_dotenv
import os
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

load_dotenv()

class QueryWriter:
    def __init__(self):
        self.instructions = '''
            You are an agent designed to interact with a SQL database.
            Given an input question, create a syntactically correct databricks query to answer the question.
            Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
            You can order the results by a relevant column to return the most interesting examples in the database.
            Never query for all the columns from a specific table, only ask for the relevant columns given the question.
            You have access to tools for interacting with the database.
            Only use the below tools. Only use the information returned by the below tools to construct your final answer.
            You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

            To start you should ALWAYS look at the tables in the database to see what you can query.
            Do NOT skip this step.
            Then you should query the schema of the most relevant tables.

            You do not need to run the query, just provide the SQL query that would answer the question.
            Your job is done once you provide the SQL query.
            You must return the query in the following format:

            ```<query>```
        '''
        self.llm = ChatOpenAI(temperature=0, model='gpt-4o-mini')
        self.db = self.db_databircks_sql_warehouse()

    @staticmethod
    def db_databricks_catalog() -> SQLDatabase:
        '''
        use this fx to connect to a db in databricks catalog
        '''
        db = SQLDatabase.from_databricks(
            catalog=os.environ['DATABRICKS_CATALOG'],
            schema=os.environ['DATABRICKS_SCHEMA'],
            host=os.environ['DATABRICKS_HOST'],
            api_token=os.environ['DATABRICKS_API_TOKEN'],
            warehouse_id=os.environ['DATABRICKS_WAREHOUSE_ID'],
            cluster_id=os.environ['DATABRICKS_CLUSTER_ID']
        )
        return db

    @staticmethod
    def db_databircks_sql_warehouse() -> SQLDatabase:
        '''
        use this fx to connect to a db in databricks sql warehouse
        '''
        db = SQLDatabase.from_databricks(
            catalog=os.environ['DATABRICKS_CATALOG'],
            schema=os.environ['DATABRICKS_SCHEMA'],
            host=os.environ['DATABRICKS_HOST'],
            api_token=os.environ['DATABRICKS_API_TOKEN'],
            warehouse_id=os.environ['DATABRICKS_WAREHOUSE_ID']
        )
        return db
    

    def generate_query(self, question: str) -> dict:
        '''
        Use a react agent to generate a query to answer the question.
        The agent does not run the query, it just returns the query.
        '''

        toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)

        base_prompt = hub.pull('langchain-ai/react-agent-template')
        prompt = base_prompt.partial(instructions=self.instructions)

        tools = toolkit.get_tools()

        agent = create_react_agent(
            prompt=prompt,
            llm=self.llm,
            tools=tools
        )

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, handle_parsing_errors=True, verbose=True
        )

        response = agent_executor.invoke(
            input={
                "input": question
            }
        )

        return response

    @staticmethod
    def response_parser(response: str) -> str:
        '''
        Helper fx to parse the response to get the query.
        '''
        return response['output'].replace('```', '').lstrip('sql')


    def run_query(self, query: str) -> str:
        '''
        Run the query and return the results.
        '''
        return self.db.run(query)

if __name__ == '__main__':
    query = """
        What is the average age?
    """
    query_writer = QueryWriter()
    response = query_writer.generate_query(query)
    print('------- response -------')
    print(response)
    print('------- results -------')
    query_to_run = query_writer.response_parser(response)
    print(query_writer.run_query(query_to_run))

