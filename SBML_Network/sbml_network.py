import xml.etree.ElementTree as ET

# Load and parse the XML file
tree = ET.parse('fattyacidsynthesis.xml')
root = tree.getroot()

# Namespaces used by CellDesigner
ns = {'celldesigner': 'http://www.sbml.org/2001/ns/celldesigner', '': 'http://www.sbml.org/sbml/level2/version4'}


genes = []
for gene in root.findall('.//celldesigner:gene', ns):
    genes.append(gene.get('name'))


# Extract species (nodes)
nodes = []
for species in root.findall('.//species',ns):
    # print(species)
    species_id = species.get('id')
    species_name = species.get('name')
    
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
        'classes' : 'Gene' if species_name in genes else 'Lipid' 
    }
    nodes.append(node)


# Extract reactions (edges)
edges = []
for reaction in root.findall('.//reaction', ns):
    reaction_id = reaction.get('id')

    # create a mid node for intersection
    tempNodeID = f"{reaction_id}_mid"
    node = {
        'data': {
            'id': tempNodeID,
        },
        'classes' : 'temp'
    }
    nodes.append(node)


    # Reactants to Products
    for reactant in reaction.findall('.//celldesigner:baseReactant', ns):
        source = reactant.get('species')
        edges.append({
            'data' : {'source':source, 'target':tempNodeID, 'label':reaction_id},
            'classes' : 'first_half'
        })

    for product in reaction.findall('.//celldesigner:baseProduct', ns):
        target = product.get('species')
        edges.append({
            'data' : {'source':tempNodeID, 'target':target, 'label':reaction_id},
            'classes' : 'second_half'
        })

    # Modifiers (e.g., enzymes) connected to reactions
    for modifier in reaction.findall('.//celldesigner:modification', ns):
        modifier_species = modifier.get('modifiers')
        edges.append({
            'data': {'source': modifier_species, 'target': tempNodeID, 'label': f"{reaction_id}"},
            'classes' : 'modify_edge'
        })

# print(nodes)
# print(edges)
# print(genes)
# Combine nodes and edges for Cytoscape
# elements = nodes + edges

##################################################################################################################
#example data
# ex_nodes = [
#     {
#         'data':{'id' : '1','label':'Gene1'},
#         'classes':'Gene'
#     },
#     {
#         'data':{'id' : '2','label':'Lipid1'},
#         'classes':'Lipid source'
#     },
#     {
#         'data':{'id' : '3','label':'Lipid2'},
#         'classes':'Lipid target'
#     },
#     {
#         'data':{'id' : '4','label':'Lipid1_Lipid2'},
#         'classes':'temp'
#     }
# ]

# ex_edges = [
#     {
#         'data' : {'source':'2', 'target':'4', 'label':'r1'},
#         'classes' : 'first_half'
#     },
#     {
#         'data' : {'source':'4', 'target':'3','label':''},
#         'classes' : 'second_half'
#     },
#     {
#         'data' : {'source':'1', 'target':'4', 'label':'modifies r1'},
#         'classes' : 'modify_edge'
#     }

# ]

####################################################################################################

ex_stylesheet = [
    # Style for Gene nodes
    {
        'selector': '.Gene',
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
    # Style for Lipid nodes
    {
        'selector': '.Lipid',
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
        'selector': '.modify_edge',
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
    }

]

########################################################################################################
import dash
from dash import dcc, html
import dash_cytoscape as cyto

app = dash.Dash(__name__)

elements = nodes + edges

app.layout = html.Div([
    cyto.Cytoscape(
        id='cytoscape',
        elements=elements,
        layout={'name': 'cose'},  # Choose a layout that suits your network
        style={'width': '100%', 'height': '600px'},
        stylesheet=ex_stylesheet
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
    
