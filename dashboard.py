import json
import os
import sqlite3
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import threading
import time

app = Dash(__name__)
app.title = "Real-Time Cleaning Metrics Dashboard"

app.layout = html.Div([
    html.H2("Real-Time Cleaning Metrics Dashboard"),
    dcc.Interval(id='interval', interval=1000, n_intervals=0),

    html.Div(id='metrics'),
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='bar-plant'),
    dcc.Graph(id='bar-building'),
    dcc.Graph(id='bar-machine'),
])

@app.callback(
    [Output('metrics', 'children'),
     Output('line-chart', 'figure'),
     Output('bar-plant', 'figure'),
     Output('bar-building', 'figure'),
     Output('bar-machine', 'figure')],
    [Input('interval', 'n_intervals')]
)
def update_dashboard(n):
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    num_plants = df['plant_id'].nunique()
    num_buildings = df['building_id'].nunique()
    num_machines = df['machine_id'].nunique()
    num_txns = len(df)
    avg_dli = df['dli'].mean()
    avg_sri = df['sri'].mean()
    avg_odi = df['odi'].mean()
    metrics = html.Div([
        html.P(f"Number of Plants: {num_plants}"),
        html.P(f"Number of Buildings: {num_buildings}"),
        html.P(f"Number of Machines: {num_machines}"),
        html.P(f"Number of Transactions: {num_txns}"),
        html.P(f"Average DLI: {avg_dli:.2f}, SRI: {avg_sri:.2f}, ODI: {avg_odi:.2f}"),
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    fig_line = px.line(df.sort_values('timestamp'), x='timestamp', y=['dli', 'sri', 'odi'], title="Cleaning Metrics Over Time")
    fig_plant = px.bar(df, x='plant_id', y='dli', title='DLI per Plant', barmode='group')
    fig_building = px.bar(df, x='building_id', y='sri', title='SRI per Building', barmode='group')
    fig_machine = px.bar(df, x='machine_id', y='odi', title='ODI per Machine', barmode='group')
    return metrics, fig_line, fig_plant, fig_building, fig_machine

if __name__ == '__main__':
    # NOTE: environment variables must be sourced in advance
    SQLITE_DB_NAME = os.environ["SQLITE_DB_NAME"]
    # Create connection
    conn = sqlite3.connect(SQLITE_DB_NAME, check_same_thread=False)
    app.run(debug=True)
