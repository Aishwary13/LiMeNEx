import xml.etree.ElementTree as ET
import pandas as pd

import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_cytoscape as cyto
import json
import os
from css import ex_stylesheet
from itertools import chain
from dash_extensions import EventListener
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager
import io


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
                    'label' : "",
                    'reactInfo' : reactData['reactInfo']
                },
                'classes' : 'first_half'
            })
        
        for reactant in reactData['productList']:
            edges.append({
                'data' : {
                    'source' : f"mid_{reactionId}",
                    'target' : reactant,
                    'classes' : 'second_half',
                    'label': "",
                    'reactInfo' : reactData['reactInfo']
                },
                'classes' : 'second_half'
            })
        
        for gene,modification in zip(reactData['geneList'],reactData['geneModifierType']):
            edges.append({
                'data' : {
                    'source' : gene,
                    'target' : f"mid_{reactionId}",
                    'classes' : modification,
                    'label' : "",
                    'reactInfo' : reactData['reactInfo']
                },
                'classes' : modification
            })
        
    finalNodes.extend(nodes)
    finalEdges.extend(edges)

    return

def readMapping(df, finalNodes, finalEdges,finalNodeSet,followers_node_di,followers_edges_di):

    transcriptionFactor = df['TF'].unique()
    targetGene = df['TargetGene'].unique()

    tfLen = len(transcriptionFactor)
    inc = (1/tfLen)*10
    st = 0
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
        yield str(st)
        st+=inc
    
    return str(st)

########################################################################################################

cyto.load_extra_layouts()
basePath = 'D:/Raylab/LiMeNEx/SBML_Network'

cache = diskcache.Cache("./cache")
long_callback_manager = DiskcacheLongCallbackManager(cache)

app = dash.Dash(__name__,long_callback_manager=long_callback_manager)
#########################################################################################################
@app.callback(
    Output('pathwayDropdownOptions', 'value'),
    Input('pathwayDropdownOptions', 'value')
)
def update_pathway_selection(selected_values):
    if selected_values and 'ALL' in selected_values:
        global pathwayDropdownOptions
        # Replace 'ALL' with the full list of pathway values
        all_pathway_values = list(pathwayDropdownOptions.values())
        return all_pathway_values
    return selected_values


@app.long_callback(
    Output('cytoscape', 'elements',allow_duplicate=True),
    Output('cytoscape','stylesheet', allow_duplicate=True),
    Output('followers-node-store','data'),
    Output('followers-edge-store','data'),
    Output('dataframe-store','data'),
    Input('fetchPathwaysButton','n_clicks'),
    State('pathwayDropdownOptions', 'value'),
    State('cytoscape','stylesheet'),
    running=[
        (
            Output("progress-container", "style"),
            {"display": "block","value" : '0','max' : '10',"position":"fixed","top":"0","left":"0","zIndex" : '1002', "width": "100vw", "height": "100vh",  "background": "rgba(0, 0, 0, 0.5)", "backdrop-filter": "blur(5px)"},
            {"display": "none"},
        )
    ],
    progress=[Output("progress-bar", "value"), Output("progress-bar", "max")],
    prevent_initial_call = True
)
def handlePathwaySelection(set_progress,n_clicks,optionList,stylesheet):
    if optionList is None:
        return [], stylesheet,{},{},{}

    if len(optionList) != 0:
        set_progress(('0','10'))

        followers_edges_di = {}
        followers_node_di = {}

        finalNodes = []
        finalEdges = []
        finalNodeSet = set()
        finalReactionList = []
        reactionNum = 1

        total_files = len(optionList)
        try:
            inc = 10/total_files
        except:
            set_progress(('10','10'))
        # init = 0

        dfList = []
        for i,fileName in enumerate(optionList):
            filePathSbml = os.path.join(basePath,'networkFile',f"{fileName}.xml")
            filePathTf = os.path.join(basePath,'pathwayTfs',f"{fileName}.csv")
            readSbml(filePath=filePathSbml,finalNodes=finalNodes,finalNodeSet=finalNodeSet,finalEdges=finalEdges, reactionNum=reactionNum)
            
            if os.path.exists(filePathTf):
                temp = pd.read_csv(filePathTf)
                dfList.append(temp)

        df = pd.DataFrame()

        if len(dfList) != 0:
            df = pd.concat(dfList, ignore_index=True)

            # adding display stylesheet for each tissue
            uniqueTissue = df['Tissue'].unique()
            for tis in uniqueTissue:
                stylesheet.extend([{
                    "selector" : f".{tis}_T",
                    "style" : {"display" : "element"}
                }])
            
            for progress in readMapping(df=df,finalNodes=finalNodes,finalEdges=finalEdges, finalNodeSet=finalNodeSet,followers_node_di=followers_node_di,followers_edges_di=followers_edges_di):
                set_progress((progress,'10'))

        # print(followers_edges_di)
        dataframe_json = df.to_json(orient='split')
        return finalNodes+finalEdges, stylesheet,followers_node_di,followers_edges_di,dataframe_json
    else:
        new_stylesheet = []
        for style in stylesheet:
            if 'T_' != style.get('selector')[-1:-3:-1]:
                new_stylesheet.append(style)

        return [], new_stylesheet,{},{},{}

@app.callback(
    Output("cytoscape", "stylesheet", allow_duplicate=True),
    Output("cytoscape", "elements", allow_duplicate=True),
    Output('hoverTooltip','style',allow_duplicate=True),
    Input("tfsButton", "n_clicks"),
    State("cytoscape", "elements"),
    State("cytoscape", 'stylesheet'),
    State("physiologicalDropdownOptions", "value"),
    State("tissueDropdownOptions", "value"),
    State("followers-node-store",'data'),
    State('followers-edge-store','data'),
    State('cytoscape','tapNodeData'),
    State('hoverTooltip','style'),
    prevent_initial_call=True,
)
def generateTfs(n_clicks, elements,stylesheet,physOptions,tisOptions, followers_node_di,followers_edges_di,nodeData,hoverStyle):

    # print(followers_edges_di)
    # print(json.dumps(elements,indent=2)
    if not nodeData:
        return stylesheet,elements,hoverStyle

    # Find the node in the elements list
    for element in elements:

        if nodeData["id"] == element.get("data").get("id"):
            # If the node is already expanded, remove its followers
            # print(nodeData)
            if element["data"].get("expanded"):
                return stylesheet,elements,hoverStyle
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
    
    hoverStyle['display'] = 'none'
    if ((tisOptions is None) or len(tisOptions) == 0) and (physOptions is None or len(physOptions) == 0):
        return stylesheet, elements,hoverStyle
    elif (tisOptions is not None) and len(tisOptions) != 0:
        
        return handleTissueSelection(tisOptions=tisOptions,stylesheet=stylesheet,phySystemOptions=physOptions,elements=elements),hoverStyle
    else:
        return handlePhysiologicalSelection(val=physOptions,stylesheet=stylesheet,elements=elements),hoverStyle
    

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
            # print(newClassFormat)
        else:
            newClassFormat = [firstClass] + notAllowed
        
        newClassFormat = " ".join(newClassFormat)

        # print(src,":",newClassFormat)
        newElements.append({
            'data' : ele.get("data"),
            'classes' : newClassFormat
        })
    # print(tfList)
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

        label = ele.get('data').get('label')

        if label in tfList:
            newClassFormat = [firstClass] + commonTissue
        else:
            newClassFormat = [firstClass] + notAllowed

        newClassFormat = " ".join(newClassFormat)

        # print(label," : ",newClassFormat)
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

        # print(json.dumps(basic_stylesheet,indent=2))

        allowedTissues = list(chain(*[psToTissue[sys] for sys in val]))
        allowedTissues = set([var+"_T" for var in allowedTissues])
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
    Output('hoverTooltip','style',allow_duplicate=True),
    Output('showProof', 'data'),
    Output('tooltip-text-content', 'children'),
    Output('tooltip-text-content', 'style'),
    Output('tfsButton','style'),
    Output('citationsButton','style'),
    Output('uniprotButton','style'),
    Output('citationsLink','href'),
    Input("cytoscape", "tapNodeData"),
    Input('cytoscape', 'tapEdgeData'),
    State('hoverTooltip','style'),
    State('tooltip-text-content','style'),
    State('dataframe-store','data'),
    State('cytoscape-mousemove-listener', 'event'),
    State('tfsButton','style'),
    State('citationsButton','style'),
    State('uniprotButton','style'),
    prevent_initial_call = True
)
def tapNodeAndEdge(nodeData,edgeData,hoverStyle,hoverTextStyle,dataframe_json,event,tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle):
    ctx = dash.callback_context

    if not ctx.triggered:
        hoverStyle['display'] = 'none'
        return hoverStyle, pd.DataFrame().to_dict('records'), "",hoverTextStyle,tfsButtonsStyle,citationButtonStyle, uniprotButtonStyle,""
    
    # print(ctx.triggered)
    triggered_id = ctx.triggered[0]['prop_id']

    if triggered_id == 'cytoscape.tapNodeData':
        
        classType1 = nodeData.get("classes")
        classType2 = nodeData.get("tissueClass")

        if classType1 is not None:
            classType = classType1.split(" ")[0]
        else:
            classType = classType2.split(" ")[0]

        if classType not in ["transcriptionFactorGene","enzymaticGene"]:
            return hoverStyle, pd.DataFrame().to_dict('records'), "",hoverTextStyle, tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle,""

        hoverTextStyle['display'] = 'none'
        hoverStyle['display'] = 'block'
        hoverStyle['top'] = f"{event['clientY']}px"
        hoverStyle['left'] = f"{event['clientX']}px"

        # print(nodeData)
        transNode = nodeData.get('tissueClass')
        if transNode:
            tfsButtonsStyle['display'] = 'none',
            citationButtonStyle['display'] = 'block'
            uniprotButtonStyle['display'] = 'block'

            return hoverStyle, pd.DataFrame().to_dict('records'), "",hoverTextStyle, tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle,"https://www.uniprot.org/uniprotkb/P53396/entry"
        else:
            tfsButtonsStyle['display'] = 'block',
            citationButtonStyle['display'] = 'none'
            uniprotButtonStyle['display'] = 'block'

            return hoverStyle, pd.DataFrame().to_dict('records'), "",hoverTextStyle, tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle,"https://www.uniprot.org/uniprotkb/P53396/entry"
    
    else:
        df = pd.read_json(io.StringIO(dataframe_json), orient='split')

        source = edgeData['source']
        target = edgeData['target']

        transEdge = edgeData.get("tissueClass")

        hoverStyle['display'] = 'block'
        hoverStyle['top'] = f"{event['clientY']}px"
        hoverStyle['left'] = f"{event['clientX']}px"

        hoverTextStyle['display'] = 'block'

        tfsButtonsStyle['display'] ='none'
        citationButtonStyle['display'] = 'none'
        uniprotButtonStyle['display'] = 'none'

        if transEdge:
            # print(source, target)
            mask = (df['TF'] == source) & (df['TargetGene'] == target)
            temp = df[mask]
            hoverTextStyle['display'] = 'none'
            # f"source: {edgeData['source']} to target: {edgeData['target']}"
            return hoverStyle, temp.to_dict('records'),"",hoverTextStyle, tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle,""
        else:
            reactType = edgeData.get("reactInfo")
            return hoverStyle,pd.DataFrame().to_dict('records'),f"Reaction Type {reactType}",hoverTextStyle,tfsButtonsStyle,citationButtonStyle,uniprotButtonStyle,""

@app.callback(
    Output('showProof','data',allow_duplicate=True),
    Input('citationsButton','n_clicks'),
    State('cytoscape','tapNodeData'),
    State('dataframe-store','data'),
    prevent_initial_call = True
)
def showTfsCitiations(n_clicks,nodeData,dataframe_json):

    if n_clicks is None:
        return pd.DataFrame().to_dict('records')
    else:
        label = nodeData.get('label')
        df = pd.read_json(io.StringIO(dataframe_json), orient='split')
        mask = (df['TF'] == label)
        temp = df[mask]
        
        return temp.to_dict('records')


@app.callback(
    Output('hoverTooltip','style', allow_duplicate=True),
    Input('close-tooltip', 'n_clicks'),
    State('hoverTooltip', 'style'),
    prevent_initial_call = True
)
def closeHover(n_clicks,style):
    if n_clicks is None:
        return style
    
    else:
        style['display'] = 'none'
        return style

    
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
    dcc.Store(id='followers-node-store'),
    dcc.Store(id='followers-edge-store'),
    dcc.Store(id='dataframe-store'),
    html.Div(
        children=[
            # First Row: Pathway Dropdown with Button
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='pathwayDropdownOptions',
                        options=[
                            {'label': 'All Pathways', 'value': 'ALL'},
                            *[{'label': key, 'value': pathwayDropdownOptions[key]} for key in pathwayDropdownOptions.keys()]
                        ],
                        multi=True,
                        maxHeight=300,
                        optionHeight=30,
                        placeholder="Select one or more pathways",
                        style={
                            'width': '100%',  # Adjust width to make space for the button
                            'marginRight': '10px'
                        }
                    ),
                    html.Button(
                        'Fetch Pathways',
                        id='fetchPathwaysButton',
                        n_clicks=0,
                        style={
                            'backgroundColor': '#fca117',
                            'color': 'white',
                            'border': 'none',
                            'borderRadius': '5px',
                            'padding': '5px',
                            'cursor': 'pointer',
                        }
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent' : 'space-between',
                    'width': '100%',
                    'marginBottom': '10px'  # Add spacing between rows
                }
            ),

            # Second Row: Physiological and Tissue Dropdowns
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='physiologicalDropdownOptions',
                        options=[
                            *[{'label': key, 'value': key} for key in physiologicalSystemOptions]
                        ],
                        multi=True,
                        maxHeight=300,
                        optionHeight=30,
                        placeholder="Select one or more physiological System",
                        style={
                            'width': '100%',
                            'marginRight': '10px'
                        }
                    ),
                    dcc.Dropdown(
                        id='tissueDropdownOptions',
                        options=[
                            {'label': 'Select Physiological System To View Tissues List', 'value': 'null'}
                        ],
                        multi=True,
                        maxHeight=300,
                        optionHeight=30,
                        placeholder="Select one or more Tissue",
                        style={
                            'width': '100%'
                        }
                    )
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'width': '100%',
                    'justifyContent' : 'space-between'
                }
            )
        ],
        style={
            'backgroundColor': '#292929',  # Set background color for entire container
            'padding': '10px',  # Add padding for aesthetics
            'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.3)',  # Add shadow effect
            'borderRadius': '5px',  # Rounded corners
            'display': 'flex',
            'flexDirection': 'column',  # Stack elements vertically
            'justifyContent': 'space-between'
        }
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
            'padding': "0.25em 0.25em",
            'backgroundColor': 'black',
            'color': 'white',
            'textAlign': 'center',
            'borderRadius': '0.25em',
            'whiteSpace': 'nowrap',
            'zIndex': '1001',
            'pointerEvents': 'auto',
            'maxWidth': '400px',  # Set a max width for the tooltip
            'maxHeight': '300px',  # Set a max height for the tooltip
            'overflow': 'hidden',  # Ensure overflow is hidden on the outer container
        },
        children=[
            html.Button('X', id='close-tooltip', n_clicks=0, style={
                'position': 'absolute',
                'top': '2px',
                'right': '2px',
                'background': 'transparent',
                'border': 'none',
                'color': 'red',
                'cursor': 'pointer',
                'fontSize': '12px',
                'lineHeight': '12px',
            }),
            # Tooltip Content Container
            html.Div(style={
                'marginTop': '0.8em',  # Adding top margin to separate from button
                'maxHeight': '250px',  # Max height for table container
                'overflowY': 'auto',   # Vertical scroll for table content
                'overflowX': 'auto',   # Horizontal scroll for table content
                'padding': '0.25em',    # Padding around the table
                'border': '1px solid #444',  # Add a border around table for separation
                'fontSize': '0.9em',
            },
                children=[
                    html.Div(id='tooltip-text-content', style={
                            'padding' : '0.2em',
                            'textAlign': 'left',
                            'color': 'white',
                            'backgroundColor': '#444',
                            'border': '1px solid #555',
                            'borderRadius': '0.25em',
                            'maxHeight': '80px',
                            'overflowY': 'auto',
                        },
                    ),
                    html.Div(
                        id = 'hoverButtons',
                        style={
                            'margin': '0.4em',
                            'display': 'flex',
                            'justifyContent': 'space-around',
                            'dispaly' : 'block'
                        },
                        children=[
                            html.A(
                                html.Button('Uniprot', id='uniprotButton', n_clicks=0, style={
                                    'backgroundColor': '#0052cc',
                                    'color': 'white',
                                    'border': 'none',
                                    'borderRadius': '0.25em',
                                    'padding': '0.5em 1em',
                                    'cursor': 'pointer',
                                    'margin' : '0 0.5em'
                                }),
                                href="",
                                target="_blank",
                                id="citationsLink"
                            ),
                            html.Button('Show TFs', id='tfsButton', n_clicks=0, style={
                                'backgroundColor': '#28a745',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '0.25em',
                                'padding': '0.5em 1em',
                                'cursor': 'pointer',
                                'margin' : '0 0.5em'
                            }),

                            html.Button('Citations', id='citationsButton', n_clicks=0, style={
                                'backgroundColor': '#dc3545',
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '0.25em',
                                'padding': '0.5em 1em',
                                'cursor': 'pointer',
                                'margin' : '0 0.5em'
                            }),
                        ]
                    ),
                    dash_table.DataTable(
                        id='showProof',
                        style_table={
                            'overflowX': 'auto',  # Ensure horizontal scrolling in the table
                        },
                        style_cell={
                            'minWidth': '100px', 'maxWidth': '200px', 'width': '150px',  # Set cell width constraints
                            'whiteSpace': 'normal',  # Allow cell content to wrap
                            'textAlign': 'left',  # Align text to the left
                            'backgroundColor': '#333',  # Background color for cells
                            'color': 'white'  # Text color
                        },
                        style_header={
                            'backgroundColor': 'black',  # Header background color
                            'color': 'white',  # Header text color
                            'fontWeight': 'bold'  # Bold font for headers
                        },
                        fixed_rows={'headers': True},  # Fix headers when scrolling vertically
                    )
                ]
            )
        ]
    ),
    html.Div(
        id='progress-container',
        style={'display': 'none'},
        children=[
            html.Progress(id='progress-bar',style = {'position': 'absolute','top' : '50%', 'left' : '30%','width' : '40%','height' : '15px'})
        ]
    ),
    # html.Div(id='background-blur', style={'display': 'none'})
    # html.Div(id="mouse-coordinates")
])



if __name__ == '__main__':
    app.run_server(debug=True, port = 6060)



    
