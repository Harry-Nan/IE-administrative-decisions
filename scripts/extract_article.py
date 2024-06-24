"""
This file contains code to clean text by removing excessive spaces, removing ',-' and removing common prefixes. 

USAGE:
from scripts.clean_text import run_clean_text
run_clean_text(df)

output: df with 'cleaned_text' column.

note: only works if 'foi_bodyText' or 'foi_bodyTextOCR' exist.

"""

import re

pattern = r'\bartikel\s+\d+[a-z]*\b'

def find_articles(list_of_sentences, nlp, pattern=pattern, extra_index=100, gpt_context=100):
    
    legal_basis = ['overtre', 'overtra', 'bevoeg', 'als bedoeld in']
    words_re = re.compile("|".join(legal_basis))
    articles_idxs = []
    article_list = []
    
    for sentences_idx, sents in enumerate(list_of_sentences):
        sents_idxs = []
        # Find all law articles in the text, ignoring case
        for i, sent in enumerate(sents):
            matches = re.finditer(pattern, str(sent), re.IGNORECASE)
            for match in matches:
                article = ''
                start_index = match.start()
                max_index = min(start_index+extra_index, len(sent.text))
                new_text = sent.text[start_index:max_index]
                new_text = nlp(new_text)

                for j, t in enumerate(new_text):
                    if t.pos_ == 'VERB' or t.lemma_.lower() in ['zijn', 'luidt:', 'zaak:'] or t.text.lower() in [')', '(', 'een', 'met', 'door', '—']:
                        break
                    if 'artikel' in article.lower() and t.text.lower() == 'artikel':
                        break
                    end_idx = t.idx
                    article = article + ' ' + t.text
                article = article.strip()
                article_list.append(article)

                text = ''
                add_sents = []
                if match.start() == 0:
                    if i != 0:
                        text = str(sents[i-1].text[-extra_index:])
                        add_sents.append(i-1)
                if len(new_text) == j + 1:
                    if i != len(sents) - 1:
                        text = str((text + ' ' + sents[i+1].text[:extra_index])).strip()
                        add_sents.append(i+1)

                start_index = max(0, match.start()-extra_index)
                max_index = min(end_idx+extra_index, len(sent.text))
                more_text = sent.text[start_index:max_index]
                if text:
                    more_text = more_text + text
                if words_re.search(more_text):
                    sent_start_i = max(0, i-1)
                    sent_end_i = min(len(sents) - 1, i+1)
                    sents_idxs.append([x for x in range(sent_start_i, sent_end_i + 1)])
                    #sents_idxs.append([i])
                    if add_sents:
                        sents_idxs.append(add_sents)
        flattened_list = [item for sublist in sents_idxs for item in sublist]
        unique_list = sorted(list(set(flattened_list)))
        if unique_list: 
            articles_idxs.append([sentences_idx, unique_list])
            
    return article_list, articles_idxs