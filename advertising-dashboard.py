import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates  # Import mdates for date formatting

# Load the main campaign data
data = pd.read_excel('Sponsored_Products_Search_term_report-2.xlsx')
data.columns = data.columns.str.strip()  # Remove leading/trailing spaces
data = data.rename(columns={'Start Date': 'Date'})  # Rename 'Start Date' to 'Date'

# Load the sales performance data
try:
    sales_data = pd.read_csv('BusinessReport-2-16-25-2.csv')
    sales_data.columns = sales_data.columns.str.strip()  # Clean column names
except Exception as e:
    st.error(f"Error loading the sales performance data: {e}")
    sales_data = pd.DataFrame()  # Fallback to an empty DataFrame

# Set the title of the Streamlit app
st.title("Campaign Performance Dashboard")

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_tab = st.sidebar.radio("Select a tab:", ["Campaign Performance", "Sales Performance"])

if selected_tab == "Campaign Performance":
    # Basic metrics calculation
    total_impressions = data['Impressions'].sum()
    total_clicks = data['Clicks'].sum()
    total_spend = data['Spend'].sum()
    total_sales = data['7 Day Total Sales'].sum()

    # Display overall metrics
    st.write("### Campaign Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Impressions", f"{total_impressions:,.0f}")
    with col2:
        st.metric("Total Clicks", f"{total_clicks:,.0f}")
    with col3:
        st.metric("Total Spend", f"${total_spend:,.2f}")
    with col4:
        st.metric("Total Sales", f"${total_sales:,.2f}")

    # Campaign Performance Metrics by Search Term
    performance_metrics = data.groupby('Customer Search Term').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        '7 Day Total Sales': 'sum',
        '7 Day Total Orders (#)': 'sum'
    }).reset_index()

    # Calculate additional metrics
    performance_metrics['CTR'] = (performance_metrics['Clicks'] / performance_metrics['Impressions'].replace(0, 1) * 100).round(2)
    performance_metrics['CPC'] = (performance_metrics['Spend'] / performance_metrics['Clicks'].replace(0, 1)).round(2)
    performance_metrics['ROAS'] = (performance_metrics['7 Day Total Sales'] / performance_metrics['Spend'].replace(0, 1)).round(2)
    performance_metrics = performance_metrics.sort_values(by='Impressions', ascending=False)

    # Display the performance metrics table
    st.write("### Campaign Performance by Search Term")
    st.dataframe(performance_metrics)

    # Time Series Analysis
    daily_performance = data.groupby('Date').agg({
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Spend': 'sum',
        '7 Day Total Sales': 'sum'
    }).reset_index()

    # Convert 'Date' to datetime format
    daily_performance['Date'] = pd.to_datetime(daily_performance['Date'])

    # Plot daily trends
    st.write("### Daily Performance Trends")

    # Plot for Impressions and Clicks
    fig3, ax3 = plt.subplots()
    ax3.plot(daily_performance['Date'], daily_performance['Impressions'], label='Impressions')
    ax3.plot(daily_performance['Date'], daily_performance['Clicks'], label='Clicks')
    ax3.set_title('Daily Impressions and Clicks')

    # Format x-axis
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))  # Format to show day and month
    plt.xticks(rotation=45)  # Rotate x-axis labels
    ax3.legend()
    st.pyplot(fig3)

    # Plot for Spend and Sales
    fig4, ax4 = plt.subplots()
    ax4.plot(daily_performance['Date'], daily_performance['Spend'], label='Spend')
    ax4.plot(daily_performance['Date'], daily_performance['7 Day Total Sales'], label='Sales')
    ax4.set_title('Daily Spend and Sales')

    # Format x-axis
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))  # Format to show day and month
    plt.xticks(rotation=45)  # Rotate x-axis labels
    ax4.legend()
    st.pyplot(fig4)

    # Performance Summary Statistics
    st.write("### Performance Summary Statistics")
    summary_stats = performance_metrics.describe()

    # Format the summary statistics
    formatted_stats = summary_stats[['Impressions', 'Clicks', 'Spend', '7 Day Total Sales', 'CTR', 'CPC', 'ROAS']].copy()
    formatted_stats.loc['mean'] = formatted_stats.loc['mean'].round(2)
    formatted_stats.loc['std'] = formatted_stats.loc['std'].round(2)
    formatted_stats.loc['min'] = formatted_stats.loc['min'].round(2)
    formatted_stats.loc['25%'] = formatted_stats.loc['25%'].round(2)
    formatted_stats.loc['50%'] = formatted_stats.loc['50%'].round(2)
    formatted_stats.loc['75%'] = formatted_stats.loc['75%'].round(2)

    # Format Spend and Sales as currency
    formatted_stats.loc[:, ['Spend', '7 Day Total Sales']] = formatted_stats.loc[:, ['Spend', '7 Day Total Sales']].applymap(lambda x: f"${x:,.2f}")

    # Display the formatted summary statistics
    st.dataframe(formatted_stats)

elif selected_tab == "Sales Performance":
    st.write("### Sales Performance Report")

    if sales_data.empty:
        st.warning("No sales data available. Please check the file path or data.")
    else:
        # Convert 'Date' to datetime format
        sales_data['Date'] = pd.to_datetime(sales_data['Date'])

        sales_data['Ordered Product Sales'] = (
            sales_data['Ordered Product Sales']
            .replace('[\$,%]', '', regex=True)  # Remove dollar signs and commas
            .astype(float)  # Convert to float
        )
# Clean percentage columns (e.g., 'Unit Session Percentage', 'Featured Offer (Buy Box) Percentage')
        percentage_columns = [
            'Unit Session Percentage', 
            'Featured Offer (Buy Box) Percentage',
            'Unit Session Percentage - B2B', 
            'Featured Offer (Buy Box) Percentage - B2B'
        ]
        for col in percentage_columns:
            if col in sales_data.columns:
                sales_data[col] = (
                    sales_data[col]
                    .replace('%', '', regex=True)  # Remove percentage signs
                    .astype(float)  )
        # Display overall sales metrics
        st.write("#### Sales Overview since October 2024")
        total_ordered_sales = sales_data['Ordered Product Sales'].sum()
        total_units_ordered = sales_data['Units Ordered'].sum()
        total_sessions = sales_data['Sessions - Total'].sum()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Ordered Sales", f"${total_ordered_sales:,.2f}")
        with col2:
            st.metric("Total Units Ordered", f"{total_units_ordered:,.0f}")
        with col3:
            st.metric("Total Sessions", f"{total_sessions:,.0f}")

        # Plot daily sales trends
        st.write("#### Daily Sales Trends")
        fig, ax = plt.subplots()
        ax.plot(sales_data['Date'], sales_data['Ordered Product Sales'], label='Ordered Product Sales')
        ax.plot(sales_data['Date'], sales_data['Units Ordered'], label='Units Ordered')
        ax.set_title('Daily Sales and Units Ordered')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))  # Format to show day and month
        plt.xticks(rotation=45)  # Rotate x-axis labels
        ax.legend()
        st.pyplot(fig)

        # Display sales performance table
        st.write("#### Sales Performance Data")
        st.dataframe(sales_data)

        # Additional metrics
        st.write("#### Additional Metrics")
        average_unit_session_percentage = sales_data['Unit Session Percentage'].mean()
        average_buy_box_percentage = sales_data['Featured Offer (Buy Box) Percentage'].mean()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Average Unit Session Percentage", f"{average_unit_session_percentage:.2f}%")
        with col2:
            st.metric("Average Buy Box Percentage", f"{average_buy_box_percentage:.2f}%")