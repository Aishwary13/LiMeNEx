from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
import smtplib
from email.message import EmailMessage

# dash.register_page(__name__, path='/contact')

@callback(
    Output("email-status", "children"),
    Input("send-email", "n_clicks"),
    State("userName", "value"),
    State("userEmail", "value"),
    State("userPhone", "value"),
    State("userMessage", "value"),
    prevent_initial_call=True
)
def send_email(n_clicks, name, email, phone, message):
    if not name or not email or not phone or not message:
        return dbc.Alert("Please fill in all fields.", color="danger")

    try:
        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # start TLS for security
        s.starttls()
        # Authentication
        s.login("aishwary20490@iiitd.ac.in", "krsysetwvvgrooid")
        # message to be sent
        email_message = EmailMessage()
        email_message['From'] = "aishwary20490@iiitd.ac.in"
        email_message['To'] = email
        email_message['Subject'] = "Contact Form Submission"
        email_message.set_content(f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}")
        # sending the mail
        s.send_message(email_message)
        # terminating the session
        s.quit()
        return dbc.Alert("Email sent successfully.", color="success")
    except Exception as e:
        return dbc.Alert(f"Failed to send email. Error: {e}", color="danger")

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
                html.Div( className = 'formDiv',children=[
                    html.H3('Contact us', className='title'),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(id = 'userName',type='text', name='name', className='input', placeholder='Name')
                    ]),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(id='userEmail',type='email', name='email', className='input', placeholder='Email')
                    ]),
                    html.Div(className='social-input-containers', children=[
                        dcc.Input(id = 'userPhone', type='tel', name='phone', className='input', placeholder='Phone')
                    ]),
                    html.Div(className='social-input-containers textarea', children=[
                        dcc.Textarea(id = 'userMessage', name='message', className='input', placeholder='Message')
                    ]),
                    html.Button('Send', className='btn', id="send-email"),
                    html.Div(id="email-status",style={"margin-top":"5px"})
                ]),
            ])
        ])
    ])
], style={'background-color':'#1a1a1a'})
