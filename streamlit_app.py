import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import Database 

def get_selected_guild(guild_ids):
    """
    Returns the selected guild from the dropdown

    Args:
        guild_ids (list): List of guild ids
    """
    return st.selectbox('Select a Guild', guild_ids)

def plot_chart(x_data, y_data, title, x_label, y_label):
    """
    Plots a chart using the given data

    Args:
        x_data (list): List of x data
        y_data (list): List of y data
        title (str): Title of the chart
        x_label (str): Label for the x axis
        y_label (str): Label for the y axis
    """
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    st.pyplot(fig)

def main():
    """
    Main function that runs the streamlit app
    """
    # Initialize the database
    db = Database()

    message_data = db.get_message_data_per_week_by_guild()
    unique_users_data = db.get_unique_users_by_week_by_guild()

    # Convert data to DataFrames for easier manipulation
    message_df = pd.DataFrame(message_data)
    unique_users_df = pd.DataFrame(unique_users_data)

    st.title('Guild Statistics')

    selected_guild = get_selected_guild(message_df['guild_id'].unique())

    # Filter data for the selected guild
    filtered_message_df = message_df[message_df['guild_id'] == selected_guild]
    filtered_unique_users_df = (
        unique_users_df[unique_users_df['guild_id'] == selected_guild]
    )

    # Plot Messages per Week
    plot_chart(
        filtered_message_df['week_number'],
        filtered_message_df['message_count'],
        'Messages per Week', 
        'Week Number', 
        'Message Count'
    )

    # Plot Unique Users per Week
    plot_chart(
        filtered_unique_users_df['week_number'],
        filtered_unique_users_df['unique_users'],
        'Unique Users per Week',
        'Week Number', 
        'Unique User Count'
    )

if __name__ == "__main__":
    main()
