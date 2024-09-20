import xml.etree.ElementTree as ET

# Load and parse the XML file
tree = ET.parse('fattyacidsynthesis_new_new.xml')
root = tree.getroot()

# Namespaces used by CellDesigner
ns = {'celldesigner': 'http://www.sbml.org/2001/ns/celldesigner', '': 'http://www.sbml.org/sbml/level2/version4',
      'html': 'http://www.w3.org/1999/xhtml'}


genes = []
for gene in root.findall('.//celldesigner:gene', ns):
    genes.append(gene.get('name'))


locus  = {}
for species in root.findall('.//celldesigner:speciesAlias',ns):
    species_id = species.get('species')

    coord = species.find('.//celldesigner:bounds',ns)
    coordVar = {'x' : float(coord.get('x')), 'y':float(coord.get('y'))}
    locus[species_id] = coordVar

# Extract species (nodes)
nodes = []
for species in root.findall('.//species',ns):
    # print(species)
    species_id = species.get('id')
    species_name = species.get('name')

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
            'id': species_id,
            'label': species_name,
            'catalyzes': catalyzed_reactions
        },
        'classes' : classVar,
        'position' : locus[species_id]
    }
    nodes.append(node)


# Extract reactions (edges)
edges = []
for reaction in root.findall('.//reaction', ns):
    reaction_id = reaction.get('id')
    reaction_type = reaction.find('.//celldesigner:reactionType', ns).text

    if reaction_type != 'TRANSCRIPTION':
        # create a mid node for intersection
        tempNodeID = f"{reaction_id}_mid"
        node = {
            'data': {
                'id': tempNodeID,
            },
            'classes' : 'temp'
        }

        isReversible = reaction.get('reversible')
        reactInfo = species.find('.//html:customInfo', ns)
        if reactInfo is not None:
            infoVar = reactInfo.get('info')
        else:
            infoVar = 'notAssignedInfo'

        #coord of temp node
        x = 0
        y=0
        totalNodes = 0

        # Reactants to Products
        for reactant in reaction.findall('.//celldesigner:baseReactant', ns):
            source = reactant.get('species')
            
            x+=locus[source]['x']
            y+=locus[source]['y']
            totalNodes+=1

            edges.append({
                'data' : {'source':source, 'target':tempNodeID, 'label':reaction_id,'info':infoVar,'id' : f"{source}_{tempNodeID}"},
                'classes' : 'first_half'
            })

        for product in reaction.findall('.//celldesigner:baseProduct', ns):
            target = product.get('species')

            x+=locus[target]['x']
            y+=locus[target]['y']
            totalNodes+=1

            edges.append({
                'data' : {'source':tempNodeID, 'target':target, 'label':reaction_id, 'info':infoVar},
                'classes' : 'second_half'
            })

        node['position'] = {'x':x/totalNodes, 'y':y/totalNodes}
        nodes.append(node)


        # Modifiers (e.g., enzymes) connected to reactions
        for modifier in reaction.findall('.//celldesigner:modification', ns):
            modifier_species = modifier.get('modifiers')
            modifierType = modifier.get('type')
            edges.append({
                'data': {'source': modifier_species, 'target': tempNodeID, 'label': f"{reaction_id}"},
                'classes' : modifierType
            })
    else:
        reactant = reaction.find('.//celldesigner:baseReactant', ns)
        source = reactant.get('species')

        product = reaction.find('.//celldesigner:baseProduct', ns)
        target = product.get('species')

        edges.append({
            'data': {'source': source, 'target': target, 'label': f"{reaction_id}"},
            'classes' : 'TRANSCRIPTION'
        })

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

app = dash.Dash(__name__)

elements = nodes + edges

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={'name': 'preset'},
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
        print(data)
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



    
