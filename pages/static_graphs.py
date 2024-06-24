import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
from modules.sqlite_manager import execute_query_to_df
from modules.config_loader import config
from modules.aggregate_sales_result import AggregateSalesResult
from utils.logger import Logger

def load_user_data():
    table_name = config.table_names.sales_data
    query = f"SELECT user_id, total_events, total_purchases, average_price FROM {table_name}"
    df_oct = execute_query_to_df(config.databases.sales_data.october.db_path, query)
    df_nov = execute_query_to_df(config.databases.sales_data.november.db_path, query)
    return df_oct, df_nov

def show():
    st.title('User Activity Analysis')
    df_oct, df_nov = load_user_data()
    
    with st.expander("October Data Analysis"):
        aggregate_sales_oct = AggregateSalesResult(
        db_path=config.databases.aggregated_sales.october.db_path,
    
        aggregate_sales_table_name=config.table_names.aggregated_sales,
        month = 'October'
        )
        aggregate_sales_oct.show()
        st.markdown("""---""")
        Logger.info('Showing October Data Analysis')
        show_summary(df_oct['average_price'], "Average Price", "October")
        st.markdown("""---""")
        Logger.info('Plotting Purchases')
        plot_purchases(config.databases.sales_data.october.db_path, "Purchases", "October")
        st.markdown("""---""")
        Logger.info('Plotting Violin')
        plot_violin(df_nov['total_events'], "Total Events in October")
        st.markdown("""#### as we can see, the violin plot isnt really "fitting" to our data, so showing the events in buckets next will be much more informative""")
        st.markdown("""---""")
        Logger.info('Plotting Aggregated Bar')
        plot_aggregated_bar(df_nov['total_events'], "Total Events in October")
        st.markdown("""---""")



    with st.expander("November Data Analysis"):
        aggregate_sales_nov = AggregateSalesResult(
        db_path=config.databases.aggregated_sales.november.db_path,

        aggregate_sales_table_name=config.table_names.aggregated_sales,
        month='November'
    )
        aggregate_sales_nov.show()
        st.markdown("""---""")
        show_summary(df_nov['average_price'], "Average Price", "November")
        st.markdown("""---""")
        plot_purchases(config.databases.sales_data.november.db_path, "Purchases", "November")
        st.markdown("""---""")
        plot_violin(df_nov['total_events'], "Total Events in November")
        st.markdown("""---""")
        plot_aggregated_bar(df_nov['total_events'], "Total Events in November")
        st.markdown("""---""")
      

def plot_violin(data, title):
   
    sample_data = data.sample(10000)  # Sample data for better visualization
    plt.figure(figsize=(12, 4))
    sns.violinplot(x=sample_data, inner='point', linewidth=2)
    plt.title(f'Violin Plot of {title}')
    plt.xlabel('Total Events')
    plt.ylabel('Density')
   
    st.pyplot(plt)
    st.write(f"### The violin plot for {title} provides a visual summary of the data's distribution and density, indicating where the data concentrates and tails off.")


def plot_aggregated_bar(data, title):

    # Binning data
    bins = pd.cut(data, [1, 2, 3, 4, 5, 10, 20, 40, 80, 500, 5000, np.inf], right=False)
    bin_counts = bins.value_counts().sort_index()

    plt.figure(figsize=(12, 6))  # Adjusted figure size
    
    barplot = sns.barplot(x=bin_counts.index.categories, y=bin_counts.values, edgecolor='black', linewidth=1.5, hue=bin_counts.index.categories, palette='spring')
    barplot.set_xticks(range(len(bin_counts)))  # Set ticks to match the number of bins
    barplot.set_xticklabels(barplot.get_xticklabels(), rotation=45, ha='right')  # Rotate labels for better visibility

    plt.title(f'Aggregated Bar Chart of {title}')
    plt.xlabel('Event Bins')
    plt.ylabel('Number of Users')
    st.pyplot(plt) 


def show_summary(data, metric, month):
    st.write(f'### Summary Statistics for {metric} in {month}')
    st.write(data.describe())
    st.write(f"### This table provides basic descriptive statistics such as mean, median, and standard deviation for {metric.lower()} which helps in understanding the central tendency and dispersion of {metric.lower()}.")


def plot_purchases(db_path, metric, month):

    query = f"""
    SELECT 
        CASE WHEN total_purchases > 0 THEN 'Purchased' ELSE 'No Purchase' END AS Purchase_Status,
        COUNT(*) as Count
    FROM {config.table_names.sales_data}
    GROUP BY Purchase_Status
    """
    purchases = execute_query_to_df(db_path,query)
    purchases['Percentage'] = purchases['Count'] / purchases['Count'].sum() * 100
    plt.figure(figsize=(8, 6))
    pie = plt.pie(purchases['Percentage'], labels=purchases['Purchase_Status'], autopct='%1.1f%%', startangle=90, colors=['#4CAF50', '#FFC107'])
    plt.title(f'Proportion of Users Making {metric} in {month}')
    plt.legend(pie[0], purchases['Purchase_Status'], title="Purchase Status", loc="upper right", bbox_to_anchor=(1, 0, 0.5, 1))
    st.pyplot(plt)
    st.write(f"### This pie chart illustrates the percentage of users who made purchases versus those who did not in {month}, highlighting consumer behavior trends.")