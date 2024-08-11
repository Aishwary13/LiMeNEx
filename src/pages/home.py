import dash
import dash_bootstrap_components as dbc
from dash import html, dcc

external_js_lib = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                     external_scripts=[external_js_lib], title="LiMeNex")

layout = html.Div([
    # Welcome Section (Hero Section)
    html.Div([
        html.H1("Welcome to LiMeNEx: Your Gateway to Lipidomics Research",
                style={'color': '#FFFFFF', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.P("Explore the intricate network of lipid metabolic pathways and gain insights into gene regulation with advanced differential expression analysis.",
               style={'color': '#FFFFFF', 'textAlign': 'center', 'maxWidth': '800px', 'margin': '0 auto'}),
        html.A("Get Started", href="#features",
               style={'display': 'inline-block', 'padding': '10px 20px', 'backgroundColor': '#4CAF50', 
                      'color': '#FFFFFF', 'textDecoration': 'none', 'borderRadius': '5px', 
                      'marginTop': '20px', 'textAlign': 'center'})
    ], style={'padding': '50px', 'textAlign': 'center'}),

    # 3D Network Animation Section
    html.Div([
        html.H2("Visualize the Lipid Metabolic Pathways", style={'color': '#FFFFFF', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Div(id='network-animation', style={'height': '500px', 'backgroundColor': '#2C2C2C'}),
        html.P("Explore the interconnected pathways that drive lipid metabolism. Watch as nodes change color to indicate differential expression.",
               style={'color': '#CCCCCC', 'textAlign': 'center', 'marginTop': '20px'})
    ], style={'backgroundColor': '#292929', 'padding': '50px 20px'}),

    # Functionalities Section
    html.Div([
        html.H2("Key Features & Functionalities", style={'color': '#FFFFFF', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Ul([
            html.Li("1. Differential Expression Analysis: Identify upregulated and downregulated genes with precision.", style={'color': '#CCCCCC'}),
            html.Li("2. Custom Data Input: Upload your data and see real-time results on the network.", style={'color': '#CCCCCC'}),
            html.Li("3. Interactive Visualization: Interact with the network and explore gene relationships visually.", style={'color': '#CCCCCC'}),
        ], style={'listStyleType': 'none', 'paddingLeft': '0', 'textAlign': 'left', 'maxWidth': '800px', 'margin': '0 auto', 'textAlign': 'center'})
    ], style={'backgroundColor': '#1A1A1A', 'padding': '50px 20px'}),

    # Step-by-Step Guide Section
    html.Div([
        html.H2("How to Use LiMeNEx", style={'color': '#FFFFFF', 'fontWeight': 'bold', 'textAlign': 'center'}),
        html.Div([
            html.Div([
                html.H3("Step 1", style={'color': '#4CAF50', 'textAlign': 'center'}),
                html.P("Upload your gene expression data.", style={'color': '#CCCCCC', 'textAlign': 'center'})
            ], style={'padding': '20px', 'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                html.H3("Step 2", style={'color': '#4CAF50', 'textAlign': 'center'}),
                html.P("Run differential expression analysis.", style={'color': '#CCCCCC', 'textAlign': 'center'})
            ], style={'padding': '20px', 'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),

            html.Div([
                html.H3("Step 3", style={'color': '#4CAF50', 'textAlign': 'center'}),
                html.P("Visualize the upregulated and downregulated genes on the network.", style={'color': '#CCCCCC', 'textAlign': 'center'})
            ], style={'padding': '20px', 'width': '30%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'textAlign': 'center'})
    ], style={'backgroundColor': '#2D2D2D', 'padding': '50px 20px'}),
], style={'backgroundColor': '#1A1A1A', 'height': '100vh'})
