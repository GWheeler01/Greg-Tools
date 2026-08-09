import requests
import json

### One-touch script to query ChEMBL for all small-molecule cancer drugs and write out the relevant data to a JSON. No configuration needed. ###

def fetch_molecules(limit:int=1000):
    # Base URL for ChEMBL molecule resource
    url = "https://www.ebi.ac.uk/chembl/api/data/molecule.json"
    
    # Query parameters using the accepted molecule_atc_code filter
    params = {
        "max_phase": 4,                    # Approved drugs
        "molecule_atc_code__startswith": "L01", # ATC L01 = Antineoplastic agents
        "limit": limit
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Python script)",
        "Accept": "application/json"
    }

    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"HTTP Error {response.status_code}: {response.text[:200]}")
        return []

    data = response.json()
    molecules = data.get('molecules', [])
    return molecules

# Run query
molecules = fetch_molecules()

def get_cancer_drugs(molecules:list):
    cancer_drugs = []
    for mol in molecules:
        pref_name = mol.get('pref_name')
        chem_structs = mol.get('molecule_structures')
        if chem_structs is None:
            continue
        elif 'canonical_smiles' not in chem_structs:
            continue
        else:
            smiles = chem_structs['canonical_smiles']

        atc_codes = mol['atc_classifications']
            
        # Verify it has a valid canonical SMILES and an explicit L01 ATC classification
        if any(code.startswith('L01') for code in atc_codes):
            cancer_drugs.append({
                'chembl_id': mol.get('molecule_chembl_id'),
                'name': pref_name,
                'atc_codes': ";".join(atc_codes),
                'smiles': smiles,
                'approval': mol['first_approval']
            })
    
    return cancer_drugs

molecules = fetch_molecules(100000)
cancer_drugs = get_cancer_drugs(molecules)

with open('cancer_drugs.json','w') as cancer_drugs_out:
    cancer_drugs_out.write(json.dumps(cancer_drugs, indent=2))