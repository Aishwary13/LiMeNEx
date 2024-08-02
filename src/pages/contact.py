import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# dash.register_page(__name__, path='/contact')

layout = html.Div([
    html.Div(className='container',children=[
        html.Div(className='form', children=[
            html.Div(className='contact-info', children=[
                html.H3("Let's get in touch", className='title'),
                html.P("Contact us with the following details, and fill up the form with the details.", className='text'),
                html.Div(className='info', children=[
                    html.Div(className='social-information', children=[
                        html.I(className='fa fa-map-marker'),
                        html.P('Ray Lab, Indraprastha Institute of Information Technology, Delhi, India')
                    ]),
                    html.Div(className='social-information', children=[
                        html.I(className='fa-solid fa-envelope'),
                        html.P('arjun@iiitd.ac.in')
                    ])
                ])
            ]),
            html.Div(className='contact-info-form', children=[
                html.Span(className='circle one'),
                html.Span(className='circle two'),
                html.Form(action='#', children=[
                    html.H3('Contact us', className='title'),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(type='text', name='name', className='input', placeholder='Name')
                    ]),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(type='email', name='email', className='input', placeholder='Email')
                    ]),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(type='tel', name='phone', className='input', placeholder='Phone')
                    ]),
                    html.Div(className='social-input-containers textarea', children=[
                        dcc.Textarea(name='message', className='input', placeholder='Message')
                    ]),
                    html.Button('Send', type='submit', className='btn')
                ])
            ])
        ])
    ])
], style={'background-color':'#1a1a1a','height':'100vh'})
