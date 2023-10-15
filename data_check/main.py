import streamlit as st
import pandas as pd
from data_processor import ComputeDiff
from data_formatter import highlight_selected_text
from data_helpers import get_table_schemas, run_query_compare_primary_keys, get_column_diff_ratios, get_common_schema
from models.table import TableSchema

class DataDiff():
    def __init__(self) -> None:
        self.df1: pd.DataFrame = None
        self.df2: pd.DataFrame = None
        self.diff: ComputeDiff = None

        self.primary_key: str = None
        self.columns_to_compare: str = None

        st.set_page_config(layout="wide")
        st.title('data-diff homemade 🏠')

        if 'config_tables' not in st.session_state:
            st.session_state.config_tables = False

        if 'loaded_tables' not in st.session_state:
            st.session_state.loaded_tables = False

        if 'display_diff' not in st.session_state:
            st.session_state.display_diff = False

        if 'column_to_display' not in st.session_state:
            st.session_state.column_to_display = None

    @staticmethod
    def display_results(results: list) -> None:
        st.table(results)

    def update_first_step(self):
        st.session_state.table1 = st.session_state.temp_table_1
        st.session_state.table2 = st.session_state.temp_table_2
        st.session_state.sampling_rate = st.session_state.temp_sampling_rate
        st.session_state.config_tables = True
        st.session_state.loaded_tables = False

    def update_second_step(self):
        st.session_state.primary_key = st.session_state.temp_primary_key
        st.session_state.is_select_all = st.session_state.temp_is_select_all

        if st.session_state.is_select_all:
            st.session_state.columns_to_compare = st.session_state.common_table_schema.columns_names
        else:
            st.session_state.columns_to_compare = st.session_state.temp_columns_to_compare

        st.session_state.loaded_tables = True

    def update_third_step(self):
        st.session_state.display_diff = True

    def window(self):
        with st.form(key='first_step'):
            st.text_input('Table 1', value="gorgias-growth-production.dbt_activation.act_candu_ai_user_traits", key='temp_table_1')
            st.text_input('Table 2', value="gorgias-growth-development.dbt_development_antoineballiet.act_candu_ai_user_traits", key='temp_table_2')
            st.slider("Data sampling", min_value=10, max_value=100, step=1, key="temp_sampling_rate")
            submit = st.form_submit_button(label='OK', on_click=self.update_first_step)

        if st.session_state.config_tables:
            with st.form(key='second_step'):
                st.write('Retrieving list of common columns...')
                schema_table_1, schema_table_2 = get_table_schemas(st.session_state.table1, st.session_state.table2)
                st.session_state.schema_table_1 = schema_table_1
                st.session_state.schema_table_2 = schema_table_2

                common_table_schema = get_common_schema(st.session_state.table1, st.session_state.table2)
                st.session_state.common_table_schema = common_table_schema

                st.selectbox('Select primary key:', common_table_schema.columns_names, key='temp_primary_key')

                st.multiselect('Select columns to compare:', common_table_schema.columns_names, key='temp_columns_to_compare')
                st.checkbox("Select all", key="temp_is_select_all")

                submit = st.form_submit_button(label='OK', on_click=self.update_second_step)

        if st.session_state.loaded_tables:
            with st.form(key='third_step'):
                # Using BigQueryClient to run queries, output primary keys in common and exclusive to each table on streamlit : display rows in table format
                st.write('Analyzing primary keys...')
                results_primary_keys = run_query_compare_primary_keys(st.session_state.table1, st.session_state.table2, st.session_state.primary_key)
                st.dataframe(results_primary_keys)

                st.write('Computing difference ratio...')
                results_ratio_per_column = get_column_diff_ratios(table1=st.session_state.table1, table2=st.session_state.table2, primary_key=st.session_state.primary_key, selected_columns=st.session_state.columns_to_compare, common_table_schema=st.session_state.common_table_schema, sampling_rate=st.session_state.sampling_rate)
                st.dataframe(results_ratio_per_column)

                st.selectbox('Select column to display full-diff:', st.session_state.columns_to_compare, key='column_to_display')
                button_check = st.form_submit_button(label='Show diff row-wise', on_click=self.update_third_step)

        if st.session_state.display_diff and st.session_state.column_to_display:
            with st.form(key='fourth_step'):
                st.write(f"Displaying rows where {st.session_state.column_to_display} is different...")

                # df = diff.display_diff_rows(st.session_state.column_to_display)

                df = pd.DataFrame({'item_name': ['Chocolate is the best', 'We love Chocolate',
                                                'I would pay money for Chocolate', 'Biscuit',
                                                'Biscuit', 'Biscuit',
                                                'IceCream', 'Dont love IceCream',
                                                'IceCream'],
                                    'value': [90, 50, 86, 87, 42, 48,
                                            68, 92, 102],
                                    'weight': [4, 2, 3, 5, 6, 5, 3, 7,
                                                5]})

                df["highlighted"] = df.apply(highlight_selected_text, axis=1)
                st.markdown(df.to_html(escape=False),unsafe_allow_html=True)

if __name__ == '__main__':
    dd = DataDiff()
    dd.window()