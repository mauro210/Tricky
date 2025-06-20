import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the parent directory to the path so we can import from the main file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the main file
from utils import (
    get_tricks_df, get_completed_tricks
)

df_tricks = get_tricks_df()
completed_tricks = get_completed_tricks()

# Set page config
st.set_page_config(page_title="Your Progress", layout="wide", initial_sidebar_state="collapsed")

if st.button(":material/arrow_back: All Tricks 🛹"):
    st.switch_page("Home.py")

st.markdown("<h1 style='text-align: center;'>Your Skateboarding Progress</h1>", unsafe_allow_html=True)

# Get data for analysis
df = df_tricks.copy()  # Use a copy of the global df_tricks
completed_list = completed_tricks['completed']

# Create tricks learned count with progress bar
st.subheader("")
total_tricks = len(df)
completed_count = len(completed_list)
completion_percentage = completed_count / total_tricks if total_tricks > 0 else 0

# Create columns to shift the progress bar area to the left
col1, col2, col3 = st.columns([1.2, 2, 0.8])

with col1:
    st.markdown(f"### Tricks Learned: {completed_count}/{total_tricks}")
    st.progress(completion_percentage)

# Add separator
st.markdown("---")

# Display tricks by difficulty category
st.subheader("Tricks by Difficulty Category")

# Count tricks in each category
category_order = ["Beginner", "Easy", "Intermediate", "Advanced", "Expert"]
category_counts = df['Category'].value_counts().reindex(category_order).fillna(0)

# Create a bar chart using Plotly for better visualization
fig = px.bar(
    x=category_counts.index,
    y=category_counts.values,
    labels={'x': 'Difficulty Category', 'y': 'Number of Tricks'},
    title='Distribution of Tricks by Difficulty',
    color=category_counts.index,
    color_discrete_map={
    "Beginner": "#C5E1A5",
    "Easy": "#66BB6A",
    "Intermediate": "#26A69A",
    "Advanced": "#5C6BC0",
    "Expert": "#283593"
    }
)
fig.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig, use_container_width=True)

# Add separator
st.markdown("---")

# Display completion status by category
st.subheader("Your Progress by Category")

# Add a completion status column to the DataFrame
df['Completed'] = df['Trick'].apply(lambda x: x in completed_list)

# Group by category and count completed vs total
category_progress = df.groupby('Category').agg(
    Completed=('Completed', 'sum'),
    Total=('Trick', 'count')
).reset_index()

# Add a percentage column
category_progress['Percentage'] = (category_progress['Completed'] / category_progress['Total'] * 100).round(1)

# Sort by the established category order
category_order_dict = {cat: i for i, cat in enumerate(category_order)}
category_progress['Order'] = category_progress['Category'].map(category_order_dict)
category_progress = category_progress.sort_values('Order').drop('Order', axis=1)

# Create a completion visualization
completion_data = []
for cat in category_order:
    cat_data = category_progress[category_progress['Category'] == cat]
    if not cat_data.empty:
        completed = cat_data['Completed'].iloc[0]
        total = cat_data['Total'].iloc[0]
        completion_data.append({"Category": cat, "Status": "Completed", "Count": completed})
        completion_data.append({"Category": cat, "Status": "Remaining", "Count": total - completed})

completion_df = pd.DataFrame(completion_data)
if not completion_df.empty:
    fig = px.bar(
        completion_df,
        x="Category",
        y="Count",
        color="Status",
        title="Completion Status by Category",
        barmode="stack",
        color_discrete_map={
            "Completed": "#2196F3",  # Blue
            "Remaining": "#BBDEFB"  # Very Light Blue
        }
    )
    fig.update_layout(legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

# Add separator
st.markdown("---")

# Next tricks to learn
st.subheader("Recommended Next Tricks to Learn")

# Strategy: Find tricks that are slightly harder than the hardest completed trick
if completed_list:
    # Get the difficulty of the hardest completed trick
    completed_tricks_df = df[df['Trick'].isin(completed_list)]
    if not completed_tricks_df.empty:
        max_completed_difficulty = completed_tricks_df['Difficulty'].max()

        # Find tricks that are 5-15 points harder than the hardest completed trick
        next_tricks = df[
            (df['Difficulty'] > max_completed_difficulty) &
            (df['Difficulty'] <= max_completed_difficulty + 15) &
            (~df['Trick'].isin(completed_list))
            ].sort_values('Difficulty')

        if not next_tricks.empty:
            st.write("Based on your current skill level, these tricks would be good to learn next:")
            st.dataframe(
                next_tricks[['Trick', 'Difficulty', 'Category']],
                column_config={
                    "Trick": "Trick Name",
                    "Difficulty": st.column_config.ProgressColumn(
                        "Difficulty",
                        format="%d / 100",
                        min_value=0,
                        max_value=100,
                    ),
                    "Category": "Difficulty Level"
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No suitable next tricks found. You may have completed all tricks in the next difficulty range!")
    else:
        st.info("No completed tricks found. Start with some beginner tricks!")
else:
    # If no tricks completed, recommend beginner tricks
    beginner_tricks = df[df['Category'] == 'Beginner'].sort_values('Difficulty')
    st.write("You haven't marked any tricks as learned yet. Here are some beginner tricks to start with:")
    st.dataframe(
        beginner_tricks[['Trick', 'Difficulty', 'Category']],
        column_config={
            "Trick": "Trick Name",
            "Difficulty": st.column_config.ProgressColumn(
                "Difficulty",
                format="{} / 100",
                min_value=0,
                max_value=100,
            ),
            "Category": "Difficulty Level"
        },
        hide_index=True,
        use_container_width=True
    )

# Top 10 hardest tricks table
st.subheader("Top 10 Hardest Tricks")

hardest_tricks = df.sort_values('Difficulty', ascending=False).head(10)
hardest_tricks['Status'] = hardest_tricks['Trick'].apply(
    lambda x: "✅ Learned" if x in completed_list else "❌ Not Yet")

# Display as a table
st.dataframe(
    hardest_tricks[['Trick', 'Difficulty', 'Category', 'Status']],
    column_config={
        "Trick": "Trick Name",
        "Difficulty": st.column_config.ProgressColumn(
            "Difficulty",
            format="%d / 100",
            min_value=0,
            max_value=100,
        ),
        "Category": "Difficulty Level",
        "Status": "Your Status"
    },
    hide_index=True,
    use_container_width=True
)
