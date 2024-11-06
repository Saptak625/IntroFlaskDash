import pandas as pd
from dash import dcc, html, Input, Output, Dash

from plotly.graph_objs import Figure, Bar

import plotly.express as px

url = 'https://api.covidtracking.com/v1/states/current.csv'
data = pd.read_csv(url)

app = Dash(__name__)

app.layout = html.Div([
    dcc.Markdown("# Covid-19 Data Visualization"),
    dcc.Markdown("## Tracking Metrics and Trends Across States for Late 2020 and Early 2021"),

    dcc.Tabs([
        dcc.Tab(label='Overview', children=[
            html.Div([
                dcc.Graph(id='cases-bar-chart'),
                dcc.Graph(id='deaths-scatter-plot')
            ])
        ]),
        dcc.Tab(label='State Information', children=[
            html.Div([
                dcc.Markdown("## Select State for Detailed Information"),
                dcc.Dropdown(id='state-dropdown', options=[{'label': state, 'value': state} for state in data['state'].unique()],
                    value='GA',
                    clearable=False,
                    placeholder='Select a state'
                ),
                dcc.Graph(id='hospitalized-chart'),
                dcc.Graph(id='death-rate-chart')
            ])
        ])
    ])
])

@app.callback(
    Output('cases-bar-chart', 'figure'),
    Input('state-dropdown', 'value')
)
def update_cases_bar_chart(selected_state):
    cases_data = data.groupby('state')['positive'].sum().reset_index()

    fig = px.bar(cases_data, x='state', y='positive', title='Total Positive Cases by State')
    fig.update_layout(xaxis_title='State', yaxis_title='Total Positive Cases')
    return fig

@app.callback(
    Output('deaths-scatter-plot', 'figure'),
    Input('state-dropdown', 'value')
)
def update_deaths_scatter_plot(selected_state):
    fig = px.scatter(data, x='totalTestResults', y='death', color='state', hover_name="state", title='Total Deaths vs. Total Cases')
    fig.update_layout(xaxis_title='Total Cases', yaxis_title='Total Deaths')
    return fig

@app.callback(
    Output('hospitalized-chart', 'figure'),
    Input('state-dropdown', 'value')
)
def update_hospitalized_chart(selected_state):
    selected_state_data = data[data['state'] == selected_state]
    fig = Figure(data=[
        Bar(name='Currently Hospitalized', x=['Hospitalized'], y=[selected_state_data['hospitalizedCurrently'].values[0]]),
        Bar(name='Hospitalized Cumulative', x=['Hospitalized Cumulative'], y=[selected_state_data['hospitalizedCumulative'].values[0]])
    ])
    fig.update_layout(barmode='group', title=f'Current vs Cumulative Hospitalizations in {selected_state}')
    return fig

@app.callback(
    Output('death-rate-chart', 'figure'),
    Input('state-dropdown', 'value')
)
def update_death_rate_chart(selected_state):
    selected_data = data[data['state'] == selected_state]
    death_rate = 100 * selected_data['death'].values[0] / selected_data['positive'].values[0]
    fig = px.bar(x=['Death Rate'], y=[death_rate], title=f'Death Rate in {selected_state}')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)