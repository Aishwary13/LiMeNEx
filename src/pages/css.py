sigUp = [
        {"selector": ".sigUp",
            "style": {
                "opacity": 1,
                "height": 30,
                "width": 30,
                "background-color": "#f53636",
                "label" :  "data(label)",
                "font-size" : "15px"
            }
        }
    ]

sigDown = [
    {"selector": ".sigDown",
        "style": {
            "opacity": 1,
            "height": 30,
            "width": 30,
            "background-color": "#0a85ff",
            "label" :  "data(label)",
            "font-size" : "15px"
        }
    }
]

hideGrid = [
    {"selector": ".circle", 
        "style": {"shape": "ellipse", 
                "width": 50,
                "height": 50, 
                "opacity": 0.5, 
                "background-color": "#ffffff"}
    }
]

highlightLipid = [
    {"selector": ".Lipid",
        "style": {
            "opacity": 1,
            "height": 30,
            "width": 30,
            "background-color": "#CE5A67",
            "label" :  "data(label)",
            "font-size" : "15px"
        }
    }
]

highlightGene = [
    {
        "selector": '.gene',
        "style": {
            "opacity": 1,
            "height": 30,
            "width": 30,
            "background-color": "#CE5A67",
            "label" :  "data(label)",
            "font-size" : "15px"
        }
    }
]

default_stylesheet = [
        {
            "selector": "node",
            "style": {
                "opacity": 1,
                "height": 200,
                "width": 200,
                "background-color": "#CE5A67",
                "label" :  "data(label)",
                "font-size" : "50px",
                "color" : "#ffffff"
            },
        },
        {
            "selector" : ".Lipid",
            "style" : {
                "height" : 300,
                "width" : 300,
                "background-color": "red",
            }
        },
        {"selector": ".circle", "style": {"shape": "ellipse",  "width": 100, "height": 100, "opacity": 0.5, "background-color": "#ffffff"}},
        {
            "selector": "edge",
            "style": {
                "width": 25,  # Set the width of edges
                "line-color": "#ffffff",  # Set the color of edges
                "line-style": "solid",  # Set the style of edges (solid, dotted, dashed, etc.)
                "curve-style": "bezier",  # Set the curve style of edges
            }
        },
        {"selector": "edge[directed]",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",  # Add an arrow to indicate direction
                "target-arrow-color": "#ffffff",  # Arrow color
                "size" : 4
            },
        }
    ]

default_stylesheet2 = [
        {
            "selector": "node",
            "style": {
                "opacity": 1,
                "height": 30,
                "width": 30,
                "background-color": "#F4BF96",
                "label" :  "data(label)",
                "font-size" : "15px",
                "color" : "#ffffff"
            },
        },
        {
            "selector": "edge",
            "style": {
                "width": 4,  # Set the width of edges
                "line-color": "#ffffff",  # Set the color of edges
                "line-style": "solid",  # Set the style of edges (solid, dotted, dashed, etc.)
                "curve-style": "bezier",  # Set the curve style of edges
                "opacity" : 0.6,
                "target-arrow-shape": "triangle",  
                "target-arrow-color": "#ffffff"
            }
        },
        {"selector": "edge[directed]",
            "style": {
                "curve-style": "bezier",
                "target-arrow-shape": "triangle",  # Add an arrow to indicate direction
                "target-arrow-color": "#ffffff",  # Arrow color
                "size" : 2
            },
        }
    ]