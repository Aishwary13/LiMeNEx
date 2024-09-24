import xml.etree.ElementTree as ET
import pandas as pd


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
    pathwayName = filePath.split('/')[-1][:-4]
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
                'pathway' : [pathwayName]
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
                'pathway' : [pathwayName]
            },
            'classes' : 'temp'
        }
        nodes.append(temp)

        for reactant in reactData['reactantList']:
            edges.append({
                'data' : {
                    'source' : reactant,
                    'target' :f"mid_{reactionId}",
                },
                'classes' : 'first_half'
            })
        
        for reactant in reactData['productList']:
            edges.append({
                'data' : {
                    'source' : f"mid_{reactionId}",
                    'target' : reactant,
                },
                'classes' : 'second_half'
            })
        
        for gene,modification in zip(reactData['geneList'],reactData['geneModifierType']):
            edges.append({
                'data' : {
                    'source' : gene,
                    'target' : f"mid_{reactionId}",
                },
                'classes' : modification
            })
        
    finalNodes.extend(nodes)
    finalEdges.extend(edges)

    return

def readMapping(filePath, finalNodes, finalEdges,finalNodeSet):
    df = pd.read_csv(filePath)

    transcriptionFactor = df['TF'].unique()
    targetGene = df['TargetGene'].unique()

    nodes = []
    edges = []
    for tf in transcriptionFactor:
        for tg in targetGene:

            mask = (df['TF'] == tf) & (df['TargetGene'] == tg)
            temp = df[mask]

            if temp.empty:
                continue
            
            if tf not in finalNodeSet:
                nodes.append({
                    'data' : {
                        'id' : tf,
                        'label' : tf,
                    },
                    'classes' : 'transcriptionFactorGene'
                })
            
            edges.append({
                'data' : {
                    'source' : tf,
                    'target' : tg
                },
                'classes' : 'TRANSCRIPTION'
            })
    finalNodes.extend(nodes)
    finalEdges.extend(edges)
    return nodes,edges

ex_stylesheet = [
    # Style for Gene nodes
    {
        'selector': '.transcriptionFactorGene',
        'style': {
            'shape': 'rectangle',
            'background-color': '#FF4136',
            'label': 'data(label)',
            'width': '40px',
            'height': '20px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    {
        'selector': '.enzymaticGene',
        'style': {
            'shape': 'rectangle',
            'background-color': 'green',
            'label': 'data(label)',
            'width': '40px',
            'height': '20px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    # Style for Lipid nodes
    {
        'selector': '.lipidMetabolite',
        'style': {
            'shape': 'ellipse',
            'background-color': '#0074D9',
            'label': 'data(label)',
            'width': '100px',
            'height': '40px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    {
        'selector': '.nonLipidSubstrate',
        'style': {
            'shape': 'ellipse',
            'background-color': 'orange',
            'label': 'data(label)',
            'width': '100px',
            'height': '40px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    {
        'selector': '.nonLipidMetabolite',
        'style': {
            'shape': 'ellipse',
            'background-color': 'pink',
            'label': 'data(label)',
            'width': '100px',
            'height': '40px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    {
        'selector': '.lipidSubstrate',
        'style': {
            'shape': 'ellipse',
            'background-color': 'red',
            'label': 'data(label)',
            'width': '100px',
            'height': '40px',
            'color': '#FFFFFF',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size' : '10px'
        }
    },
    # Style for Temp nodes
    {
        'selector': '.temp',
        'style': {
            'shape': 'rectangle',
            'background-color': 'white',  # Set the background color to white
            'border-width': '1px',        # Define the width of the border
            'border-color': 'black',      # Set the border color to black
            'width': '10px',
            'height': '10px',
            'color': '#000000',            # Set the text color to black
            'text-valign': 'center',
            'text-halign': 'center',
        }
    },
    # Style for edges
    {
        'selector': '.second_half',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#000000',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
            'line-color' : '#000000'
        }
    },
    {
        'selector': '.first_half',
        'style': {
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
            'line-color' : '#000000'
        }
    },
    {
        'selector': '.CATALYSIS',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'circle',
            'target-arrow-color': 'black',    # Set the border color of the circle
            'target-arrow-fill': 'hollow',
            'target-arrow-size' : '0.6rem',
            'line-color': '#9D9D9D',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
        }
    },
    {
        'selector': '.PHYSICAL_STIMULATION',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': 'blue',    # Set the border color of the circle
            'target-arrow-fill': 'hollow',
            'target-arrow-size' : '0.6rem',
            'line-color': 'blue',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
        }
    },
    {
        'selector': '.TRANSCRIPTION',
        'style': {
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': 'black',    # Set the border color of the circle
            'target-arrow-fill': 'hollow',
            'target-arrow-size' : '0.6rem',
            'line-color': 'black',
            'line-style' : 'dashed',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
        }
    }

]

########################################################################################################
import dash
from dash import dcc, html, Input, Output, State
import dash_cytoscape as cyto
import json
import os

app = dash.Dash(__name__)

cyto.load_extra_layouts()
basePath = 'D:/Raylab/LiMeNEx/SBML_Network'

# readSbml('D:/Raylab/LiMeNEx/SBML_Network/networkFile/betaOxidationFattyAcid.xml')
# readSbml('D:/Raylab/LiMeNEx/SBML_Network/networkFile/fattyAcidSynthesis.xml')
# readMapping('D:/Raylab/LiMeNEx/SBML_Network/data/fattyAcidSynthesis.csv')

#########################################################################################################

@app.callback(
    Output('cytoscape', 'elements'),
    Input('pathwayDropdownOptions', 'value'),
)
def handlePathwaySelection(optionList):
    if optionList is not None:
        finalNodes = []
        finalEdges = []
        finalNodeSet = set()
        finalReactionList = []
        reactionNum = 1

        for fileName in optionList:
            filePath = os.path.join(basePath,'networkFile',f"{fileName}.xml")

            readSbml(filePath=filePath,finalNodes=finalNodes,finalNodeSet=finalNodeSet,finalEdges=finalEdges, reactionNum=reactionNum)

        return finalNodes+finalEdges
    
    return []

###########################################################################################################
with open("D:/Raylab/LiMeNEx/SBML_Network/pathwayDropdownOptions.json", 'r') as file:
    # Load the JSON data
    pathwayDropdownOptions = json.load(file)

# elements = finalNodes + finalEdges

app.layout = html.Div([
    dcc.Dropdown(
        id = 'pathwayDropdownOptions',
        options=[
            {'label' : 'All Pathways', 'value' : 'ALL'},
            *[{'label': key, 'value': pathwayDropdownOptions[key]} for key in pathwayDropdownOptions.keys()]
        ],
        multi= True,
        maxHeight=300,
        optionHeight=30
    ),
    cyto.Cytoscape(
        id='cytoscape',
        elements=[],
        layout={'name': 'cose-bilkent'},  #dagre, cose-bilkent, 
        style={'width': '100%', 'height': '600px'},
        boxSelectionEnabled = True,
        stylesheet=ex_stylesheet
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
        'zIndex': '1000',
        'pointerEvents': 'none'
    }),
    dcc.Store(id='mouse-coordinates')
])

@app.callback(
    Output('hoverTooltip', 'style'),
    Output('hoverTooltip', 'children'),
    Input('cytoscape', 'mouseoverEdgeData'),
    State('hoverTooltip', 'style'),
)
def display_hover(data,style):
    if data:
        print(json.dumps(data,indent=2))
        style['display'] = 'none'
        return style, f"source: {data['source']} to target: {data['target']}"
    else:
        style['display'] = 'none'
        return style, ''

app.clientside_callback(
    """
    function() {
        var cyto = document.getElementById('cytoscape');
        var tooltip = document.getElementById('hoverTooltip');

        console.log("Here1")
        var temp = document.getElementById('s30_re16_mid')
        if(temp){
            console.log("Here2")
        }

        if (cyto && tooltip) {
            cyto.addEventListener('mousemove', function(event) {
                tooltip.style.top = event.pageY + 10 + 'px';
                tooltip.style.left = event.pageX + 10 + 'px';
            });

            cyto.addEventListener('mouseout', function(event) {
                if (event.target === cyto) {
                    tooltip.style.display = 'none';
                }
            });
        }
    }
    """,
    Output('mouse-coordinates', 'data'),
    Input('cytoscape', 'mouseoverEdgeData')
)

if __name__ == '__main__':
    app.run_server(debug=True, port = 6060)



    
