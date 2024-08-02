from flask import Flask
import base64
import datetime
import io
from dash import html, Dash, Output, Input , dcc, ctx, State, callback
import dash
import dash_cytoscape as cyto
import math
import pandas as pd
import networkx as nx
import os
import numpy as np
import json
import dash_bootstrap_components as dbc
import subprocess
import shutil
import uuid
import zipfile
import glob
from flask import session
from pages.uniportApi import get_uniprot_entry
from pages.css import sigDown, sigUp, hideGrid, highlightLipid, highlightGene, default_stylesheet, default_stylesheet2

# dash.register_page(__name__)

def create_session_folder():
    session_id = str(uuid.uuid4())

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # session['session_id'] = session_id
    session_id = session.get('session_id', None)
    session_folder = os.path.join('rScript', 'sessions', session_id)
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
    
    return session_folder

def clean_session_folder():
    # print("in cleaning folder")
    session_id = session.get('session_id', None)
    if session_id:
        session_folder = os.path.join('rScript','sessions', session_id)
        # print("here 2",session_folder)
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)
        if os.path.exists('D:/Raylab/NewNetwork/assets/plots'):
            shutil.rmtree('D:/Raylab/NewNetwork/assets/plots')
            os.makedirs('D:/Raylab/NewNetwork/assets/plots')

        session.pop('session_id', default=None)
    else:
        if os.path.exists('D:/Raylab/NewNetwork/assets/plots'):
            shutil.rmtree('D:/Raylab/NewNetwork/assets/plots')
            os.makedirs('D:/Raylab/NewNetwork/assets/plots')

def copy_folder_contents(src_folder, dst_folder):
    """
    Copies the contents of src_folder to dst_folder.
    """
    # Ensure the destination folder exists
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)

    # List all items in the source folder
    items = os.listdir(src_folder)
    
    for item in items:
        src_item = os.path.join(src_folder, item)
        dst_item = os.path.join(dst_folder, item)

        if os.path.isdir(src_item):
            # If the item is a directory, recursively copy it
            shutil.copytree(src_item, dst_item)
        else:
            # If the item is a file, copy it
            shutil.copy2(src_item, dst_item)

@callback(
    Output("download-zip", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True
)
def generate_zip(n_clicks):
    if n_clicks is not None:
        zip_buffer = io.BytesIO()
        base_path = create_session_folder()  # Replace with the path to your folder containing "plots" and CSVs

        with zipfile.ZipFile(zip_buffer, "w") as zf:
            # Add files from "plots" folder
            plots_folder = os.path.join(base_path, "plots")
            for root, dirs, files in os.walk(plots_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_path)  # Preserve folder structure
                    zf.write(file_path, arcname=arcname)
            
            # Add CSV files from the base folder
            for file in os.listdir(base_path):
                if file.endswith(".csv"):
                    file_path = os.path.join(base_path, file)
                    arcname = os.path.relpath(file_path, base_path)  # Preserve folder structure
                    zf.write(file_path, arcname=arcname)

        zip_buffer.seek(0)
        return dcc.send_bytes(zip_buffer.getvalue(), "plots_and_csvs.zip")
    
def check_for_csv_files(directory):
    # Create a pattern for CSV files
    csv_pattern = os.path.join(directory, '*.csv')
    # Use glob to find all CSV files in the directory
    csv_files = glob.glob(csv_pattern)
    # Check if there are any CSV files
    if csv_files:
        return True  # Return True and the list of CSV files
    else:
        return False # Return False and an empty list

def get_checklist_options(disabled):
    opacity = 0.5 if disabled else 1
    return [
        {'label': html.Span('Highlight downregulated', style={'color': '#0a85ff', 'opacity': opacity}), 'value': 'd', 'disabled': disabled},
        {'label': html.Span('Highlight upregulated', style={'color': '#f53636', 'opacity': opacity}), 'value': 'u', 'disabled': disabled}
    ]

@callback(
    Output("Analysis-output", "children"),
    Output("Analysis-output", "style"),
    Output('checklist', 'options', allow_duplicate= True),
    Input("run-analysis", "n_clicks"),
    prevent_initial_call = True,
)
def RunAnalysis(n_clicks):
    # Define the options for the checklist

    if n_clicks is None:
        return "", {},get_checklist_options(True)

    session_folder = create_session_folder()
    if not check_for_csv_files(session_folder):
        return "Please upload the count matrix and metadata", {"color" : "#f53636"},get_checklist_options(True)

    try:
        # Run the Python script
        result = subprocess.run(['python', '../../rScript/temp.py', session_folder], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = "Analysis Completed"
            updata = pd.read_csv(os.path.join(session_folder, 'upregulated_lipid_genes.csv'))
            downdata = pd.read_csv(os.path.join(session_folder, 'downregulated_lipid_genes.csv'))

            significant_genes['upregulated'] = updata['genes'].to_list()
            significant_genes["downregulated"] = downdata['genes'].to_list()

            copy_folder_contents(os.path.join(session_folder, 'plots'),'D:/Raylab/NewNetwork/assets/plots')
            return output, {"color" : "#7ee089"},get_checklist_options(False)
        else:
            return f"Error: {result.stdout}",{"color" : "#f53636"}, get_checklist_options(True)
    except Exception as e:
        return f"Exception occurred: {str(e)}",{"color" : "#f53636"}, get_checklist_options(True)
    

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    session_folder = create_session_folder()
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
            df.to_csv(os.path.join(session_folder, filename), index=False, encoding='utf-8')
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
            with open(os.path.join(session_folder, filename), 'wb') as file:
                file.write(decoded)
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(f"File {filename} uploaded successfully.", style={"color" : "#7ee089","fontSize": "15px"}),
        html.H6(datetime.datetime.fromtimestamp(date), style={"color" : "#7ee089","fontSize": "15px"})
    ], style={'margin-right' : '15px'})

@callback(
    Output('initial-interval', 'n_intervals'),
    Input('initial-interval', 'n_intervals'),
)
def on_load(n_intervals):
    if n_intervals == 0:
        # Check if files were uploaded and display the message
        clean_session_folder()
        return 1
    return n_intervals

@callback(Output('output-data-upload', 'children'),
                   Output('checklist','options', allow_duplicate=True),
                   Input('upload-count-matrix', 'contents'),
                   State('upload-count-matrix', 'filename'),
                   State('upload-count-matrix', 'last_modified'),
                   prevent_initial_call = True
              )
def update_output(list_of_contents, list_of_names, list_of_dates):
    # print("Here-Callback function")
    if list_of_contents is not None:
        # print("Here-Callback function-if")
        clean_session_folder()
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children, get_checklist_options(True)
    
    session.pop('upload_status', None)
    return "", get_checklist_options(True)


def get_svg_images(folder_path):
    svg_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    return svg_files

svg_folder_path = "..\\assets\\plots"

@callback(
    Output("modal-fs", "is_open", allow_duplicate=True),
    Output("svg-container", "children"),
    Input("open-fs", "n_clicks"),
    State("modal-fs", "is_open"),
    prevent_initial_call = True
)
def toggle_modal(n, is_open):
    if n:
        svg_files = get_svg_images(svg_folder_path)
        if svg_files:
            svg_images = [html.Img(src=os.path.join(svg_folder_path, f), style={'width' : '50%'}) for f in svg_files]
            return True, svg_images
        else:
            return True, html.P("No images found in the folder.")
    return False, ""

@callback(
    Output("cytoscape2", "generateImage", allow_duplicate=True),
    Input("btn-get-jpg", "n_clicks"),
    Input("btn-get-png", "n_clicks"),
    prevent_initial_call = True
)
def get_image(get_jpg_clicks, get_png_clicks):
    if ctx.triggered:
        triggered_id = ctx.triggered_id
        ftype = triggered_id.split("-")[-1]
        action = "download"
        return {'type': ftype, 'action': action}

    # Default return for no action
    return {'type': 'png', 'action': 'store'}

@callback(
    Output("cytoscape", "zoom"),
    Output("cytoscape", "elements"),
    Input("bt-reset", "n_clicks"),
)
def reset_layout(n_clicks):
    # print(n_clicks, "click")
    return 1, cy_nodes + cy_edges

@callback(
    Output('tooltip', 'children'),
    Output('hiddentext','children'),
    Input('cytoscape2', 'tapNodeData')
)
def displayTapNodeData(data):
    if data:
        id = data["UniId"]
        if(id == ""):
            return "Uniprot ID not available",""
        
        # Immediately return a loading message
        return dcc.Loading(
            id="loading",
            type="circle",
            children=[html.Div("Loading... Data")],
        ), data
    else:
        return "", ""

@callback(
    Output('tooltip', 'children', allow_duplicate=True),
    Input('hiddentext', 'children'),
    # State('loading', 'id'),
    prevent_initial_call=True
)
def updateTapNodeData(data):
    if data:
        id = data["UniId"]

        info = get_uniprot_entry(id)
        # print(info)
        try:

            output_str = f"""
UniProt ID: {info['uniprotID'] if 'uniprotID' in info.keys() else "data not available"}
Gene Name: {info['geneName'] if 'geneName' in info.keys() else "data not available"}
Protein Name: {info['proteinName'] if 'proteinName' in info.keys() else "data not available"}
Organism Name: {info['organismName'] if 'organismName' in info.keys() else "data not available"}
Function: {info['function'] if 'function' in info.keys() else "data not available"}
Gene Ontology:
- Biological Process: {', '.join(info['go']['Biological Process']) if len(info['go']['Biological Process']) else 'data not available'}
- Molecular Function: {', '.join(info['go']['Molecular Function']) if len(info['go']['Molecular Function']) else 'data not available'}
- Cellular Component: {', '.join(info['go']['Cellular Component']) if len(info['go']['Cellular Component']) else 'data not available'}
"""
        except:
            output_str = "Uniprot ID not available + hello"

        lines = output_str.split('\n')
        paragraphs = [html.P(line) for line in lines]

        return paragraphs
    else:
        return "To get Information about the Gene. Kindly click on the Gene Node"
    
@callback(
    Output('cytoscape2', 'stylesheet', allow_duplicate=True),
    Input('checklist','value'),
    prevent_initial_call=True
)
def highlight_significant(val):
    
    if('u' in val and 'd' in val): 
        return default_stylesheet2 + sigDown + sigUp
    elif('u' in val):
        return default_stylesheet2 + sigUp
    elif('d' in val):
        return default_stylesheet2 + sigDown 
    
    return default_stylesheet2 + highlightLipid + highlightGene

@callback(
    Output('cytoscape', 'stylesheet', allow_duplicate=True),
    Output('cytoscape', 'layout', allow_duplicate=True),
    Output('cytoscape2', 'elements'),
    Output('cytoscape2', 'stylesheet'),
    Output('checklist', 'value'),
    Input('show-Molecule-pathway-layout', 'value'),
    Input('show-Gene-pathway-layout', 'value'),
    prevent_initial_call=True
)
def highlight_Molecule_pathway(mol, gene):
    if(mol == "None" or gene == "None"):
        return default_stylesheet, {"name": "preset"}, [], default_stylesheet2,[]

    if mol or gene:
        to = ""
        sour = ""
        paths_from_molecule = []
        paths_to_molecule = []
        all_nodes = []

        molecule = ''
        if mol:
            molecule = mol.split(',')

        if(molecule):
            for name in molecule:
                if(name[-1:-4:-1] == ')i('):
                    to = name
                else:
                    sour = name
        else:
            to = gene
            sour = gene

        if(sour != ""):
            try :
                for node in graph.nodes:
                    if(node != sour):
                        temp = list(nx.all_simple_paths(graph, source=sour, target=node))
                        paths_from_molecule.extend(temp)
            except :
                 paths_from_molecule = []

        if(to != ""):
            try :
                for node in graph.nodes:
                    if(node != to):
                        temp = list(nx.all_simple_paths(graph, source=node, target=to))
                        paths_to_molecule.extend(temp)
            except:
                paths_to_molecule = []


        if(len(paths_from_molecule) != 0):
            all_nodes = list(np.concatenate(paths_from_molecule).flat)
        if(len(paths_to_molecule) != 0):
            all_nodes += list(np.concatenate(paths_to_molecule).flat)

        highlight_stylesheet = [
            {"selector": f'node[id="{node}"]',
             "style": {"background-color": "#CE5A67", "height": 170, "width": 170, "label": "data(label)",
                       "font-size": "100px","color" : "#ffffff"} if node in all_nodes else {"background-color": "black", "height": 100,
                                                                   "width": 100, "label": "data(label)",
                                                                   "opacity" : 0,
                                                                   "font-size": "100px"}
             } for node in graph.nodes
        ]

        edges = [
            {
                "selector": f'edge[source="{path[i-1]}"][target="{path[i]}"]',
                "style": {
                    "line-color": "#ffffff",
                    "width": 25,
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "target-arrow-color": "#ffffff"
                }
            }
            for paths in (paths_from_molecule, paths_to_molecule) for path in paths for i in range(1, len(path))
        ]

        # Use a specific layout for better visibility
        layout = {"name": "preset"}

        second_node_list = []
        second_edge_list = []

        for node in all_nodes:
            Id = ""
            try:
                Id = str(graph.nodes[node]['Uniprot_ID'])
            except:
                Id = ""

            if node[-1:-4:-1] == ")i(" or node[-1:-5:-1] == ")ii(":
                if(node == to or node == sour):
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node[:len(node)-3] if node[-1:-4:-1] == ")i(" else (node[:len(node)-4] if node[-1:-5:-1] == ")ii(" else node)}, "classes":"Lipid"})
                else:
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node[:len(node)-3] if node[-1:-4:-1] == ")i(" else (node[:len(node)-4] if node[-1:-5:-1] == ")ii(" else node)}})

            else:
                node_classes = []
                if node in significant_genes['upregulated']:
                    node_classes.append("sigUp")
                elif node in significant_genes["downregulated"]:
                    node_classes.append("sigDown")
                
                if node == sour:
                    node_classes.append("gene")
                
                node_data = {"data": {"id": node, "UniId": Id, "label": node}}
                if node_classes:
                    node_data["classes"] = " ".join(node_classes)
                
                second_node_list.append(node_data)

        
        unique_pair = set()
        for path in paths_from_molecule:
            for i in range(1, len(path)):
                if (path[i-1], path[i]) not in unique_pair:
                    second_edge_list.append({"data" : {"source": path[i-1], "target": path[i]}, "directed" : True})
                    unique_pair.add((path[i-1],path[i]))

        for path in paths_to_molecule:
            for i in range(1, len(path)):
                if (path[i-1], path[i]) not in unique_pair:
                    second_edge_list.append({"data" : {"source": path[i-1], "target": path[i]}, "directed" : True}) 
                    unique_pair.add((path[i-1],path[i]))

        return highlight_stylesheet+edges + hideGrid, layout, second_node_list+second_edge_list, default_stylesheet2+highlightLipid+highlightGene,[]
    else:
        # If no gene is selected, revert to the default stylesheet and layout
        return default_stylesheet, {"name": "preset"}, [], default_stylesheet2,[]

@callback(
    Output('cytoscape', 'stylesheet', allow_duplicate=True),
    Output('cytoscape', 'layout', allow_duplicate=True),
    Output('cytoscape2', 'elements', allow_duplicate=True),
    Output('cytoscape2', 'stylesheet', allow_duplicate=True),
    Output('checklist', 'value',allow_duplicate=True), 
    Input('show-pathway-layout', 'value'),
    prevent_initial_call=True
)
def highlight_pathway(pathway):

    # print("here")
    if pathway in Main_Pathways.values():
        pathway = f"..\\data\\gene_pathways_new\\{pathway}.gml"
        temp_graph = read_gml_file(pathway)
        
        all_nodes = temp_graph.nodes
        all_edges = temp_graph.edges

        highlight_stylesheet = [
            {"selector": f'node[id="{node}"]',
             "style": {"background-color": "#CE5A67", "height": 170, "width": 170, "label": "data(label)",
                       "font-size": "100px", "color" : "#ffffff"} if node in all_nodes else {"background-color": "black", "height": 100,
                                                                   "width": 100, "label": "data(label)",
                                                                   "opacity" : 0,
                                                                   "font-size": "100px"}
             } for node in graph.nodes
        ]
        edges = [ {
                "selector": f'edge[source="{edge[0]}"][target="{edge[1]}"]',
                "style": {"line-color": "#ffffff",
                           "width": 25,
                           "curve-style": "bezier",  
                            "target-arrow-shape": "triangle",  
                            "target-arrow-color": "#ffffff"
                        }
            }for edge in all_edges
        ]
    
        # Use a specific layout for better visibility
        layout = {"name": "preset"}

        # other cytoscape2 
        
        second_node_list = []
        second_edge_list = []

        for node in all_nodes:
            Id = ""
            try:
                Id = str(graph.nodes[node]['Uniprot_ID'])
            except:
                Id = ""

            if node[-1:-4:-1] == ")i(" or node[-1:-5:-1] == ")ii(":
                second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node[:len(node)-3] if node[-1:-4:-1] == ")i(" else (node[:len(node)-4] if node[-1:-5:-1] == ")ii(" else node)}, "classes":"Lipid"})
            else:
                if(node in significant_genes['upregulated']):
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}, "classes":"sigUp"})
                elif(node in significant_genes["downregulated"]):
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}, "classes":"sigDown"})
                else:
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}})

        for edge in all_edges:
            second_edge_list.append({"data" : {"source": edge[0], "target": edge[1]}, "directed" : True})
        

        return highlight_stylesheet+edges + hideGrid, layout, second_node_list+second_edge_list, default_stylesheet2+highlightLipid,[]
    else:
        # If no gene is selected, revert to the default stylesheet and layout
        return default_stylesheet, {"name": "preset"}, [], default_stylesheet2,[]



@callback(
    Output('cytoscape', 'stylesheet'),
    Output('cytoscape', 'layout'),
    Output('cytoscape2', 'elements', allow_duplicate=True),
    Input('start-gene-input', 'value'),
    Input('end-gene-input', 'value'),
    prevent_initial_call=True
)
def highlight_path(start_gene_name, end_gene_name):
    if start_gene_name and end_gene_name:
        # Update the stylesheet to highlight the path from start_gene_name to gene_name
        all_paths = list(nx.all_simple_paths(graph, source=start_gene_name, target=end_gene_name))

        # print(all_paths)
        all_nodes = list(np.concatenate(all_paths).flat)

        highlight_stylesheet = [
            {"selector": f'node[id="{node}"]',
             "style": {"background-color": "#CE5A67", "height": 170, "width": 170, "label": "data(label)",
                       "font-size": "100px", "color" : "#ffffff"} if node in all_nodes else {"background-color": "black", "height": 100,
                                                                   "width": 100, "label": "data(label)",
                                                                   "opacity" : 0,
                                                                   "font-size": "100px"}
             } for node in graph.nodes
        ]
        edges =[ {
                "selector": f'edge[source="{path[i-1]}"][target="{path[i]}"]',
                "style": {"line-color": "#ffffff",
                           "width": 25,
                           "curve-style": "bezier",  
                            "target-arrow-shape": "triangle",  
                            "target-arrow-color": "#ffffff"
                        }
            }for path in all_paths for i in range(1, len(path))
        ]

        # Use a specific layout for better visibility
        layout = {"name": "preset"}

        second_node_list = []
        second_edge_list = []

        for node in all_nodes:
            Id = ""
            try:
                Id = str(graph.nodes[node]['Uniprot_ID'])
            except:
                Id = ""

            if node[-1:-4:-1] == ")i(" or node[-1:-5:-1] == ")ii(":
                second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node[:len(node)-3] if node[-1:-4:-1] == ")i(" else (node[:len(node)-4] if node[-1:-5:-1] == ")ii(" else node)}, "classes":"Lipid"})
            else:
                if(node in significant_genes['upregulated']):
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}, "classes":"sigUp"})
                elif(node in significant_genes["downregulated"]):
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}, "classes":"sigDown"})
                else:
                    second_node_list.append({"data" : {"id": node,"UniId":Id ,"label": node}})

        
        for path in all_paths:
            for i in range(1,len(path)):
                second_edge_list.append({"data" : {"source": path[i-1], "target": path[i]}, "directed" : True})


        return highlight_stylesheet+edges + hideGrid, layout, second_node_list+second_edge_list
    else:
        # If no gene is selected, revert to the default stylesheet and layout
        return default_stylesheet, {"name": "preset"}, []


def read_gml_file(file_path):
    graph = nx.read_gml(file_path)
    return graph

def return_levels(adj_matrix, start_node,indDic, region, startlevel = 1):
    levels = {indDic[start_node]: startlevel}  # Dictionary to store the level of each node
    sector = {indDic[start_node]: region}

    # Initialize a queue for BFS traversal
    queue = [start_node]

    while queue:
        current_node = queue.pop(0)
        current_level = levels[indDic[current_node]]
        
        #source
        for node in range(0,len(adj_matrix[0])):
            if node==current_node:
                continue
            
            if adj_matrix[current_node][node] == 1:
                if indDic[node] not in levels:
                    levels[indDic[node]] = current_level-1
                    sector[indDic[node]] = region
                    queue.append(node)

        #target
        for node in range(0,len(adj_matrix)):
            if node==current_node:
                continue
            
            if adj_matrix[node][current_node] == 1:
                if indDic[node] not in levels:
                    levels[indDic[node]] = current_level+1
                    sector[indDic[node]] = region
                    queue.append(node)

    return levels,sector

def mergeGraph(graph1, graph2):
    merged = nx.compose(graph1,graph2)
    return merged

def get_max_level(dic):
    maxi = 0
    for i in dic.keys():
        maxi = max(maxi,dic[i])

    return maxi

def get_extreme_nodes():
    # Initialize empty lists to store unique values from each column
    start_node = []
    end_node = []
    
    folder_path = '..\doc'
    # Iterate over each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.xlsx'):

            # Construct the full path to the Excel file
            file_path = os.path.join(folder_path, filename)
            
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(file_path)
            start_node.extend(df.iloc[:, 0].unique())
            
            end_node.extend(df.iloc[:, 1].unique())

    # Remove duplicates from the lists
    start_node = list(set(start_node))
    end_node = list(set(end_node))
    return start_node,end_node

def read_graph(startNode=""):
    path1 = '..\data\gene_pathways_new\cholesterol_synthesis_graph.gml'
    path2 = '..\data\gene_pathways_new\cholesterol_degradation_graph.gml'
    path3 = '..\data\gene_pathways_new\sphingolipid_synthesis.gml'
    path4 = '..\data\gene_pathways_new\Phospholipid_degradation_pathway.gml'
    path5 = '..\data\gene_pathways_new\phospholipid_synthesis_graph.gml'
    path6 = '..\data\gene_pathways_new\lipolysis.gml'
    path7 = '..\data\gene_pathways_new\Lipogenesis.gml'
    path8 = '..\data\gene_pathways_new\Beta_Oxidation_fattyacids.gml'
    path9 = '..\data\gene_pathways_new\Fatty_acid_synthesis.gml'
    path10 = '..\data\gene_pathways_new\sphingolipid_degradation.gml'

    graph1 = read_gml_file(path1)
    graph2 = read_gml_file(path2)
    graph3 = read_gml_file(path3)
    graph4 = read_gml_file(path4)
    graph5 = read_gml_file(path5)
    graph6 = read_gml_file(path6)
    graph7 = read_gml_file(path7)
    graph8 = read_gml_file(path8)
    graph9 = read_gml_file(path9)
    graph10 = read_gml_file(path10)

    graph = mergeGraph(graph1=graph1,graph2=graph2)
    graph = mergeGraph(graph1=graph, graph2=graph3)
    graph = mergeGraph(graph1=graph, graph2=graph4)
    graph = mergeGraph(graph1=graph, graph2=graph5)
    graph = mergeGraph(graph1=graph, graph2=graph6)
    graph = mergeGraph(graph1=graph, graph2=graph7)
    graph = mergeGraph(graph1=graph, graph2=graph8)
    graph = mergeGraph(graph1=graph, graph2=graph9)
    graph = mergeGraph(graph1=graph, graph2=graph10)

    adj_matrix = nx.adjacency_matrix(graph)
    adj_matrix = adj_matrix.toarray()
    indDic = {}

    # get outer and inner circle nodes 
    start_node , end_node = get_extreme_nodes()
    
    # 'Phosphatidylglycerol(i)', 'Phosphatidylserine(i)', 'Phosphatidic Acid(i)', 'lysophosphatidylcholine(i)', 'CardioLipin(i)'
    # end_node_new = ['Hexadecenal(i)','Bile_Salts(i)','Acetyl-CoA(i)','Glycerol3phosphate(i)',
    #                 'Ceramide(i)','Phosphatidylglycerol(i)', 'Phosphatidylserine(i)', 
    #                 'Phosphatidic Acid(i)', 'lysophosphatidylcholine(i)', 'CardioLipin(i)',
    #                 'Fatty Acyl-CoA(i)']
    end_node_new = ['Hexadecenal(i)','Bile_Salts(i)','Glycerol3phosphate(i)',
                'Ceramide(i)','Phosphatidylglycerol(i)', 'Phosphatidylserine(i)', 
                'lysophosphatidylcholine(i)', 'CardioLipin(i)',
                'Fatty Acyl-CoA(i)']
    end_id = []
    
    for i,x in enumerate(graph.nodes):
        indDic[i] = x
        if(x in end_node_new):
            end_id.append(i)
    
    lev1 = {}
    sector1 = {}
    r = 0
    for i in end_id:
        lev2,sector2 = return_levels(adj_matrix=adj_matrix,start_node=i,region=r,indDic=indDic)
        lev1.update(lev2)
        sector1.update(sector2)
        r+=1


    maxi = get_max_level(lev1)
    #update the level of start nodes
    for node in start_node:
        lev1[node] = maxi+2

    for node in end_node:
        lev1[node] = 1

    nx.set_node_attributes(graph,lev1,'level')
    nx.set_node_attributes(graph,sector1,'sector')
    nx.write_gml(graph, 'Finalgraph.gml')

    return graph


with open("../data/Main_Pathways.json", 'r') as file:
    # Load the JSON data
    Main_Pathways = json.load(file)

with open("../data/Main_Molecules.json", 'r') as file:
    # Load the JSON data
    Main_Molecules = json.load(file)

for keys in Main_Molecules.keys():
    Main_Molecules[keys] = ",".join(Main_Molecules[keys])

# data = pd.read_csv('data\significant_genes.csv')
significant_genes = {
    'upregulated': [],
    'downregulated': []
}

#---------------------------------------------------------------------------------------------------------
graph  = read_graph()
    # nx.write_gml(graph,'final.gml')

cy_nodes = []
class_rank = {}  # Dictionary to store number of nodes based on class
unique_sec = []
sec_level_dic = {}

Gene_List = []
num_genes = 0
num_lipids = 0

for node in list(graph.nodes):
    Id = ""
    try:
        Id = str(graph.nodes[node]['Uniprot_ID'])
    except:
        print(node)

    try:
        level = str(graph.nodes[node]['level'])
    except:
        print(node)

    try:
        sector = str(graph.nodes[node]['sector'])
    except:
        print(node)

    if node[-1:-4:-1] != ")i(" and node[-1:-5:-1] != ")ii(":
        if(node not in Gene_List):
            Gene_List.append(node)

    if sector not in unique_sec:
        unique_sec.append(sector)

    key = f"{sector}_{level}"
    if key not in sec_level_dic:
        sec_level_dic[key] = 1
    else:
        sec_level_dic[key] += 1

    if node[-1:-4:-1] == ")i(" :
        num_lipids+=1
        cy_nodes.append({"data": {"id": node, "label": node[:len(node)-3],"UniId":Id}, "level": level, "sector":sector, "classes" : "Lipid"})
    elif node[-1:-5:-1] == ")ii(" :
        num_lipids+=1
        cy_nodes.append({"data": {"id": node, "label": node[:len(node)-4], "UniId":Id}, "level": level, "sector":sector, "classes" : "Lipid"})
    else:
        num_genes+=1
        cy_nodes.append({"data": {"id": node, "label": node, "UniId":Id}, "level": level, "sector":sector, "classes" : "gene"})


    if level not in class_rank:
        class_rank[level] = 1
    else:
        class_rank[level] = class_rank[level]+1

sec_level_track = {}
offset = -(2*math.pi/len(unique_sec))
radius =  0
for color, count in class_rank.items():
    k = int(color)
    if(k==1):
        radius = 2000 + 500*k
    else:
        radius = 2000 + 500*(k+1)
    start = 0.0
    for i, node in enumerate(filter(lambda x: x["level"] == color, cy_nodes)):
        key = f"{node['sector']}_{k}"

        if key not in sec_level_track:
            sec_level_track[key] = 0
            dis = 0
        else:
            sec_level_track[key] += 1
            dis = sec_level_track[key]

        angle = int(node['sector']) * (2*math.pi)/len(unique_sec) + offset*(1/sec_level_dic[key])*dis
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        node["position"] = {"x": x, "y": y}


for color, count in class_rank.items():
    # radius = (300)*(int(color))
    k = int(color)
    if(k == 1):
        radius = 2000 + 500*k
    else:
        radius = 2000 + 500*(k+1)
        
    end = 25*k
    for i in range(1, end):
        angle = (2 * math.pi * i) / end
        # radius = 300 * int(color)
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        node_id = f"circle_{color}_{i}"
        cy_nodes.append({"data": {"id": node_id, "label": ""}, "classes": f"circle {color}","position" : {"x": x, "y": y}})


cy_edges = []

for edge in list(graph.edges):

    cy_edges.append(
        {  # Add the Edge Node
            "data": {"source": edge[0], "target": edge[1], "directed": True}
        }
    )

modal = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Analysis Plots")),
            dbc.ModalBody(html.Div(id = "svg-container")),
        ],
        id="modal-fs",
        fullscreen=True,
    )
])

layout = html.Div(
    [   modal,
        dcc.Interval(id='initial-interval', interval=1*1000, n_intervals=0, max_intervals=1),
        dcc.Download(id="download-zip"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div(
                    [
                        html.Label('Select Pathway', style={"text-align" : "center", "color": "#dcdcdc", "font-weight": "bold","margin-right":"3px"}),
                        dcc.Dropdown(
                            id='show-pathway-layout',
                            clearable=True,
                            placeholder="Select Specific Pathway",
                            options=[
                                {'label': 'None', 'value': 'None'},
                                *[{'label': key, 'value': Main_Pathways[key]}
                                for key in Main_Pathways.keys()]
                            ],
                            style= {"width" : "100%"}
                            
                        ),
                    ],
                        style={"display": "flex", "width": "33.3%"}
                    ),
                
                    html.Div(
                    [
                        html.Label('Select Lipid Molecules', style={"text-align" : "center", "color": "#dcdcdc", "font-weight": "bold"}), ##212529
                        dcc.Dropdown(
                            id='show-Molecule-pathway-layout',
                            clearable=True,
                            placeholder="Select Lipid Molecule",
                            options=[
                                {'label': 'None', 'value': 'None'},
                                *[{'label': key, 'value': Main_Molecules[key]}
                                for key in Main_Molecules.keys()]
                            ],
                            style = {"width" : "100%"}
                        ),
                    ],
                        style={"display": "flex", "width": "33.3%"}
                    ),
                    
                    html.Div(
                    [
                        html.Label('Select Gene', style={"text-align" : "center", "color": "#dcdcdc", "font-weight": "bold","margin-right":"3px","margin-left":"3px"}),
                        dcc.Dropdown(
                            id='show-Gene-pathway-layout',
                            clearable=True,
                            placeholder="Select Gene",
                            options=[
                                {'label': 'None', 'value': 'None'},
                                *[{'label': key, 'value': key}
                                for key in Gene_List]
                            ],
                            style = {"width" : "80%"}
                        ),
                    ],
                        style={"display": "flex","width": "33.3%"}
                    )
                ],
                    style={"display" : "flex", "margin-bottom" : "10px"}
                ),

                html.Div(
                    [
                        html.Div(
                        [
                            html.Label('Select Start Gene',  style={"text-align" : "center", "color": "#dcdcdc", "font-weight": "bold"}),
                            dcc.Dropdown(
                                id='start-gene-input',
                                clearable=True,
                                placeholder="Select Gene",
                                options=[
                                    {'label': 'None', 'value': 'None'},
                                    *[{'label': key, 'value': key}
                                    for key in Gene_List]
                                ],
                                style = {"width" : "100%", }
                            )
                        ],
                            style= {"width" : "33.3%", "display" : "flex"}
                        ),
                        html.Div(
                        [
                            html.Label('Select End Gene',  style={"text-align" : "center", "color": "#dcdcdc", "font-weight": "bold"}),
                            dcc.Dropdown(
                                id='end-gene-input',
                                clearable=True,
                                placeholder="Select Gene",
                                options=[
                                    {'label': 'None', 'value': 'None'},
                                    *[{'label': key, 'value': key}
                                    for key in Gene_List]
                                ],
                                style = {"width" : "100%"}
                            )
                        ],
                            style= {"width" : "33.3%", "display" : "flex"}
                        ),
                    ],
                    style={"display": "flex", "width" : "100%"}
                )],

                style= {"width":"100%", "padding":"5px","paddingtop" : "7px"}
            ),
        ],  
            className="navbar"
        ),

        html.Div([
            html.Div([
                html.A('Want to do your own analysis ? Then upload your count matrix and metadata', style={'margin':'8px','align-items':'center','color':"#ffffff"}),
                dcc.Upload(
                    id='upload-count-matrix',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select File')
                    ], style={'color': '#ffffff'}),
                    style={
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'borderColor' : '#fca117'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                dcc.Loading(
                    id="loading",
                    type="default",
                    children=html.Div(id='output-data-upload', style={"display" : "flex"})
                ),
                html.Button("Show plots", id="open-fs", style={"margin-top":"5px","margin-bottom":"5px", "margin-right" : "7px"}),
                html.Button("Run Analysis", id="run-analysis", style={"margin-top":"5px","margin-bottom":"5px","margin-right" : "7px"},n_clicks=0),
                html.Button("Download ZIP", id="btn-download",style={"margin-top":"5px","margin-bottom":"5px"},n_clicks=0),
                dcc.Loading(
                    id="analysis-loading",
                    type="default",
                    children=html.Div(id='Analysis-output',style={"color" : "#7ee089"})
                )
            ],
                style={"border-radius": "5px","border-style" : "solid","border-width" : "1px", 'width' : '100%', 'padding':'5px',"background-color" : "#292929" }
            )
            
        ],
            style = {"padding-left":"15px","padding-right":"15px","padding-top":"150px"}
        ),

        html.Div(
        [   
            html.Div([
                html.Button("Reset", id="bt-reset", style={"margin-top":"3px","margin-bottom":"3px"}),
                cyto.Cytoscape(
                    id="cytoscape",
                    elements=cy_nodes + cy_edges,
                    stylesheet=default_stylesheet,
                    layout={"name": "preset"},
                    style={"height":"85vh","width": "100%", "border-radius": "5px"},
                )
            ],
                style={"height": "90vh","width": "45%","border-radius": "5px","border-style" : "solid","border-width" : "1px" ,"box-shadow": "0 3px 3px 0 rgba(0, 0, 0, 0.3)", "background-color" : "#292929", "align-items": "center", "display":"flex", "flex-direction":"column"}
            ),
            html.Div(
                [   
                    html.Div([
                        dcc.Checklist(
                            id = 'checklist',
                            options=[
                                {'label': html.Span('Highlight downregulated', style={'color':'#0a85ff', 'opacity': 0.5}), 'value': 'd', 'disabled':True},
                                {'label': html.Span('Highlight upregulated', style={'color' : '#f53636', 'opacity': 0.5}), 'value': 'u','disabled' : True}
                            ],
                            inline=True,
                            style = {"display" : "flex","alignItems" : "center","justifyContent" : "center", "gap" : "15px"}
                        ),
                        cyto.Cytoscape(
                            id="cytoscape2",
                            elements=[],
                            stylesheet=default_stylesheet2,
                            layout={"name": "cose"},
                            style={"height": "45vh", "width": "100%"},
                        ),
                        html.Div([
                            html.Div('Download graph:'),
                            html.Button("as jpg", id="btn-get-jpg"),
                            html.Button("as png", id="btn-get-png"),
                        ],
                            style={"display" : "flex","color": "#ffffff", "gap" : "6px","padding-left" : "3px"}
                        )
                    ],
                        style = {"height": "55vh", "width": "100%","border-style" : "solid","border-width" : "1px" ,"border-radius": "5px","box-shadow": "0 3px 3px 0 rgba(0, 0, 0, 0.3)", "background-color" : "#292929"}
                    ), 
                    html.P(id='tooltip', style={"height": "32vh", "width": "100%", 
                                                    "border-radius": "5px",
                                                    "border-style" : "solid","border-width" : "1px",
                                                "box-shadow": "0 3px 3px 0 rgba(0, 0, 0, 0.3)",
                                                "background-color" : "#292929", "overflowY": "scroll", "border-color": "#292929","padding" : "3px",
                                                "text-align": "left", "font-family": "Arial","word-break": "normal", "margin-top":"3vh","color":"#ffffff"}),
                    html.P(id ="hiddentext", style={"display" :"None"})
                ],
                style = {"height": "90vh", "width": "53%"}
            )
        ],
            style={"display": "flex", "justify-content" : "space-between","padding":"15px"}
        )
    ],

    style={"background-color" : "#1a1a1a","padding":"0px"}
    #white
    #F1F1F1
)
