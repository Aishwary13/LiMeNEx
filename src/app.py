import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

dash_app = Dash(__name__, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP], title="LiMeNex", use_pages=True)
dash_app.config.suppress_callback_exceptions = True
dash_app.server.secret_key = 'supersecretkey'

dash_app.layout = html.Div([
    html.H1('Multi-page app with Dash Pages'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == '__main__':
    dash_app.run(debug=True)