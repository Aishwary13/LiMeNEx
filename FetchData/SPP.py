import pandas as pd

targetGenedf = pd.read_excel('D:/Raylab/LiMeNEx/FetchData/data/ACSS2.xls')
targetGenedf.columns = targetGenedf.iloc[1]
targetGenedf = targetGenedf.iloc[2:]

finaldf = pd.DataFrame(columns=['Database','TF','TargetGene','Tissue','Experiment'])


mapping = pd.read_csv('D:/Raylab/LiMeNEx/FetchData/Physiologicalsystem.csv')

for i in range(0,len(targetGenedf)):

    experi = targetGenedf.iloc[i]['Experiment Name']
    tissue = targetGenedf.iloc[i]['Tissue']
    targetGene = targetGenedf.iloc[i]['Symbol']
    
    Tf = targetGenedf.iloc[i]['IPAGS|BSM|Other AGS'].split('|')
    
    mask = mapping['Types'] == tissue
    temp = mapping[mask]

    #handling Immune tissue case 
    Immunetissue = tissue.split(', ')[1] if ',' in tissue else tissue

    mask2 = mapping['Types'] == Immunetissue
    temp2 = mapping[mask2]

    if(len(temp2) != 0):
        tissue = Immunetissue
        temp = temp2

    if(len(temp) == 0):
        print("New Tissue Type Detected! -> ",tissue)
        print('----------------------')

        print('Type system:')
        system = input()

        print('Type Tissue:')
        newtissue = input()

        print('newtissueType')
        newtissuetype = input()

        new_row = {'Physiological System':system, 'Tissue':newtissue, 'Types':newtissuetype}
        mapping = pd.concat([mapping, pd.DataFrame([new_row])],ignore_index = True)

        mapping.to_csv("D:/Raylab/LiMeNEx/FetchData/Physiologicalsystem.csv", index = False)
    
    mask = mapping['Types'] == tissue
    temp = mapping[mask]

    for tf in Tf:
        # Check if the combination of TF and target gene already exists
        existing_row = finaldf[(finaldf['TF'] == tf) & (finaldf['TargetGene'] == targetGene) & (finaldf['Tissue'] == temp.iloc[0]['Tissue'])]
        
        if not existing_row.empty:
            # Append the new experiment to the existing row's Experiment column
            existing_index = existing_row.index[0]
            finaldf.at[existing_index, 'Experiment'] += f", {experi}"
        else:
            # Add new row if it doesn't exist
            new_row = {'Database': 'SPP', 'TF': tf, 'TargetGene': targetGene, 'Tissue': temp.iloc[0]['Tissue'], 'Experiment': experi}
            finaldf = pd.concat([finaldf, pd.DataFrame([new_row])], ignore_index=True)


finaldf.to_csv(f"D:/Raylab/LiMeNEx/FetchData/data/{targetGene}_modified.csv")
