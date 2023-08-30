import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load SpaceX launch data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Initialize the Dash app
app = dash.Dash(__name__)

# Task 1: Create Launch Site Dropdown
launch_sites = spacex_df["Launch Site"].unique()
launch_site_options = [{"label": site, "value": site} for site in launch_sites]

launch_site_dropdown = dcc.Dropdown(
    id="site-dropdown",
    options=[{"label": "All Sites", "value": "ALL"}] + launch_site_options,
    value="ALL",
    placeholder="Select a Launch Site",
    searchable=True,
)

# Task 2: Callback to render success-pie-chart based on selected site dropdown
@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def render_pie_chart(selected_site):
    if selected_site == "ALL":
        # Group data by Launch Site and class (success/failure), then unstack for the pie chart
        pie_df = spacex_df.groupby(["Launch Site", "class"]).size().unstack(fill_value=0)
        pie_df["Total"] = pie_df.sum(axis=1)  # Calculate total launches per site
        
        colors = px.colors.qualitative.Plotly[:2]
        title = "Total Success Launches by Site"
        
        pie_fig = px.pie(
            pie_df, 
            names=pie_df.index,
            values="Total",  # Use the "Total" column for values
            title=title,
            color_discrete_sequence=colors
        )
        
        pie_fig.update_traces(textinfo="percent+label", pull=[0.2, 0.2, 0.2, 0.2])  # Customize labels and pulling slices
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == selected_site]
        fig = px.pie(
            filtered_df,
            names="class",
            title=f"Success Launches - {selected_site}",
        )
        fig.update_traces(textinfo="percent+label")
    return pie_fig if selected_site == "ALL" else fig

# Task 3: Create Payload Range Slider
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

payload_slider = dcc.RangeSlider(
    id="payload-slider",
    min=min_payload,
    max=max_payload,
    step=1000,
    marks={min_payload: str(min_payload), max_payload: str(max_payload)},
    value=[min_payload, max_payload],
)

# Task 4: Callback to render success-payload-scatter-chart scatter plot
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [
        Input("site-dropdown", "value"),
        Input("payload-slider", "value"),
    ]
)
def render_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df
    
    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == selected_site]
        
    filtered_df = filtered_df[
        (filtered_df["Payload Mass (kg)"] >= payload_range[0])
        & (filtered_df["Payload Mass (kg)"] <= payload_range[1])
    ]

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",  
        color="Booster Version Category",
        title="Payload vs. Launch Outcome",
    )
    return fig

# Layout of the app
app.layout = html.Div([
    html.H1("SpaceX Launch Data Dashboard"),
    
    # Launch Site Dropdown
    launch_site_dropdown,
    
    # Success Pie Chart
    dcc.Graph(id="success-pie-chart"),
    
    # Payload Range Slider
    payload_slider,
    
    # Success Payload Scatter Chart
    dcc.Graph(id="success-payload-scatter-chart"),
])

if __name__ == "__main__":
    app.run_server(debug=True)