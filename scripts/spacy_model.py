"""
This file contains code to load the spacy model used throughout this project.

USAGE:
from scripts.spacy_model import spacy_nlp
nlp = spacy_nlp()

output: spacy model

"""
# Load in nlp model from spacy
import spacy
from spacy.tokenizer import Tokenizer
import re

def spacy_nlp():
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
    print('Successfully loaded nlp-model.')
    return nlp_lg