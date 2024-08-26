import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

font_awesome1 = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/all.min.css'
font_awesome3 = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.1/css/solid.min.css'

external_js_lib="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

dash_app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP,font_awesome1,font_awesome3],
                    title="LiMeNex" ,use_pages=True,suppress_callback_exceptions=True,
                    external_scripts=[external_js_lib])

from pages import home,visualisation, contact,Analysis

link_style = {
    'padding': '0.75em 1em',
    'text-decoration': 'none',
    'color': 'white',
    'display': 'block'
}

dash_app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div([
        # html.Div(
        #     dcc.Link(f"{page['name']}", href=page["relative_path"], style=link_style)
        # ) for page in dash.page_registry.values()
        html.Div([
                html.Div([
                    html.Img(src="assets/network_pic.png", style={"width": "4rem"}),
                    html.Img(src="assets/Title.png", style={"width": "10rem"})
                    # html.H5("LiMeNEx", style={'color': 'white', 'marginTop': '20px'}),
                    # html.Img(src="assets/Title.png", style={"width": "4.5rem"})
                ], className='image_title')
            ], className="sidebar-header"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink([html.Div([
                    html.I(className="fa-solid fa-house"),
                    html.Span("Home", style={'marginTop': '0px', 'marginLeft' :'6px'})], className='icon_title')],
                    href="/",
                    active="exact",
                    className="pe-3",
                ),
                dbc.NavLink([html.Div([
                    html.I(className="fa-solid fa-circle-nodes"),
                    html.Span("Network", style={'marginTop': '0px', 'marginLeft' :'6px'})], className='icon_title')],
                    href="/Network",
                    active="exact",
                    className="pe-3",
                    style={'marginTop' : '8px'}
                ),
                dbc.NavLink([html.Div([
                    html.I(className="fa-solid fa-magnifying-glass-chart"),
                    html.Span("D.E. Analysis", style={'marginTop': '0px', 'marginLeft' :'6px'})], className='icon_title')],
                    href="/DiffAnalysis",
                    active="exact",
                    className="pe-3",
                    style={'marginTop' : '8px'}
                ),
                dbc.NavLink([html.Div([
                    html.I(className="fa-solid fa-address-card"),
                    html.Span("Contact Us", style={'marginTop': '0px', 'marginLeft' :'6px'})], className='icon_title')],
                    href="/Contact",
                    active="exact",
                    className="pe-3",
                    style={'marginTop' : '8px'}
                )
            ],
            vertical=True,
            pills=True,
        )

    ], className='sidebar'),

    html.Div(
        # dash.page_container,
        id='page-content',
        children=[]
    )
])

@dash_app.callback(
        Output('page-content', 'children'),
        Input('url', 'pathname'),
    )
def display_page(pathname):
    if pathname == '/':
        return home.layout
    elif pathname == '/Network':
        return visualisation.layout
    elif pathname == '/Contact':
        return contact.layout
    elif pathname == '/DiffAnalysis':
        return Analysis.layout


if __name__ == '__main__':
    dash_app.run_server(debug=True)
