import pandas as pd
import os
import networkx as nx

def read_csv_files_from_folder(folder_path):
    all_data = pd.DataFrame()
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            all_data = pd.concat([all_data,df], ignore_index=True)
    return all_data

# Example usage
csv_folder_path = 'data//uniprotID//'
combined_df = read_csv_files_from_folder(csv_folder_path)
# print(len(combined_df))


def update_graph_with_uniprot_ids(graph, df):
    # print(graph.nodes['Fatty Acids(ii)'])
    for node in list(graph.nodes):
        protein_name = node
        # print(protein_name)
        matching_row = df[df['Proteins'] == protein_name]
        # print(matching_row)
        if not matching_row.empty:
            uniprot_id = matching_row.iloc[0]['Uniprot ID']
            graph.nodes[node]['Uniprot_ID'] = uniprot_id
            # print(node)
    return graph

def process_gml_files(gml_folder_path, df):
    for filename in os.listdir(gml_folder_path):
        if filename.endswith('.gml'):
            file_path = os.path.join(gml_folder_path, filename)
            graph = nx.read_gml(file_path)
            updated_graph = update_graph_with_uniprot_ids(graph, df)
            nx.write_gml(updated_graph, os.path.join('data//gene_pathways_new//',filename))

# Example usage
gml_folder_path = 'data//gene_pathways_updated//'
process_gml_files(gml_folder_path, combined_df)
