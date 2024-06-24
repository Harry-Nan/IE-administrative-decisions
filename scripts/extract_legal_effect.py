from scripts.spacy_model import spacy_nlp
nlp = spacy_nlp()

from scripts.money_matcher import money_matcher
money_matcher = money_matcher(nlp)

exclude_words = ['maximale', 'maximaal', 'basisboete', 'verhoogt', 'minimumboete', 'minimum', 'verhoogd']

def find_associated(span, doc):
    
    def process_noun(token):
        # If head of token is 'bedrag' or oblique nominal (does not give much extra information)
        if token.text.lower() == 'bedrag' or token.dep_ == 'obl':
            # Add head of 'bedrag' to give extra information (such as: 'bedrag' + 'afgesloten')
            noun.append(token.text + ' ' + token.head.text)

            for child in token.head.children:
                if child.dep_ in ['nsubj', 'nsubj:pass'] and child.text not in span.text:
                    for child2 in child.children:
                        if child2.dep_ == 'acl':
                            temp_noun = child2.text + ' ' + child.text
                            for child3 in child2.children:
                                if child3.dep_ == 'advmod':
                                    temp_noun = child3.text + ' ' + temp_noun
                            noun.append(temp_noun)
                        else:
                            noun.append(child.text + ' ' + token.text)

        # If no other conditions apply, add the head as the noun
        else:
            temp_noun = token.text

            # Check for extra information (such as 'maximaal')
            for child in token.children:
                if child.dep_ in ['acl']:
                    for child2 in child.children:
                        if child2.dep_ in ['amod', 'advmod']:
                            temp_noun = child2.text + ' ' + child.text + ' ' + temp_noun
                        
                if child.dep_ in ['amod', 'advmod']:
                    temp_noun = child.text + ' ' + temp_noun
            noun.append(temp_noun)

    def process_verb(token):
        for child in token.children:
            # If the verb is related to something in the form of a nominal subject (active or passive):
            if child.dep_ in ['nsubj', 'nsubj:pass'] and child.text not in span.text:

                # 
                if child.pos_ == 'NOUN':
                    for child2 in child.children:
                        if child2.dep_ == 'acl':
                            temp_noun = child.text + ' ' + token.text
                            for child3 in child2.children:
                                if child3.dep_ == 'advmod':
                                    temp_noun = child3.text + ' ' + temp_noun
                            noun.append(temp_noun)
                        else:
                            noun.append(child.text + ' ' + token.text)

                else:
                    noun.append(child.text + ' ' + token.text)

            # If the verb is related to something in the form of an object
            if child.dep_ == 'obj' and child.text not in span.text:
                if child.pos_ == 'NOUN':
                    temp_noun = child.text
                    for child2 in child.children:
                        if child2.dep_ in ['amod', 'advmod']:
                            temp_noun = child2.text + ' ' + temp_noun
                    noun.append(temp_noun)
                else:
                    noun.append(child.text)

        # If no noun is found:
        if not noun:
            #TODO
            noun.append('#TODO')
    
    noun = []

    # Go up the tree untill a noun or verb is found
    for token in span:
        head_token = token.head
        while head_token.pos_ != "VERB" and head_token.pos_ != "NOUN" and head_token.head != head_token:
            head_token = head_token.head
        
        # If head of token is noun:
        if head_token.pos_ == 'NOUN' and head_token.text not in span.text:
            process_noun(head_token)

        # If head of token is verb:
        elif head_token.pos_ == 'VERB' and head_token.text not in span.text:
            process_verb(head_token)
                        
    #print(f'output:', span.text, set(noun))
    return set(noun)

def extract_legal_effect(list_of_sentences):
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
