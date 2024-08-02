import networkx as nx
import os

def read_gml(file_path):
    """Read a graph from a GML file."""
    return nx.read_gml(file_path)

def common_nodes(graph1, graph2):
    """Find common nodes between two graphs."""
    return set(graph1.nodes) & set(graph2.nodes)

def find_common_nodes_in_folder(folder_path):
    """Find common nodes among pairs of graphs in a folder."""
    files = os.listdir(folder_path)
    files = [file for file in files if file.endswith(".gml")]

    graphs = [read_gml(os.path.join(folder_path, file)) for file in files]

    common_nodes_list = []

    for i in range(len(graphs)):
        for j in range(i+1, len(graphs)):
            common_nodes_set = common_nodes(graphs[i], graphs[j])
            common_nodes_list.append((files[i], files[j], common_nodes_set))

    return common_nodes_list

folder_path = "NewNetwork\data"
result = find_common_nodes_in_folder(folder_path)

for file1, file2, common_nodes_set in result:
    print(f"Common nodes between {file1} and {file2}: {common_nodes_set}")
