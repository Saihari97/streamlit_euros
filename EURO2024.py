import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
#from statsbombpy import sb
from mplsoccer import VerticalPitch,Pitch
#from highlight_text import ax_text, fig_text
#from mplcursors import cursor
#import mplcursors
import matplotlib.lines as mlines

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

### Reading Input Files:
####### Team Level Goals vs xG
team_df = pd.read_excel(os.path.join(script_dir, 'Team Level Stats.xlsx'))

####### Player Level Stats: Goals, Assists
player_df = pd.read_excel(os.path.join(script_dir, 'Player Level Stats.xlsx'))

######## Shot Map
shot_map_team = pd.read_excel(os.path.join(script_dir, "Shot Map.xlsx"))

### Streamlit 
# ---- Streamlit UI ----
st.set_page_config(layout="wide")

## Title and Sub Title
st.markdown("<h1 style='text-align: center;'>EURO 2024</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size:18px; color:gray;'>Select a team to view top scorers,assists, Shots and Goal Maps</p>", unsafe_allow_html=True)

# ---- Dropdown Selection ----
teams = team_df['team'].unique().tolist()
# Default value (initial value) for the dropdown
default_value = 'All Teams'
teams.append(default_value)
selected_team = st.selectbox("Select a team:", teams,index=teams.index(default_value))

# # ---- Filter Data based on selected value----
# team_stats = team_df[team_df['team'] == selected_team]
# player_stats = player_df[player_df['team'] == selected_team]
# player_stats = player_stats[player_stats['Attacking Threat']>0]

# Create a 2x2 layout
col1, col2 = st.columns(2)  # First row
col3, col4 = st.columns(2)  # Second row

# ---- Team Performance infront Goal (1,1)
with col1:
    st.subheader("Goals vs xG")
    
    # Define colors for Performance categories
    color_map = {"Under-Performed": "#F44336", "Out-Performed xG": "#4CAF50"}
    team_df.sort_values(by=['Performance','Goal'],ascending=[False,True],inplace=True)

    # Create bar chart
    fig_team = px.bar(
        team_df, 
        x='Goal', 
        y='team', 
        title='Goals vs Expected Goals (xG)', 
        orientation='h', 
        color='Performance', 
        color_discrete_map=color_map, 
        text='Goal',
        labels={"Goal": "Goals Scored", "team": "Team"},
        hover_data={"Goal": True, "Expected Goals": True,'Performance':True}
    )
    fig_team.update_traces(hovertemplate='Team: %{y}<br>Goals: %{x}<br>xG: %{customdata[0]}<br>Performance: %{customdata[1]}<extra></extra>',\
        textangle=0, textfont=dict(size=14, color='white', family='Arial'),texttemplate = '<b>%{text}</b>')

    # Customize plot size and y-axis label font size
    fig_team.update_layout(
        width=900,  # Increase plot width
        height=700,  # Increase plot height
        yaxis=dict(
            title_font=dict(size=9),  # Increase y-axis label font size
            tickfont=dict(size=8.5)  # Increase y-axis tick labels size
        ),
        xaxis=dict(
            title_font=dict(size=12),  # Increase x-axis label font size
            showticklabels=False
        )
    )
    st.plotly_chart(fig_team)

# ---- Bar Chart for Top Goal Scorers & Assisters ---- (1,2)
with col2:
    st.subheader("Attacking Threat")
    
    # Define colors for the bars
    colors = {'Goal': '#FFD700', '#Assists': '#00FFFF'}
    if selected_team == 'All Teams':
        player_stats = player_df
        player_stats = player_stats[player_stats['Attacking Threat']>0]
    else:
        player_stats = player_df[player_df['team'] == selected_team]
        player_stats = player_stats[player_stats['Attacking Threat']>0]
    
    player_stats.sort_values(by='Attacking Threat',ascending=True,inplace=True)
    player_stats = player_stats.tail(15)
    # Create the bar chart
    fig_bar = go.Figure()

    # Add Goals bar
    fig_bar.add_trace(go.Bar(
        y=player_stats['player'],
        x=player_stats['Goal'],
        name='Goals',
        orientation='h',
        marker=dict(color=colors['Goal']),
        hovertemplate='Player: %{y}<br>Goals: %{x}<extra></extra>',
        text=player_stats['Goal'],
        textposition='inside',
        insidetextfont=dict(color='#006400',size=14),
        textangle=0,
        texttemplate = '<b>%{text}</b>'
    ))

    # Add Assists bar
    fig_bar.add_trace(go.Bar(
        y=player_stats['player'],
        x=player_stats['#Assists'],
        name='Assists',
        orientation='h',
        marker=dict(color=colors['#Assists']),
        hovertemplate='Player: %{y}<br>Assists: %{x}<extra></extra>',
        text=player_stats['#Assists'],
        textposition='inside',
        insidetextfont=dict(color='black',size=14),
        textangle=0,
        texttemplate = '<b>%{text}</b>'
    ))

    # Update layout
    fig_bar.update_layout(
        title=f"Top Goal Scorers & Assists for {selected_team}",
        barmode='stack',
        xaxis_title='Attacking Threat',
        yaxis_title='Player',
        xaxis = dict(showticklabels=False)
    )

    ##Update Legend title
    fig_bar.update_layout(legend_title_text="Attacking Type")
    st.plotly_chart(fig_bar, use_container_width=True)  


# ---- Shot Map - On Target vs Off-Target ---- (2,1)
with col3:

    st.subheader(f"{selected_team} Shot Map: On-Target vs Off-Target")

    pitch = VerticalPitch(pitch_type='statsbomb',line_color='white',half=True,pitch_color='#000000',linewidth=1,goal_type='box')
    fig_shot,ax = plt.subplots(1,1,figsize=(16,12),sharey=True)

    if selected_team == 'All Teams':
        shot_df = shot_map_team.copy()
    else:
        shot_df = shot_map_team[(shot_map_team.team == selected_team)].copy()
    
    sont = shot_df[shot_df['Shot_target_type']=='On-target'].shape[0]
    soft = shot_df[shot_df['Shot_target_type']=='Off-target'].shape[0]
    
    # Define a color map for the shot types
    shot_color_map = {'On-target': '#2ECC71', 'Off-target': '#E74C3C'}  # Example colors for two types
    # Map colors to the shot_df based on 'Shot_type'
    shot_colors = shot_df['Shot_target_type'].map(shot_color_map)


    # Draw the pitch for the team
    pitch.draw(ax=ax)

    # Plot Goal Shots
    pitch.scatter(
        shot_df["shot_x"], 
        shot_df["shot_y"], 
        s=shot_df["shot_statsbomb_xg"] * 1000 + 100, #Scaling Factor
        marker="o", 
        c=shot_colors ,
        ax=ax, 
        alpha=0.7, 
        # edgecolors='red', 
        linewidth=1, 
        label="Shots"
    )
    
    ax.text(
        54, 80,  # Coordinates (x, y)
        "Shots on-Target",  # Text
        color="white",  # Text color
        fontsize=15,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        54, 76,  # Coordinates (x, y)
        f"{sont}",  # Text
        color="white",  # Text color
        fontsize=15,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        70, 80,  # Coordinates (x, y)
        "Shots off-Target",  # Text
        color="white",  # Text color
        fontsize=15,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        70, 76,  # Coordinates (x, y)
        f"{soft}",  # Text
        color="white",  # Text color
        fontsize=15,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )
    

# Create legend handles with circles using plt.Line2D
    legend_handles = [\
    mlines.Line2D([], [], color='#2ECC71', marker='o', linestyle='None', markersize=15, label='On-target'),
    mlines.Line2D([], [], color='#E74C3C', marker='o', linestyle='None', markersize=15, label='Off-target')]
    # Add legend to the plot
    ax.legend(
        handles=legend_handles,
        title='On vs Off Target Shots', 
        labelspacing=1, 
        loc="upper center", 
        ncol=6, 
        frameon=True, 
        fancybox=False, 
        shadow=False, 
        bbox_to_anchor=(0.77, 0.15),
        fontsize=14,
        title_fontsize=18
    )

    st.pyplot(fig_shot)

# ---- Goal Map ---- (2,2)
with col4:
    st.subheader(f"{selected_team} Goal Map")
    # Draw the pitch and setup the plot
    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', linewidth=1, goal_type='box', half=True,pitch_color='#000000')
    fig, ax = plt.subplots(1, 1, figsize=(16,12), sharey=True)
    
    if selected_team == 'All Teams':
        events_shot_df_goal = shot_map_team[(shot_map_team.shot_outcome == 'Goal')].copy()
        events_shot_df_ngoal = shot_map_team[(shot_map_team.shot_outcome != 'Goal')].copy()

        # Calculate total xG and goals for the team
        total_xg = round(shot_map_team['shot_statsbomb_xg'].sum(),2)
        pen_goals = events_shot_df_goal[events_shot_df_goal['goal_type']=='Penalty'].shape[0]
        non_pen_goals = events_shot_df_goal[events_shot_df_goal['goal_type']!='Penalty'].shape[0]
        goals = pen_goals + non_pen_goals
    else:
        events_shot_df_goal = shot_map_team[(shot_map_team.shot_outcome == 'Goal') & (shot_map_team.team == selected_team)]
        events_shot_df_ngoal = shot_map_team[(shot_map_team.shot_outcome != 'Goal') & (shot_map_team.team == selected_team)]

        # Calculate total xG and goals for the team
        total_xg = round(shot_map_team[(shot_map_team.team == selected_team)]['shot_statsbomb_xg'].sum(),2)
        pen_goals = events_shot_df_goal[events_shot_df_goal['goal_type']=='Penalty'].shape[0]
        non_pen_goals = events_shot_df_goal[events_shot_df_goal['goal_type']!='Penalty'].shape[0]
        goals = pen_goals + non_pen_goals
        
    # Define a color map for the Goal types
    goal_color_map = {'Non-Penalty': '#2ECC71', 'Penalty': '#FFFF00'}  ## Green for non-penalty ; Lime for Penalty

    # Map colors to the shot_df based on 'Goal_type'
    goals_colors = events_shot_df_goal['goal_type'].map(goal_color_map)

    # Draw the pitch for the team
    pitch.draw(ax=ax)

    # Plot Goal Shots
    pitch.scatter(
        events_shot_df_goal["shot_x"], 
        events_shot_df_goal["shot_y"], 
        s=events_shot_df_goal["shot_statsbomb_xg"] * 1000 + 100, #Scaling Factor
        marker="o", 
        c=goals_colors, 
        ax=ax, 
        alpha=0.7, 
        # edgecolors='red', 
        linewidth=1, 
        label="Goals"
    )
    # Add a box with text for goals and xG
    # Titles
    ax.text(
        54, 80,  # Coordinates (x, y)
        f"Goals: {goals}",  # Text
        color="white",  # Text color
        fontsize=25,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        70, 80,  # Coordinates (x, y)
        "xG",  # Text
        color="white",  # Text color
        fontsize=25,  # Font size
        ha="right",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    if goals >= total_xg:
        text_color = ["#2ECC71","white"]
    else:
        text_color = ["#F44336","white"]

    # Values
            # Values
    ax.text(
        40, 76,  # Coordinates (x, y)
        f"Non-Penalty Goals: {non_pen_goals}",  # Text
        color=text_color[0],  # Text color (Green)
        fontsize=16,  # Font size
        ha="left",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        40, 73,  # Coordinates (x, y)
        f"Penalty Goals: {pen_goals}",  # Text
        color=text_color[0],  # Text color (Green)
        fontsize=16,  # Font size
        ha="left",  # Horizontal alignment
        va="center"  # Vertical alignment
    )

    ax.text(
        67, 74,  # Coordinates (x, y)
        f"{total_xg}",  # Text
        color=text_color[1],  # Text color (Green)
        fontsize=24,  # Font size
        ha="left",  # Horizontal alignment
        va="center"  # Vertical alignment
    )
    
    # Create legend handles with circles using plt.Line2D
    legend_handles = [\
    mlines.Line2D([], [], color='#2ECC71', marker='o', linestyle='None', markersize=15, label='Non-Penalty Goal'),
    mlines.Line2D([], [], color='#FFFF00', marker='o', linestyle='None', markersize=15, label='Penalty Goal')]
    # Add legend to the plot
    ax.legend(
        handles=legend_handles,
        title='Type of Goal', 
        labelspacing=1, 
        loc="upper center", 
        ncol=6, 
        frameon=True, 
        fancybox=False, 
        shadow=False, 
        bbox_to_anchor=(0.77, 0.15),
        fontsize=14,
        title_fontsize=18
    )
    st.pyplot(fig)
