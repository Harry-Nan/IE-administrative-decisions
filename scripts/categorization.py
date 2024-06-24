"""
This file contains code to identify if a document is an administrative fine or administrative penalty.

USAGE:
from scripts.categorization import ... (see file)

output: differs. (see file)


"""
def isCategoryPrimair(list_of_pages, category='sanctie'):
    """
    args:
     - list_of_pages: a list of pages with text from a single document
     - category: either 'sanctie' or 'dwangsom'
     
    returns:
     - True if category-words are in list of pages
     - False if category-words are not in list of pages
    """
    # check for filter words
    filter_words = hasFilterWords(list_of_pages, category)
    if filter_words == False:
        return False
    
    # remove advices / revelation
    list_of_pages = removeAdviceRevelation(list_of_pages)
    if not list_of_pages:
        return False
    
    primair = isPrimair(list_of_pages)
    if primair == False:
        return False
    
    list_of_sentences = convertToSents(list_of_pages)
    
    legal_effect = identifyLegalEffect(list_of_sentences)
    
    if not legal_effect:
        return False
    
    return True, list_of_sentences, legal_effect
    

sanctiebesluit_all = ['besluit', 'boete']
sanctiebesluit_any = ['sanctiebesluit', 'boetebesluit']
dwangsom_all = ['last', 'dwangsom']
dwangsom_any = []

def hasFilterWords(list_of_pages, category='sanctie'):
    """
    args:
     - list_of_pages: a list of pages with text from a single document
     - category: either 'sanctie' or 'dwangsom'
     
    returns:
     - True if category-words are in list of pages
     - False if category-words are not in list of pages
    """
    for page_text in list_of_pages:
        
        # category = boetebesluit
        if category == 'sanctie':
            if all(phrase.lower() in page_text.lower() for phrase in sanctiebesluit_all):
                return True
            if any(phrase.lower() in page_text.lower() for phrase in sanctiebesluit_any):
                return True
           
        # category = last onder dwangsom
        elif category == 'dwangsom':
            if all(phrase.lower() in page_text.lower() for phrase in dwangsom_all):
                return True
            if any(phrase.lower() in page_text.lower() for phrase in dwangsom_any):
                return True
       
    # When no filter words have been detected
    return False
     

advies_text = ['adviescommissie bezwaarschriften', 'advies inzake']
openbarings_artikelen = ['artikel 3.1 van de wet open overheid', 'artikel 3.1 van de woo', 'artikel 8 van de wet openbaarheid van bestuur', 'artikel 8 van de wob']

def removeAdviceRevelation(list_of_pages):
    """
    args:
     - list_of_pages: a list of pages with text from a single document
     
    returns:
     - list_of_pages untill advice or revelation is found. None if empty.
    """
    for i, page_text in enumerate(list_of_pages):
        
        hasAny = False
        if all(phrase.lower() in page_text.lower() for phrase in advies_text):
            hasAny = True
        if any(phrase.lower() in page_text.lower() for phrase in openbarings_artikelen):
            hasAny = True
            
        # if advice or revelation is found, return list untill detected advice/revelation
        if hasAny == True:
            new_list = list_of_pages[:i]
            if new_list:
                return new_list
            else:
                return None
            
    # return it back fully if nothing is found    
    return list_of_pages       
            
from scripts.spacy_model import spacy_nlp
nlp = spacy_nlp()

def isPrimair(list_of_pages):
    """
    args:
     - list_of_pages: a list of pages with text from a single document
     
    returns:
     - isPrimair, True or False
    """
    isPrimair = False
    for page_text in list_of_pages:
        if 'zes weken' in page_text.lower():
            doc = nlp(page_text)
            for sent in doc.sents:
                if 'zes weken' in sent.text.lower():
                    if 'beroepschrift' in sent.text.lower():
                        return False
                    elif 'bezwaarschrift' in sent.text.lower():
                        isPrimair = True
    
    return isPrimair
            
def convertToSents(list_of_pages):
    list_of_sentences = []
    for page_text in list_of_pages:
        doc = nlp(page_text)
        sents = list(doc.sents)
        list_of_sentences.append(sents)
    return list_of_sentences

from scripts.money_matcher import money_matcher
from scripts.extract_fine_spacy import find_associated
money_matcher = money_matcher(nlp)
exclude_words = ['maximale', 'maximaal', 'basisboete', 'verhoogt', 'minimumboete', 'minimum', 'verhoogd']

def identifyLegalEffect(list_of_sentences):
    legal_effects = []
    idxs_boete = []
    for index_sentences, sentences in enumerate(list_of_sentences):
        idxs_boete_temp = []
        for index_sent, sent in enumerate(sentences):
            doc = nlp(str(sent))
            matches = money_matcher(doc)
            for match_id, start, end in matches:
                span = doc[start:end]
                fine_amount = span.text
                associated = find_associated(span, sent)
                # if 'boete' in str(associated):
                if 'boete' in str(associated):
                    if not any(exclude_word in word for word in str(associated) for exclude_word in exclude_words):
                        i_min = max(0, index_sent - 1)
                        i_max = min(len(sentences) - 1, index_sent + 1)
                        idxs_boete_temp.append([x for x in range(i_min, i_max + 1)])
                        legal_effects.append(fine_amount)
                        
                    # if decision is: no fine
            if 'geen boete' in str(sent).lower():
            #if 'geen boete' in str(sent).lower():
                fine_amount = 'geen_boete'
                i_min = max(0, index_sent - 1)
                i_max = min(len(sentences) - 1, index_sent + 1)
                idxs_boete_temp.append([x for x in range(i_min, i_max + 1)])
                legal_effects.append(fine_amount)

            # if decision is: warning
            if 'een waarschuwing' in str(sent).lower():
                fine_amount = 'een_waarschuwing'
                i_min = max(0, index_sent - 1)
                i_max = min(len(sentences) - 1, index_sent + 1)
                idxs_boete_temp.append([x for x in range(i_min, i_max + 1)])
                legal_effects.append(fine_amount)
                
        if idxs_boete_temp:
            flattened_list = [item for sublist in idxs_boete_temp for item in sublist]
            unique_list = sorted(list(set(flattened_list)))
            idxs_boete.append([index_sentences, unique_list])
            
    return legal_effects, idxs_boete

            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            