from dash import callback, dcc, html
from dash.dependencies import Input, Output, State

from pages.subSteps import part1,part2,part3,part4

# Custom CSS for the progress bar
layout = html.Div([
    html.Div([
        # Progress Bar
        html.Div([
            html.Div(className='step completed', id='step-1', children='1'),
            html.Div(className='arrow', id='arrow-1', children=''),
            html.Div(className='step', id='step-2', children='2'),
            html.Div(className='arrow', id='arrow-2', children=''),
            html.Div(className='step', id='step-3', children='3'),
            html.Div(className='arrow', id='arrow-3', children=''),
            html.Div(className='step', id='step-4', children='4'),
        ], className='progress-bar'),

        # Content
        html.Div(id='content', style={'marginTop': '30px'}),

        # Buttons
        html.Div([
            html.Button('Prev', id='prev-button', n_clicks=0, className='btn'),
            html.Button('Next', id='next-button', n_clicks=0, className='btn'),
        ], style={'marginTop': '50px', 'textAlign': 'center'})
    ], className='form-container')
])

# Callbacks to update progress bar and arrows
@callback(
    [Output(f'step-{i}', 'className') for i in range(1, 5)] +
    [Output(f'arrow-{i}', 'className') for i in range(1, 4)] +
    [Output('next-button','disabled')] +
    [Output('prev-button','disabled')] +
    [Output('content', 'children')],
    [Input('next-button', 'n_clicks'),
     Input('prev-button', 'n_clicks')],
    [State(f'step-{i}', 'className') for i in range(1, 5)] +
    [State(f'arrow-{i}', 'className') for i in range(1, 4)]
)
def update_progress_bar(next_clicks, prev_clicks, *classes):
    step_index = next_clicks - prev_clicks
    # print(step_index)
    step_classes = []
    arrow_classes = []

    # Update step classes
    for i in range(4):
        if i < step_index:
            step_classes.append('step completed')
        elif i == step_index:
            step_classes.append('step active')
        else:
            step_classes.append('step')

    # Update arrow classes
    for i in range(3):
        if i < step_index:
            arrow_classes.append('arrow arrowCompleted')
        else:
            arrow_classes.append('arrow')
    
    btnDisabled = [False,False]
    if(step_index == 0):
        btnDisabled = [False,True]
    elif step_index == 4:
        btnDisabled = [True,False]
    
    if step_index == 0:
        content = part1.layout  # Use part1 from subSteps
    elif step_index == 1:
        content = part2.layout  # Use part2 from subSteps
    elif step_index == 2:
        content = part3.layout  # Use part3 from subSteps
    else:
        content = part4.layout  # Use part4 from subSteps

    return step_classes + arrow_classes + btnDisabled + [content]

