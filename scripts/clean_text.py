"""
This file contains code to clean text by removing excessive spaces, removing ',-' and removing common prefixes. 

USAGE:
from scripts.clean_text import run_clean_text
run_clean_text(df)

output: df with 'cleaned_text' column.

note: only works if 'foi_bodyText' or 'foi_bodyTextOCR' exist.

"""
import re
import os
import numpy as np

# Function to run full code
def run_clean_text(df):
    df = drop_no_text(df)
    df = add_clean_text_column(df)
    df = remove_common_prefixes(df)
    return df

# Drop rows without text
def drop_no_text(df):
    text_columns = ['foi_bodyText', 'foi_bodyTextOCR']
    return df.dropna(subset=text_columns, how='all')

# Add clean_text column to df
def add_clean_text_column(df):
    
    def clean_text(text):
        cleaned_text = re.sub(r'\s+', ' ', text) # Removes excessive spacing
        cleaned_text = cleaned_text.strip() # Removes leading and trailing spaces
        cleaned_text = cleaned_text.replace(',-', '') # Removes ',-' (performance)
        cleaned_text = cleaned_text.replace('|', '')
        cleaned_text = cleaned_text.replace(';', '.')
        cleaned_text = re.sub(r'^[\d\W_]+', '', cleaned_text) # Removes numbers and punctuations at start
        return cleaned_text
    
    # Define the function to clean text on df row
    def apply_clean_text(row):
        # If bodyText exists
        if row['foi_bodyText'] and isinstance(row['foi_bodyText'], str):
            return clean_text(row['foi_bodyText'])
        # If bodyTextOCR exists
        elif row['foi_bodyTextOCR'] and isinstance(row['foi_bodyTextOCR'], str):
            return clean_text(row['foi_bodyTextOCR'])
        else:
            return np.nan
    
    # Add 'cleaned_text' column
    df.loc[:, 'cleaned_text'] = df.apply(apply_clean_text, axis=1)
    return df

# Remove common start prefixes (for all pages and all pages except first page)
# Requires 'cleaned_text' column
def remove_common_prefixes(df):    

    def get_common_prefix(df, skip_pages):
        common_prefixes = dict()
        grouped_df = df.groupby(df.index)
        
        for index, document in grouped_df:
            document_clean = document['cleaned_text']
            cleaned_texts = document_clean[document_clean != ""] # Removes empty strings

            # Save common prefix in dictionary
            cleaned_texts_dossier = cleaned_texts.tolist()
            for text in cleaned_texts_dossier:
                if len(cleaned_texts_dossier[skip_pages:]) > 1:
                    common_prefix = os.path.commonprefix(cleaned_texts_dossier[skip_pages:])
                    common_prefixes[index] = common_prefix
                
        return common_prefixes
     
    def remove_common_prefix(row, common_prefixes, skip_pages=0):
        common_prefix = common_prefixes.get(row.name, None)
        if common_prefix and row['foi_pageNumber'] > skip_pages:
            return row['cleaned_text'][len(common_prefix):]
        else:
            return row['cleaned_text']
        
    # Define a function to remove numbers and punctuations at the start of a string
    def remove_starting_numbers_and_punctuation(text):
        return re.sub(r'^[\d\W_]+', '', text)
    
    for i in range(2):
        common_prefixes = get_common_prefix(df, i)
        df.loc[:, f'common_prefix_{i}'] = df.index.map(common_prefixes)
        df.loc[:, 'cleaned_text'] = df.apply(remove_common_prefix, args=(common_prefixes, i), axis=1)
        df.loc[:, 'cleaned_text'] = df['cleaned_text'].apply(remove_starting_numbers_and_punctuation)
    
    return df