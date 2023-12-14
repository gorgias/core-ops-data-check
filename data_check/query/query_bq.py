import pandas as pd
from query_client import QueryClient
import streamlit as st
from google.cloud import bigquery
from models.table import TableSchema
from google.oauth2 import service_account
from os import getenv

USE_STREAMLIT_SECRET = getenv("USE_STREAMLIT_SECRET", False)

class QueryBigQuery(QueryClient):

    def __init__(self):
        self.client = self.init_client()

    @st.cache_resource
    def get_credentials(_self):
        # Create API client from Streamlit Secret
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return credentials

    @st.cache_resource
    def init_client(_self) -> bigquery.Client:
        if not USE_STREAMLIT_SECRET:
            return bigquery.Client()
        credentials = _self.get_credentials()
        return bigquery.Client(credentials=credentials)

    @st.cache_data(ttl=600)
    def get_table(self, table: str) -> bigquery.Table:
        return self.client.get_table(table)

    @st.cache_data(ttl=600)
    def run_query_to_dataframe(_self, query: str) -> pd.DataFrame:
        return _self.run_query_job(query).to_dataframe()

    def run_query_job(_self, query: str) -> bigquery.QueryJob:
        query_job = _self.client.query(query)
        return query_job.result()

    def query_table(_self, table: str, columns: list[str]) -> pd.DataFrame:
        columns = ", ".join(columns)
        query = f"""
            SELECT
                {columns}
            FROM `{table}`
        """
        return _self.run_query_to_dataframe(query=query)

    @st.cache_data(ttl=30)
    def get_table_schema_from_table(_self, table: str) -> TableSchema:
        """Get the schema of a table"""
        table_bq = _self.client.get_table(table)
        return TableSchema.from_bq_table(table=table_bq)

    @st.cache_data(ttl=30)
    def get_table_schema_from_sql(_self, query: str) -> TableSchema:
        """Get the schema of a table from a query"""
        query_job = _self.run_query_job(query)
        return TableSchema.from_bq_query_job(query_job)
