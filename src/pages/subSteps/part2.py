from dash import callback, dcc, html
from dash.dependencies import Input, Output, State


layout = html.Div(id = 'part1',
    children=[
        html.A('Part 2',style={'color' : 'white'})
    ]
)