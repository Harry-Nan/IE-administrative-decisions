"""
This file extracts sentences from documents based on idxs from extracted identified legal effects, violated articles and legal basis.

USAGE:
from scripts.candidateSentences import selectCandidateSentences
selectCandidateSentences(legal_effect_idx, articles_idxs, list_of_sentences)

output: list of sentences

"""

def selectCandidateSentences(legal_effect_idxs, articles_idxs, list_of_sents):
    sentences_list = []
    LE_sents = [item[0] for item in legal_effect_idxs]
    AR_sents = [item[0] for item in articles_idxs]
    sents = list(sorted(set(LE_sents + AR_sents)))
    for i in sents:
        legal_effect_sents = []
        article_sents = []
        if i in [item[0] for item in legal_effect_idxs]:
            legal_effect_sents = [item[1] for item in legal_effect_idxs if item[0] == i][0]
        if i in [item[0] for item in articles_idxs]:
            article_sents = [item[1] for item in articles_idxs if item[0] == i][0]
        if article_sents and legal_effect_sents:
            all_sents = []
            all_sents.append(legal_effect_sents + article_sents)
            flattened_list = [item for sublist in all_sents for item in sublist]
            unique_list = sorted(list(set(flattened_list)))
        elif article_sents:
            unique_list = article_sents
        elif legal_effect_sents:
            unique_list = legal_effect_sents
        else:
            unique_list = []
        sentences = []
        if unique_list:
            temp = []
            for idx in unique_list:
                sentence = str(list_of_sents[i][idx])
                more_context = ['dit is een overtreding van', 'dat is een overtreding van', 'hiermee is']
                if any(context in sentence.lower() for context in more_context):
                    if str(row['sents'][idx-1]):
                        temp.append(idx-1)
                        sentences.append(str(list_of_sents[i][idx-1]))
                temp.append(idx)
                sentences.append(str(list_of_sents[i][idx]))
                    
        if sentences:
            sentences = ' '.join(sentences)
            sentences_list.append(sentences)

    return sentences_list