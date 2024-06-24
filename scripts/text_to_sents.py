from scripts.spacy_model import spacy_nlp
nlp = spacy_nlp()

def convertToSents(list_of_pages):
    list_of_sentences = []
    for page_text in list_of_pages:
        doc = nlp(page_text)
        sents = list(doc.sents)
        list_of_sentences.append(sents)
    return list_of_sentences
