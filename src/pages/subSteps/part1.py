from dash import callback, dcc, html,ctx
from dash.dependencies import Input, Output, State
import io
import pandas as pd
import base64
import os
import scanpy as sc
import anndata
import numpy
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



layout = html.Div(id='part1-container', children=[

    # Title
    html.H3('1. Upload Data', style={'color': '#FFFFFF'}),
    
    # Upload components for Count Matrix and Metadata
    html.Div([
        html.Label('Upload Count Matrix CSV:', style={'color': '#FFFFFF'}),
        dcc.Upload(
            id='upload-count-matrix',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a CSV File', style={'color': '#FF6600'})
            ]),
            style={
                'width': '90%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'color': '#FFFFFF',
                'backgroundColor': '#333333'
            },
            multiple=False
        ),
        html.Div(id = 'upload-count-matrix-confirmation',children=[]),

        html.Label('Upload Metadata CSV:', style={'color': '#FFFFFF'}),
        dcc.Upload(
            id='upload-metadata',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a CSV File', style={'color': '#FF6600'})
            ]),
            style={
                'width': '90%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px',
                'color': '#FFFFFF',
                'backgroundColor': '#333333'
            },
            multiple=False
        ),
        html.Div(id = 'upload-metadata-confirmation', children=[])
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

########################################################################################################
    # Placeholder for plot
    html.H3('2. Quality Control', style={'color': '#FFFFFF'}),
    html.Button('Run Quality Control', id='run-quality-control', n_clicks=0, className='btn'),
    html.Div(id='output-violin-plot', style={'textAlign': 'center', 'marginTop': '30px'}),

    # Add some spacing at the bottom
    html.Div(style={'marginBottom': '50px'})
])

# Callback to handle file uploads and generate the violin plot
@callback(
    Output('upload-count-matrix-confirmation','children'),
    Output('upload-metadata-confirmation', 'children'),
    [Input('upload-count-matrix', 'contents'),
     Input('upload-metadata', 'contents')],
    [State('upload-count-matrix', 'filename'),
     State('upload-metadata', 'filename')],
    [State('upload-count-matrix-confirmation','children'),
     State('upload-metadata-confirmation', 'children')]
)
def save_csv_files(count_matrix_contents, metadata_contents, count_matrix_filename, metadata_filename,count_matrix_conf,metadata_conf):
    # Check which input triggered the callback
    trigger_id = ctx.triggered_id

    # Check if the count matrix was uploaded
    if trigger_id == 'upload-count-matrix' and count_matrix_contents:
        file_path = parse_and_save_csv(count_matrix_contents, count_matrix_filename)
        if file_path:
            return html.Div(f'Count matrix file saved to {file_path}', style={'color': 'green'}),metadata_conf

    # Check if the metadata was uploaded
    elif trigger_id == 'upload-metadata' and metadata_contents:
        file_path = parse_and_save_csv(metadata_contents, metadata_filename)
        if file_path:
            return count_matrix_conf,html.Div(f'Metadata file saved to {file_path}', style={'color': 'green'})

    # In case no file is uploaded yet
    return count_matrix_conf,metadata_conf

SAVE_PATH = "D:/Raylab/LiMeNEx/newPipelineUploadFiles"
def parse_and_save_csv(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode('utf-8-sig')  # Use 'utf-8-sig' to handle BOM

    try:
        # Save the decoded CSV to a specified path
        file_path = os.path.join(SAVE_PATH, filename)
        with open(file_path, 'w', encoding='utf-8') as f:  # Save with 'utf-8' encoding
            f.write(decoded)
        print(f'Successfully saved {filename} at {file_path}')
        return file_path
    except Exception as e:
        print(f'Error while saving {filename}: {e}')
        return None
    
@callback(
    Output('output-violin-plot', 'children'),
    Input('run-quality-control', 'n_clicks')
)
def QualityControl(n_clicks):
    if n_clicks is None or n_clicks <= 0:
        return html.Div()
    
    count_matrix_path = 'D:/Raylab/LiMeNEx/newPipelineUploadFiles/GSE246269_count_matrix.csv'  # Replace with your actual file path
    metadata_path = 'D:/Raylab/LiMeNEx/newPipelineUploadFiles/metadata6 (1).csv'          # Replace with your actual file path

    # Load count matrix
    count_df = pd.read_csv(count_matrix_path, index_col=0)
    # print("Count Matrix Shape:", count_df.shape)
    # print(count_df.head())

    # Load metadata
    metadata_df = pd.read_csv(metadata_path, index_col=0)
    # print("Metadata Shape:", metadata_df.shape)
    # print(metadata_df.head())
    count_samples = set(count_df.columns)
    metadata_samples = set(metadata_df.index)

    # Find overlapping samples
    common_samples = count_samples.intersection(metadata_samples)
    print(f"Number of common samples: {len(common_samples)}")

    # Identify samples present only in count matrix
    only_in_counts = count_samples - metadata_samples
    print(f"Samples only in count matrix: {only_in_counts}")

    # Identify samples present only in metadata
    only_in_metadata = metadata_samples - count_samples
    print(f"Samples only in metadata: {only_in_metadata}")

    # Optionally, subset to common samples
    count_df = count_df.loc[:, list(common_samples)]
    metadata_df = metadata_df.loc[list(common_samples)]

    # Convert to numeric if necessary
    count_df = count_df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Reorder metadata to match count matrix columns
    metadata_df = metadata_df.loc[count_df.columns]

    adata = sc.AnnData(X=count_df.T, obs=metadata_df)
    # Set gene symbols as variable names
    adata.var_names = count_df.index.tolist()
    # Optional: Add gene symbols as a separate column if needed
    adata.var['gene_symbols'] = adata.var_names
    adata.var_names_make_unique()

    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt"], inplace=True, log1p=True
    )

    # Create subplots with 1 row and 3 columns (side-by-side plots)
    fig = make_subplots(rows=1, cols=3, shared_yaxes=False, 
                        subplot_titles=("n_genes_by_counts", "total_counts", "pct_counts_mt"))

    # Add the first violin plot for 'n_genes_by_counts' in the first column
    fig.add_trace(go.Violin(y=adata.obs['n_genes_by_counts'], box_visible=True, 
                            points='all', name='n_genes_by_counts', marker_color="blue"), row=1, col=1)

    # Add the second violin plot for 'total_counts' in the second column
    fig.add_trace(go.Violin(y=adata.obs['total_counts'], box_visible=True, 
                            points='all', name='total_counts', marker_color="red"), row=1, col=2)

    # Add the third violin plot for 'pct_counts_mt' in the third column
    fig.add_trace(go.Violin(y=adata.obs['pct_counts_mt'], box_visible=True, 
                            points='all', name='pct_counts_mt', marker_color="green"), row=1, col=3)

    # Update layout for better spacing and titles
    fig.update_layout(height=400, width=1000, showlegend=False, title_text="Violin Plots of Metrics")

    # Show the plot

    return dcc.Graph(figure=fig)