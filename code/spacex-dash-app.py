# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex_df data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Div(dcc.Dropdown(id='site-dropdown',
                                                        options=[
                                                            {'label': 'All Sites', 'value': 'ALL'},
                                                            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
                                                        ],
                                                        value='ALL',
                                                        placeholder='Select a Launch Site here',
                                                        searchable=True
                                )),
                                html.Br(),

                                # Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=int(min_payload),
                                                max=int(max_payload),
                                                step=100,
                                                value=[int(min_payload), int(max_payload)],
                                                marks={
                                                    int(min_payload): str(int(min_payload)),
                                                    int(max_payload): str(int(max_payload))
                                                }),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                                ])

# Pie Chart:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    # If ALL sites selected, show total successful launches by site
    if entered_site == 'ALL':
        fig_df = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(fig_df, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
        return fig
    else:
        # For a specific site, show success vs failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcomes = filtered_df.groupby('class').size().reset_index(name='count')
        # map class values to readable labels if present as 0/1
        outcomes['class'] = outcomes['class'].map({1: 'Success', 0: 'Failure'}).fillna(outcomes['class'])
        fig = px.pie(outcomes, values='count', names='class',
                     title=f"Total Launch Outcomes for site {entered_site}")
        return fig

# Payload Slider:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    # create scatter plot: payload vs outcome, colored by booster version category if available
    color_col = 'Booster Version Category' if 'Booster Version Category' in spacex_df.columns else None
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color=color_col,
                     title='Payload vs. Launch Outcome',
                     hover_data=['Launch Site'])
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)