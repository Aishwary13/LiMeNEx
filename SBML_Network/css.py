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
            'font-size' : '10px',
            'z-index' : 1001
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
            # 'target-arrow-size' : '0.6rem',
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
            # 'target-arrow-size' : '0.6rem',
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
            # 'target-arrow-size' : '0.6rem',
            'line-color': 'black',
            'line-style' : 'dashed',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#000000',
        }
    },
]