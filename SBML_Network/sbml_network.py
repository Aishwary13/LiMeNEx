import xml.etree.ElementTree as ET
import pandas as pd

import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import json
import os
from css import ex_stylesheet
from itertools import chain
from dash_extensions import EventListener


ns = {'celldesigner': 'http://www.sbml.org/2001/ns/celldesigner', '': 'http://www.sbml.org/sbml/level2/version4',
        'html': 'http://www.w3.org/1999/xhtml'}

def parseReaction(rx,idToName):

    reactionType = rx.find('.//celldesigner:reactionType', ns).text
    isReversible = rx.get('reversible')
    reactInfo = rx.find('.//html:customInfo', ns)
    if reactInfo is not None:
        infoVar = reactInfo.get('info')
    else:
        infoVar = 'notAssignedInfo'

    reactantList = []
    productList = []
    geneList = []
    geneModifierType = []
    for reactant in rx.findall('.//celldesigner:baseReactant', ns):
        source = reactant.get('species')
        reactantList.append(idToName[source])

    for product in rx.findall('.//celldesigner:baseProduct', ns):
        target = product.get('species')
        productList.append(idToName[target])

    for modifier in rx.findall('.//celldesigner:modification', ns):
        modifier_species = modifier.get('modifiers')
        modifierType = modifier.get('type')
        geneList.append(idToName[modifier_species])
        geneModifierType.append(modifierType)
    
    return {
        'reactionType' : reactionType,
        'isReversible' : isReversible,
        'reactInfo' : infoVar,
        'reactantList' : reactantList,
        'productList' : productList,
        'geneList' : geneList,
        'geneModifierType' : geneModifierType
    }


def readSbml(filePath,finalNodes,finalNodeSet,finalEdges,reactionNum):

    # Load and parse the XML file
    tree = ET.parse(filePath)
    root = tree.getroot()

    genes = []
    for gene in root.findall('.//celldesigner:gene', ns):
        genes.append(gene.get('name'))

    nodes = []
    pathwayName = filePath.split('//')[-1][:-4]
    idToName = {}
    for species in root.findall('.//species',ns):
        # print(species)
        species_id = species.get('id')
        species_name = species.get('name')
        idToName[species_id] = species_name

        if species_name in finalNodeSet:
            for itr in finalNodes:
                if itr['data']['label'] == species_name:
                    itr['data']['pathway'].append(pathwayName)
                    break
            continue
        else:
            finalNodeSet.add(species_name)

        nodeClass = species.find('.//html:customClass', ns)
        if nodeClass is not None:
            classVar = nodeClass.get('type')
        else:
            classVar = 'notAssignedNode'

        # Extract the reactions catalyzed
        catalyzed_reactions = []
        for reaction in species.findall('.//celldesigner:catalyzed', ns):
            catalyzed_reactions.append(reaction.get('reaction'))
        
        # Create a node dictionary
        node = {
            'data': {
                'id': species_name,
                'label': species_name,
                'catalyzes': catalyzed_reactions,
                'pathway' : [pathwayName],
                'classes' : classVar
            },
            'classes' : classVar
        }
        nodes.append(node)

    # Extract reactions (edges)
    edges = []
    for reaction in root.findall('.//reaction', ns):

        reactData = parseReaction(reaction, idToName)

        #handle existing case
        #----------------------------------------------------------------------------------------

        #----------------------------------------------------------------------------------------

        reactionId = reactionNum
        reactionNum+=1

        #Create Mid node
        temp = {
            'data': {
                'id': f"mid_{reactionId}",
                'label': f'mid_{reactionId}',
                'pathway' : [pathwayName],
                'classes' : 'temp',
            },
            'classes' : 'temp'
        }
        nodes.append(temp)

        for reactant in reactData['reactantList']:
            edges.append({
                'data' : {
                    'source' : reactant,
                    'target' :f"mid_{reactionId}",
                    'classes' : 'first_half',
                    'label' : ""
                },
                'classes' : 'first_half'
            })
        
        for reactant in reactData['productList']:
            edges.append({
                'data' : {
                    'source' : f"mid_{reactionId}",
                    'target' : reactant,
                    'classes' : 'second_half',
                    'label': ""
                },
                'classes' : 'second_half'
            })
        
        for gene,modification in zip(reactData['geneList'],reactData['geneModifierType']):
            edges.append({
                'data' : {
                    'source' : gene,
                    'target' : f"mid_{reactionId}",
                    'classes' : modification,
                    'label' : ""
                },
                'classes' : modification
            })
        
    finalNodes.extend(nodes)
    finalEdges.extend(edges)

    return

def readMapping(df, finalNodes, finalEdges,finalNodeSet):

    global followers_node_di  # user id -> list of followers (cy_node format)
    global followers_edges_di # user id -> list of cy edges ending at user id

    transcriptionFactor = df['TF'].unique()
    targetGene = df['TargetGene'].unique()

    # nodes = []
    # edges = []
    for tf in transcriptionFactor:

        mask2 = (df['TF'] == tf)
        temp2 = df[mask2]
        tissueList = temp2['Tissue'].unique()
        nodeTissues = "_T ".join(tissueList) + "_T"

        for tg in targetGene:

            mask = (df['TF'] == tf) & (df['TargetGene'] == tg)

            temp = df[mask]

            if temp.empty:
                continue
            
            if not followers_node_di.get(tg):
                followers_node_di[tg] = []
            if not followers_edges_di.get(tg):
                followers_edges_di[tg] = []
            
            tissueList = temp['Tissue'].unique()
            edgeTissues = "_T ".join(tissueList) + "_T"

            followers_edges_di[tg].append({
                'data' : {
                    'source' : tf,
                    'target' : tg,
                    'tissueClass' : f"TRANSCRIPTION {edgeTissues}",
                    'label' : ""
                },
                'classes' : f"TRANSCRIPTION"
            })

            if tf not in finalNodeSet:
                followers_node_di[tg].append({
                    'data' : {
                        'id' : tf,
                        'label' : tf,
                        'tissueClass' : f"transcriptionFactorGene {nodeTissues}"
                    },
                    'classes' : f"transcriptionFactorGene"
                })
            else:
                ##############################################################
                for ele in finalNodes:

                    if ele.get("data").get("label") == tf:
                        ele.get("data")["tissueClass"] = f"{ele.get('classes')} {nodeTissues}"
                        break
                #####################################################################
    
    return followers_node_di, followers_edges_di

########################################################################################################


app = dash.Dash(__name__)

cyto.load_extra_layouts()
basePath = 'D:/Raylab/LiMeNEx/SBML_Network'

followers_node_di = {}
followers_edges_di = {}

#########################################################################################################

@app.callback(
    Output('cytoscape', 'elements',allow_duplicate=True),
    Output('cytoscape','stylesheet', allow_duplicate=True),
    Input('pathwayDropdownOptions', 'value'),
    State('cytoscape','stylesheet'),
    prevent_initial_call = True
)
def handlePathwaySelection(optionList, stylesheet):
    if optionList is None:
        return [], stylesheet

    if len(optionList) != 0:

        global followers_node_di
        global followers_edges_di 

        followers_edges_di = {}
        followers_node_di = {}

        finalNodes = []
        finalEdges = []
        finalNodeSet = set()
        finalReactionList = []
        reactionNum = 1

        dfList = []
        for fileName in optionList:
            filePathSbml = os.path.join(basePath,'networkFile',f"{fileName}.xml")
            filePathTf = os.path.join(basePath,'pathwayTfs',f"{fileName}.csv")
            readSbml(filePath=filePathSbml,finalNodes=finalNodes,finalNodeSet=finalNodeSet,finalEdges=finalEdges, reactionNum=reactionNum)
            
            if os.path.exists(filePathTf):
                temp = pd.read_csv(filePathTf)
                dfList.append(temp)
        
        combinedDf = pd.concat(dfList, ignore_index=True)

        # adding display stylesheet for each tissue
        uniqueTissue = combinedDf['Tissue'].unique()
        for tis in uniqueTissue:
            stylesheet.extend([{
                "selector" : f".{tis}_T",
                "style" : {"display" : "element"}
            }])

        readMapping(df = combinedDf,finalNodes=finalNodes,finalEdges=finalEdges,finalNodeSet=finalNodeSet)

        return finalNodes+finalEdges, stylesheet
    else:
        new_stylesheet = []
        for style in stylesheet:
            if 'T_' != style.get('selector')[-1:-3:-1]:
                new_stylesheet.append(style)

        return [], new_stylesheet

@app.callback(
    Output("cytoscape", "stylesheet", allow_duplicate=True),
    Output("cytoscape", "elements", allow_duplicate=True),
    Input("cytoscape", "tapNodeData"),
    State("cytoscape", "elements"),
    State("cytoscape", 'stylesheet'),
    State("physiologicalDropdownOptions", "value"),
    State("tissueDropdownOptions", "value"),
    prevent_initial_call=True,
)
def generateTfs(nodeData, elements,stylesheet,physOptions,tisOptions):
    global followers_node_di
    global followers_edges_di
    
    # print(json.dumps(elements,indent=2))

    if not nodeData:
        return stylesheet,elements

    # Find the node in the elements list
    for element in elements:
        if nodeData["id"] == element.get("data").get("id"):
            # If the node is already expanded, remove its followers
            # print(nodeData)
            if element["data"].get("expanded"):
                element["data"]["expanded"] = False
                # Remove all followers associated with this node
                followers_nodes = followers_node_di.get(nodeData["id"], [])
                followers_edges = followers_edges_di.get(nodeData["id"], [])

                elements = [el for el in elements if el not in followers_nodes or el not in followers_edges]
                break
            else:
                # If the node is not expanded, set it to expanded and add followers
                element["data"]["expanded"] = True
                followers_nodes = followers_node_di.get(nodeData["id"])
                followers_edges = followers_edges_di.get(nodeData["id"])

                if followers_nodes:
                    elements.extend(followers_nodes)

                if followers_edges:
                    elements.extend(followers_edges)
                break
    
    if ((tisOptions is None) or len(tisOptions) == 0) and (physOptions is None or len(physOptions) == 0):
        return stylesheet, elements
    elif (tisOptions is not None) and len(tisOptions) != 0:
        return handleTissueSelection(tisOptions=tisOptions,stylesheet=stylesheet,phySystemOptions=physOptions,elements=elements)
    else:
        return handlePhysiologicalSelection(val=physOptions,stylesheet=stylesheet,elements=elements)


def processElements(elements, allowedTissues):

    tfList = set()
    newElements = []
    ##3 first processing edges and making Tf list 
    for ele in elements:
        src = ele.get("data").get("source")
        cl = ele.get("data").get("tissueClass")
        if src is None:
            continue
        
        if cl is None:
            newElements.append({
                'data' : ele.get("data"),
                'classes' : ele.get("data").get("classes")
            })
            continue

        cl = cl.split(" ")
        firstClass = cl[0]
        cl = cl[1:]

        commonTissue = list(allowedTissues & set(cl))
        notAllowed = list(set(cl) - set(commonTissue))

        if len(commonTissue) != 0:
            newClassFormat = [firstClass] + commonTissue
            tfList.add(src)
        else:
            newClassFormat = [firstClass] + notAllowed
        
        newClassFormat = " ".join(newClassFormat)
        newElements.append({
            'data' : ele.get("data"),
            'classes' : newClassFormat
        })

    #processing nodes
    for ele in elements:
        label = ele.get("data").get("source")
        cl = ele.get("data").get("tissueClass")

        if label:
            continue
        
        if cl is None:
            newElements.append({
                'data' : ele.get("data"),
                'classes' : ele.get("data").get("classes")
            })
            continue

        cl = cl.split(" ")
        firstClass = cl[0]
        cl = cl[1:]

        commonTissue = list(allowedTissues & set(cl))
        notAllowed = list(set(cl) - set(commonTissue))

        if label in tfList:
            newClassFormat = [firstClass] + commonTissue
        else:
            newClassFormat = [firstClass] + notAllowed

        newClassFormat = " ".join(newClassFormat)
        newElements.append({
            'data' : ele.get("data"),
            'classes' : newClassFormat
        })

    return newElements

@app.callback(
    Output("cytoscape", "stylesheet", allow_duplicate= True),
    Output("cytoscape","elements",allow_duplicate= True),
    Input("physiologicalDropdownOptions", "value"),
    State("cytoscape", "stylesheet"),
    State("cytoscape","elements"),
    prevent_initial_call=True,
)
def handlePhysiologicalSelection(val,stylesheet, elements):
    global physiologicalSystemDf
    global psToTissue

    if val is None:
        return stylesheet,elements

    if len(val) != 0:
        basic_stylesheet = []
        show_stylesheet = []
        hide_stylesheet = []

        for style in stylesheet:
            selector = style.get('selector')

            if 'T_' == selector[-1:-3:-1]:
                if list(physiologicalSystemDf[(physiologicalSystemDf['Tissue'] == selector[1:-2])]['Physiological System'])[0] in val:
                    style.get('style')['display'] = 'element'
                    show_stylesheet.append(style)
                else:
                    style.get('style')['display'] = 'none'
                    hide_stylesheet.append(style)
            else:
                basic_stylesheet.append(style)
        
        
        basic_stylesheet.extend(show_stylesheet)
        basic_stylesheet.extend(hide_stylesheet)

        allowedTissues = list(chain(*[psToTissue[sys] for sys in val]))
        allowedTissues = set([var+"_T" for var in allowedTissues])

        # print(allowedTissues)
        newElements = processElements(elements,allowedTissues)

        return basic_stylesheet, newElements

    else:
        for style in stylesheet:
            if 'T_' == style.get('selector')[-1:-3:-1]:
                style.get('style')['display'] = 'element'

        return stylesheet, elements
    
@app.callback(
    Output("tissueDropdownOptions", "options"),
    Input("physiologicalDropdownOptions", "value"),
)
def changeTissueOptions(phySystemOptions):
    global psToTissue

    # Return placeholder option if no physiological system is selected
    if phySystemOptions is None or len(phySystemOptions) == 0:
        return [{'label': 'Select Physiological System To View Tissues List', 'value': 'null'}]

    if len(phySystemOptions) != 0:
        # Collect tissues and format labels with the system name
        tissueOptions = []  
        for system in phySystemOptions:
            tissues = psToTissue.get(system, [])
            for tissue in tissues:
                tissueOptions.append({'label': f"{system}: {tissue}", 'value': tissue})

        return tissueOptions
    else:
        
        return [{'label': 'Select Physiological System To View Tissues List', 'value': 'null'}]

@app.callback(
    Output("cytoscape", "stylesheet", allow_duplicate=True),
    Output("cytoscape","elements",allow_duplicate= True),
    Input("tissueDropdownOptions", "value"),
    State("cytoscape", "stylesheet"),
    State("physiologicalDropdownOptions","value"),
    State("cytoscape","elements"),
    prevent_initial_call=True,
)
def handleTissueSelection(tisOptions, stylesheet,phySystemOptions,elements):

    if tisOptions is None:
        return stylesheet, elements
    
    if len(tisOptions) != 0:

        if 'null' in tisOptions:
            return stylesheet

        basic_stylesheet = []
        show_stylesheet = []
        hide_stylesheet = []
        for style in stylesheet:
            selector = style.get('selector')

            if 'T_' == selector[-1:-3:-1]:
                # print(physiologicalSystemDf[(physiologicalSystemDf['Tissue'] == selector[:-2][1:])]['Physiological System'])
                if selector[:-2][1:] in tisOptions:
                    style.get('style')['display'] = 'element'
                    show_stylesheet.append(style)
                else:
                    style.get('style')['display'] = 'none'
                    hide_stylesheet.append(style)
            else:
                basic_stylesheet.append(style)
        
        basic_stylesheet.extend(hide_stylesheet)
        basic_stylesheet.extend(show_stylesheet)

        allowedTissue = set([var+'_T' for var in tisOptions])

        newElements = processElements(elements,allowedTissue)
    
        return basic_stylesheet ,newElements
    else:
        return handlePhysiologicalSelection(phySystemOptions,stylesheet, elements)
    
@app.callback(
    Output('hoverTooltip', 'style'),
    Output('tooltip-content', 'children'),
    Input('cytoscape', 'tapEdgeData'),
    Input('close-tooltip', 'n_clicks'),
    State('cytoscape-mousemove-listener', 'event'),  # Now as Input
    State('hoverTooltip', 'style'),
)
def display_hover(tap_edge_data, close_click, event, style):
    ctx = dash.callback_context

    if not ctx.triggered:
        style['display'] = 'none'
        return style, ''
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # print(f"Triggered by: {triggered_id}")

    if triggered_id == 'close-tooltip':
        style['display'] = 'none'
        return style, ''

    if triggered_id == 'tapEdgeData':
        # print(f"Coordinates: {coord}")
        style['display'] = 'block'
        style['top'] = f"{event['clientY']}px"
        style['left'] = f"{event['clientX']}px"
        return style, f"source: {tap_edge_data['source']} to target: {tap_edge_data['target']}"
    else:
        style['display'] = 'none'
        return style, ''
    
###########################################################################################################
with open("D:/Raylab/LiMeNEx/SBML_Network/pathwayDropdownOptions.json", 'r') as file:
    # Load the JSON data
    dropdownOptions = json.load(file)
    pathwayDropdownOptions = dropdownOptions["PathwayOptions"]
    physiologicalSystemOptions = dropdownOptions["physiologicalOptions"]
    physiologicalSystemDf = pd.read_csv('D:/Raylab/LiMeNEx/SBML_Network/Physiologicalsystem.csv')

    psToTissue = {}
    for ps in physiologicalSystemDf['Physiological System'].unique():
        psToTissue[ps] = list(physiologicalSystemDf[(physiologicalSystemDf['Physiological System'] == ps)]['Tissue'].unique())
    


# elements = finalNodes + finalEdges

app.layout = html.Div([
    dcc.Store(id='mouse-coordinates', data={'x' : 0,'y' : 0}),

    dcc.Dropdown(
        id = 'pathwayDropdownOptions',
        options=[
            {'label' : 'All Pathways', 'value' : 'ALL'},
            *[{'label': key, 'value': pathwayDropdownOptions[key]} for key in pathwayDropdownOptions.keys()]
        ],
        multi= True,
        maxHeight=300,
        optionHeight=30,
        placeholder="Select one or more pathways"
    ),
    dcc.Dropdown(
        id = 'physiologicalDropdownOptions',
        options=[
            *[{'label': key, 'value': key} for key in physiologicalSystemOptions]
        ],
        multi= True,
        maxHeight=300,
        optionHeight=30,
        placeholder="Select one or more physiological System"
    ),
    dcc.Dropdown(
        id = 'tissueDropdownOptions',
        options=[
            {'label': 'Select Physiological System To View Tissues List', 'value': 'null'}
        ],
        multi= True,
        maxHeight=300,
        optionHeight=30,
        placeholder="Select one or more Tissue"
    ),
    EventListener(
        id='cytoscape-mousemove-listener',
        events=[{"event": "click", "props": ["clientX", "clientY"]}],
        children = [
            cyto.Cytoscape(
                id='cytoscape',
                elements=[],
                layout={'name': 'cose-bilkent'},  #dagre, cose-bilkent, 
                style={'width': '100%', 'height': '600px'},
                boxSelectionEnabled = True,
                stylesheet=ex_stylesheet
            )
        ]
    ),
    html.Div(id='hoverTooltip', style={
        'display': 'none',
        'position': 'absolute',
        'padding': "0.25em 0.5em",
        'backgroundColor': 'black',
        'color': 'white',
        'textAlign': 'center',
        'borderRadius': '0.25em',
        'whiteSpace': 'nowrap',
        'zIndex': '1001',
        'pointerEvents': 'auto'
    },
        children=[
                html.Button('X', id='close-tooltip', n_clicks=0, style={
                    'position': 'absolute',
                    'top': '2px',
                    'right': '2px',
                    'background': 'transparent',
                    'border': 'none',
                    'color': 'white',
                    'cursor': 'pointer',
                    'fontSize': '12px',
                    'lineHeight': '12px',
                }),
                # Content of the tooltip
                html.Div(id='tooltip-content', style={'marginTop': '1.2em'})  # Adding top margin to separate from button
            ]
    )
    # html.Div(id="mouse-coordinates")
])



if __name__ == '__main__':
    app.run_server(debug=True, port = 6060)



    
