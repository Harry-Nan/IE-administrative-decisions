"""
This file contains code to find the date of a beschikking.

Download this: https://metatopos.dijkewijk.nl/metatopos-places.json

USAGE:
from scripts.extract_date import extract_date
extract_date(df)

output: list with indexes and list with dates

INFO:
extract datum:
- datum pattern
- (externe bron): nederlandse steden

stappen:
- datum in common prefix? -> datum
- datum op elke pagina (behalve eerste?) -> datum
- nederlandse stad (vlak) naast datum, of 'datum' (vlak) naast datum? -> datum

- Bij duplicaten: kies de meest recente (bijv., gerechtshoffen met datum bevatten vaak ook steden -> 'gerechtshof den haag 13 april 2018')

"""
import json
# Change the following:
location_of_json = "D:\\Documents\\UvA\\CITaDOG\\metatopos-places.json"

# Adding / removing cities:
extra_cities = ['‘s-Gravenhage', "'s-Gravenhage", "`s-Gravenhage", "s-Gravenhage", "Gravenhage", "sGravenhage", "-Gravenhage"]
remove_cities = ['Nederland', 'Een']

# Open the JSON file and load its contents into a dictionary
with open(location_of_json, 'r') as file:
    dutch_cities = json.load(file)

# Extract the list of places
dutch_cities = dutch_cities['places']
dutch_cities = [entry['place'] for entry in dutch_cities]
dutch_cities = [place for place in dutch_cities if all(substring not in place for substring in remove_cities)]
for city in extra_cities:
    dutch_cities.append(city)

# Extracting date

from datetime import datetime
import locale
import re

date_pattern = r'\b(?:\d{1,2}\s+(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)|(?:januari|februari|maart|april|mei|juni|juli|augustus|september|oktober|november|december)\s+\d{1,2})(?:\s+\d{4})?\b(?:,\s+\d{4})?|\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{1,2}-\d{1,2}-\d{4}\b|\b\d{1,2}\.\d{1,2}\.\d{4}\b'

def find_dates(text, pattern = date_pattern):
    found_dates = re.finditer(date_pattern, text, re.IGNORECASE)
    if found_dates:
        return found_dates
    return None

def format_date(date_string):
    date_string = date_string.replace(',', '').replace('.', '').strip()
    # Set the locale to Dutch
    locale.setlocale(locale.LC_TIME, 'nl_NL')
        
    date_formats = ['%d %B %Y', '%d/%m/%Y', '%B %d %Y', '%d-%m-%Y', '%d %B %Y', '%d %B %Y', '%d%m%Y']
    
    for fmt in date_formats:
        try:
            date_object = datetime.strptime(date_string, fmt)
            # Reset the locale
            locale.setlocale(locale.LC_TIME, '')
            
            formatted_date = date_object.strftime('%d/%m/%Y')
            return formatted_date
            
        except ValueError:
            continue
            
    return None

def extract_date(df):
    prefixes = ['common_prefix_0', 'common_prefix_1']
    indexes = []
    all_dates = []
    for index in df.index.unique():
        possible_dates = []

        # If date is written in common prefix
        for prefix in prefixes:
            for text in df.loc[index][prefix]:
                matches = find_dates(str(text))
                if matches:
                    for match in matches:
                        possible_dates.append(match.group(0))
                break

        if not possible_dates:
            dates_pages = []
            # If date is written on every page (skip first page)
            df2 = df.copy() # counter problems with loop
            for text in df2.loc[index]['cleaned_text'][1:]:
                matches = find_dates(text)
                if not matches:
                    dates_pages.append(['leeg'])
                else:
                    temp = []
                    for match in matches:
                        temp.append(match.group(0))
                    dates_pages.append(temp)
            if len(dates_pages) > 1:
                for date in set(dates_pages[0]):
                    present_in_all_lists = all(date in sublist for sublist in dates_pages)
                    if present_in_all_lists:
                        possible_dates.append(date)

        if not possible_dates:
            for text in df.loc[index]['cleaned_text']:
                matches = find_dates(text)
                if matches:
                    doc = nlp_lg(text)
                    dates = []
                    for match in matches:
                        start, end = match.start(), match.end()
                        merged_token = re.sub(r'\s+', '_', doc.text[start:end])  # Merge token
                        updated_text = doc.text[:start] + merged_token + doc.text[end:]  # Create updated text
                        doc = nlp_lg(updated_text)  # Create a new Doc object with updated text
                        dates.append(merged_token)
                    if dates:
                        for i, token in enumerate(doc):
                            if token.text.replace(',','').replace('.', '') in dates:
                                start_i = max(0, i-2)
                                end_i = min(len(doc), i+3)
                                surrounding_tokens = [doc[j] for j in range(start_i, end_i) if j != i]
                                #print(surrounding_tokens)
                                for temp in surrounding_tokens:
                                    #print(temp.text.replace(',', '').replace('.', ''))
                                    if temp.text.replace(',', '').replace('.', '') in dutch_cities:
                                        if not any("ECLI" in t.text or "LJN" in t.text for t in surrounding_tokens):
                                            #print(surrounding_tokens)
                                            #print(index, token.text.replace(',', '').replace('.', ''))
                                            possible_dates.append(token.text.replace(',', '').replace('.', '').replace('_', ' '))
                                    if temp.text.replace(',', '').replace('.', '').lower() in ['datum', 'datum:']:
                                        possible_dates.append(token.text.replace(',', '').replace('.', '').replace('_', ' '))

        # TODO: Skip first and last page when doing the second task

        indexes.append(index)
        #all_dates.append(possible_dates)
        possible_dates = list(set(possible_dates))
        
        for i, date in enumerate(possible_dates):
            if date:
                possible_dates[i] = format_date(date)
        if len(possible_dates) > 1:
            # Find the most recent date
            date_objects = [datetime.strptime(date, '%d/%m/%Y') for date in possible_dates if date is not None]
            if not date_objects:
                all_dates.append('unknown')
            else:
                most_recent_date = max(date_objects)
                most_recent_date = most_recent_date.strftime('%d/%m/%Y')
                all_dates.append(most_recent_date)
        else:
            if len(possible_dates) != 0:
                all_dates.append(possible_dates[0])
            else:
                all_dates.append('unknown')
    return indexes, all_dates

# Load in nlp model from spacy
import spacy
from spacy.tokenizer import Tokenizer
import re

# Load the spaCy model
nlp_lg = spacy.load("nl_core_news_lg")

# Define the custom prefix search pattern
custom_prefixes = [r'\bartikel\s+\d+[a-z]*\b']
prefix_regex = '|'.join(custom_prefixes)

# Define the custom tokenizer
tokenizer = Tokenizer(nlp_lg.vocab)
tokenizer.prefix_search = re.compile(f'({prefix_regex})').search

# Set the custom tokenizer to the spaCy pipeline
nlp_lg.tokenizer = tokenizer