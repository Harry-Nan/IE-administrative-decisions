# Combining rule-based and machine learning methods for effective information extraction on administrative decisions  

This is the GitHub page for the project for [CITaDOG](https://www.tilburguniversity.edu/about/digital-sciences-society/projects/case-inclusive-transparency) from Tilburg University regarding information extraction on administrative decisions. The paper has been written in conjunction with the University of Amsterdam, Faculty of Science. 

This project applies a combination of rule-based methods with machine learning methods to achieve effective information extraction from large bodies of text, more specifically Dutch administrative decisions, which were previously researched in isolation. This is done by using NER and RegExs techniques to identify key sentences that contains to be extracted information, and are analyzed and extracted by ChatGPT. Different types of information can be extracted this way, including types that do and do not consist of clearly identifiable patterns or structures. The results show that the information extraction is effective, but are dependent on the flexibility and ability of rule-based methods to correctly identify types of information, and an effective sentence extraction with sufficient information for the machine learning method to accurately shape the context. The project highlights the need of thorough analysis of the to be extracted information and its context within the data to understand what approach is needed or most efficient and accurate for information extraction.

## GitHub

This GitHub contains the following:

1) [Demo.ipynb](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/demo.ipynb). Contains a demo of the project, as described in the methodology section of the thesis. The information task is done on one administrative fine.
2) [Annotation_protocol_dutch.pdf](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/Annotation_protocol_dutch.pdf). Contains the annotation protocol used for this project (in Dutch).
3) [method.md](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/method.md). Contains specific and extra information about the methodology for this project.
4) [`Scripts`](./scripts).
    1) [askGPT.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/askGPT.py). This file contains code to get a response from ChatGPT using a pre-defined prompt and extracted sentences from a single document.
    2) [candidateSentences.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/candidateSentences.py). This file extracts sentences from documents based on idxs from extracted identified legal effects, violated articles and legal basis.
    3) [categorization.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/categorization.py). This file contains code to identify if a document is an administrative fine or administrative penalty.
    4) [clean_text.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/clean_text.py). This file contains code to clean text by removing excessive spaces, removing ',-' and removing common prefixes (headers, footers).
    5) [extract_article.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_article.py). This file contains code to identify candidate violated articles and legal basis', returning detected articles and their corresponding idx in the list of sentences.
    6) [extract_date.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_date.py). This file contains code to find the date of an administrative decision.
    7) [extract_legal_effect.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_legal_effect.py). This file contains code to identify candidate legal effects, returning detected legal effects and their corresponding idx in the list of sentences.
    8) [spacy_model.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/spacy_model.py). This file contains code to load the spacy model used throughout this project.
    9) [text_to_sents.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/text_to_sents.py). This file contains code to convert a list of pages to a list of sentences.
5) [`example_data`](./example_data).
    1) [ksa.csv](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/example_data/KSA.csv). Contains example data for KSA (which is obtained from [Woogle](https://woogle.wooverheid.nl/search?publisher=zb000182&page=1&country=nl) in April 2024 and contains some irrelevant data).
   




