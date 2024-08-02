from bioservices import UniProt
import json

def get_uniprot_entry(uniprot_id):
    u = UniProt()
    
    if uniprot_id == "":
        return ""
    
    mapping = {
        "P" : "Biological Process",
        "F" : "Molecular Function",
        "C" : "Cellular Component"
    }
    try:
        # entry = u.retrieve(uniprot_id)
        dump = u.retrieve(uniprot_id, frmt="json", include="yes")
        # dump = json.loads(entry)
        save_to_file(dump,"full_info")

        info = {}       
        info["uniprotID"] = dump["primaryAccession"]

        info["geneName"] = dump["genes"][0]["geneName"]["value"]

        info["proteinName"] = dump["proteinDescription"]["recommendedName"]["fullName"]["value"]

        info["organismName"] = dump["organism"]["scientificName"]

        # Function
        for val in dump["comments"]:
            if(val["commentType"] == "FUNCTION"):
                info["function"] = val["texts"][0]["value"]


        # go annotations
        info["go"] = {
            "Biological Process" : [],
            "Molecular Function" : [],
            "Cellular Component" : []
        }
        for val in dump["uniProtKBCrossReferences"]:
            if(val["database"] == "GO"):
                for prop in val["properties"]:
                    if prop["key"] == "GoTerm":
                        term = prop["value"]
                        info["go"][mapping[term[:1]]].append(term[2:])        
        # print(info)
        save_to_file(info,"temp")
        return info
    except Exception as e:
        print("An error occurred:", e)
        return None

def save_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
