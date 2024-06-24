"""
This file contains code to convert a list of pages to a list of sentences.

USAGE:
from scripts.text_to_sents import convertToSents
list_of_sentences = convertToSents(list_of_pages)

output: list of sentences

"""

from scripts.spacy_model import spacy_nlp
nlp = spacy_nlp()

def convertToSents(list_of_pages):
    list_of_sentences = []
    for page_text in list_of_pages:
        doc = nlp(page_text)
        sents = list(doc.sents)
        list_of_sentences.append(sents)
    return list_of_sentences
