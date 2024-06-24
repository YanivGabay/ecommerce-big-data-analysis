from modules.analyze_data import user_retention_query
import streamlit as st
import sqlite3
from modules.config_loader import config
import pandas as pd
from modules.sqlite_manager import save_to_sqlite
from utils.logger import Logger
import matplotlib.pyplot as plt
from modules.sqlite_manager import execute_query_to_df
import numpy as np

def show():
    setup_user_ret()
    user_retention()

def setup_user_ret():
    """
    This function is called to set up brand data. It processes data only once per session.
    """
    if 'user_retention_data' not in st.session_state:
        Logger.info("Setting up brand data...")
   
        setup_data()  
        Logger.info("Brand data setup completed.")
        st.session_state['user_retention_data'] = True  # Mark data as prepared

def setup_data():
   
    Logger.info('Executing user_retention_query Query')
    df_nov, df_oct = user_retention_query()
    Logger.info(f"October data: {df_oct.shape[0]} rows, {df_oct.shape[1]} columns")
    Logger.info(f"November data: {df_nov.shape[0]} rows, {df_nov.shape[1]} columns")
    Logger.info('Df headers:')
    Logger.info(df_oct.head())
    Logger.info(df_nov.head())
    Logger.info(' Executed')
    Logger.info('Trying to save data to SQLite')

    save_to_sqlite(df_oct, f"{config.queries_dbs.user_retention.october}", config.queries_dbs.user_retention.table_names.user_retention_oct)
    save_to_sqlite(df_nov, f"{config.queries_dbs.user_retention.november}", config.queries_dbs.user_retention.table_names.user_retention_nov)
   


def user_retention():
    Logger.info('Displaying User Retention')
    st.title('User Retention')
    st.write('This section provides an overview of user retention over different periods.')
    st.write("""
    ### Functionality Overview
    1. **Calculate User Activities**: Analyzes data from the DuckDB database to determine the first and last activities for each user across months.
    2. **Evaluate Retention**: Calculates the retention period for each user, differentiating between users based on their engagement (viewing, cart addition, purchasing).
    3. **Aggregate Data**: Aggregates data to provide insights into average retention days, user engagement, and purchase frequency.
    3. **Save And Load Data**: Saves the aggregated data to SQLite databases for October and November, then loads the data for comparison.
    4. **Compare Data**: Compares the user retention metrics between October and November, displaying the results in a bar chart.
   
             
             ### User Retention Metrics
    - **Average Retention Days**: The average number of days that users remain active.
    - **Total Users**: The total number of users who have been active.
    - **Average Purchase Frequency**: The average number of purchases made by users.
             
    """)
    Logger.info('Loading October and November User Retention Data')
    df_oct = load_monthly_user_retention(f"{config.queries_dbs.user_retention.october}", config.queries_dbs.user_retention.table_names.user_retention_oct)
    df_nov = load_monthly_user_retention(f"{config.queries_dbs.user_retention.november}", config.queries_dbs.user_retention.table_names.user_retention_nov)
    Logger.info('Loaded October and November User Retention Data')

    st.write('#### Joining October and November Data for Comparison')
    if df_oct is not None and df_nov is not None:
        plot_user_retention(df_oct, df_nov)


def plot_user_retention_separate(df_oct, df_nov):
    metrics = ['avg_retention_days', 'total_users', 'avg_purchase_frequency']
    titles = ['Average Retention Days', 'Total Users', 'Average Purchase Frequency']
    colors_oct = ['skyblue', '#C738BD', 'salmon']
    colors_nov = ['#D8EFD3', '#95D2B3', '#F1F8E8']

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    for i, metric in enumerate(metrics):
        oct_value = df_oct[metric].values[0]
        nov_value = df_nov[metric].values[0]
        x = np.arange(2)
        y = [oct_value, nov_value]
        
        axes[i].bar(x, y, color=[colors_oct[i], colors_nov[i]], width=0.4)
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(['October', 'November'])
        axes[i].set_title(titles[i])
        axes[i].set_ylabel(metric)
        
        # Adding the text labels on the bars
        for j, value in enumerate(y):
            axes[i].text(j, value, f'{value:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    st.pyplot(fig)

# This function would be called within your Streamlit application to display the plot.

def plot_user_retention(df_oct, df_nov):
    
    plot_user_retention_separate(df_oct, df_nov)

    # Displaying metrics
    st.write('### October Metrics')
    st.metric("Average Retention Days", f"{df_oct['avg_retention_days'].values[0]:.2f}")
    st.metric("Total Users", f"{df_oct['total_users'].values[0]}")
    st.metric("Average Purchase Frequency", f"{df_oct['avg_purchase_frequency'].values[0]:.2f}")

    st.write('### November Metrics')
    st.metric("Average Retention Days", f"{df_nov['avg_retention_days'].values[0]:.2f}")
    st.metric("Total Users", f"{df_nov['total_users'].values[0]}")
    st.metric("Average Purchase Frequency", f"{df_nov['avg_purchase_frequency'].values[0]:.2f}")

   
def load_monthly_user_retention(db_path, table_name):
    try:


  
        query = f"SELECT * FROM {table_name}"
        df = execute_query_to_df(db_path, query)
    


        
        return df
    except Exception as e:
        Logger.error(f"Error loading data from SQLite database: {str(e)}")
        return None




    

