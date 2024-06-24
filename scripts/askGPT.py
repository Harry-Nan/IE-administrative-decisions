"""
This file contains code to clean text by removing excessive spaces, removing ',-' and removing common prefixes. 

USAGE:
from scripts.clean_text import run_clean_text
run_clean_text(df)

output: df with 'cleaned_text' column.

note: only works if 'foi_bodyText' or 'foi_bodyTextOCR' exist.

"""

boete_prompt = "De gegeven lijst met zinnen komen uit een enkel sanctiebesluit waarbij ontvanger(s) een artikel heeft/hebben overtreden. Extract uit de lijst met zinnen per ontvanger eenmalig de juiste values voor deze keys in de volgende structuur: 'boete': [{'effect':<hoogte (getal) van opgelegde gekregen boete. Als er besloten wordt om geen bedrag als boete op te leggen, geef dan weer of er een 'waarschuwing' of '0' wordt gegeven. Geen maximale, hypothetische, basisboetes of boetes in het verleden.>, 'ontvanger':<(rechts)persoon die boete/waarschuwing ontvangt, zo volledig mogelijk>, 'overtreden_artikel':<[Welke artikelen worden besproken of deze zijn overtreden. Geef elk artikel zo weer:  artikel + nummer + evt. aanhef + wet]>}], 'type_of_activity': <Wat er is gebeurd waardoor de wet/het artikel is overtreden>, 'dma': <Decision making authority; het bestuursorgaan dat bevoegd is om boete op te leggen>, 'legal_basis': <op basis van welk artikel de dma bevoegd is om een boete op te leggen. Geef het artikel weer als: artikel + nummer + evt. aanhef + wet.>. Geef je antwoord in json-formaat."


from openai import OpenAI
client = OpenAI()

def askGPT(candidate_sentences, category='sanctie', model="gpt-3.5-turbo-0125"):
    if category == 'sanctie':
        prompt = boete_prompt
    if category == 'dwangsom':
        prompt = dwangsom_prompt
        
    full_prompt = prompt + ' Zinnen: ' + str(candidate_sentences)
    messages = [{"role": "user", "content": full_prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response


import json

# Helper function
def ensure_three_boetes(json_data):
    # Ensure each boete has the keys 'effect', 'ontvanger', and 'overtreden_artikel'
    for boete in json_data["boete"]:
        if 'effect' not in boete:
            boete['effect'] = 'None'
        if 'ontvanger' not in boete:
            boete['ontvanger'] = 'None'
        if 'overtreden_artikel' not in boete:
            boete['overtreden_artikel'] = 'None'
            
    return json_data

import pandas as pd

def extractInformation(response):
    json_data = response.choices[0].message.content
    json_data = json.loads(json_data)
    json_data = ensure_three_boetes(json_data)

    data = []
    effect = [entry['effect'] for entry in json_data['boete']]
    ontvanger = [entry['ontvanger'] for entry in json_data['boete']]
    artikel = [entry['overtreden_artikel'] for entry in json_data['boete']]
    activity = json_data['type_of_activity']
    dma = json_data['dma']
    legal_basis = json_data['legal_basis']

    data.append({
            'legal effect': effect,
            'ontvanger': ontvanger,
            'overtreden_artikel': artikel,
            'type of activity': activity,
            'dma': dma,
            'legal basis': legal_basis
        })

    df = pd.DataFrame(data)
    
    return df
    
