# Combining rule-based and machine learning methods for effective information extraction on administrative decisions  

This is the GitHub page for the project for [CITaDOG](https://www.tilburguniversity.edu/about/digital-sciences-society/projects/case-inclusive-transparency) from Tilburg University in conjunction with the University of Amsterdam. 

This project applies a combination of rule-based methods with machine learning methods to achieve effective information extraction from large bodies of text, more specifically Dutch administrative decisions, which were previously researched in isolation. This is done by using NER and RegExs techniques to identify key sentences that contains to be extracted information, and are analyzed and extracted by ChatGPT. Different types of information can be extracted this way, including types that do and do not consist of clearly identifiable patterns or structures. The results show that the information extraction is effective, but are dependent on the flexibility and ability of rule-based methods to correctly identify types of information, and an effective sentence extraction with sufficient information for the machine learning method to accurately shape the context. The project highlights the need of thorough analysis of the to be extracted information and its context within the data to understand what approach is needed or most efficient and accurate for information extraction.

## GitHub

This GitHub contains the following:

1) [Demo.ipynb](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/demo.ipynb). Contains a demo of the project, as described in the methodology section of the thesis. The information task is done on one administrative fine.
2) [`Scripts`](./scripts).
    1) [askGPT.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/askGPT.py). This file contains code to get a response from ChatGPT using a pre-defined prompt and extracted sentences from a single document.
    2) [candidateSentences.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/candidateSentences.py). This file extracts sentences from documents based on idxs from extracted identified legal effects, violated articles and legal basis.
    3) [categorization.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/categorization.py). This file contains code to identify if a document is an administrative fine or administrative penalty.
    4) [clean_text.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/clean_text.py). This file contains code to clean text by removing excessive spaces, removing ',-' and removing common prefixes (headers, footers).
    5) [extract_article.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_article.py). This file contains code to identify candidate violated articles and legal basis', returning detected articles and their corresponding idx in the list of sentences.
    6) [extract_date.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_date.py). This file contains code to find the date of an administrative decision.
    7) [extract_legal_effect.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_legal_effect.py). This file contains code to identify candidate legal effects, returning detected legal effects and their corresponding idx in the list of sentences.
    8) [spacy_model.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/spacy_model.py). This file contains code to load the spacy model used throughout this project.
    9) [text_to_sents.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/text_to_sents.py). This file contains code to convert a list of pages to a list of sentences.


# Method: Appendix

This section serves as an appendix for the paper 'Combining Rule Based and Machine-Learning Methods for Efficient Information Extraction on Administrative Decisions'.

## Data selection
The obtained data includes categories of administrative decisions that are irrelevant to this paper, such as licensing decisions. Data selection will be done to select only administrative fines and penalties within the set of administrative decisions available from both government bodies:

- **Keyword extraction**. A keyword extraction technique is applied to create a subsection based on present or absent keywords for both categories. These include 'decision', and for example 'fine' and 'penalty' for administrative fines and penalties respectively. 
- **Remove irrelevant documents through keyword extraction**. Similarly to step 1, keywords that indicate an advice document are extracted, after which the document is shortened or completely removed. In some cases, documents include an advice in their appendix in a decision. By shortening the full document and focusing solely on the decision, future steps for information extraction may be improved.
- **Extraction of Legal Effect to remove and classify documents**. Lastly, the technique described in section \ref{sec:LErule} is applied to find the Legal Effect. If any obtained Legal Effect is associated with a word like 'fine' or 'penalty', these documents are classified with their corresponding category. If no legal effect or no matches with keywords are found, and there is no indication of the decisions resulting in a 'no fine' or 'warning' result, the document is not selected.

This results in a selection of administrative fines (267) and administrative penalties (171). See the figure below. However, this selection contains noise, as the data of Woogle also includes administrative decisions related to these enforcement decisions, such as disclosure decisions and possible decisions on appeal (in response to objection to an enforcement decision).

To remove disclosure decisions, legal provisions are extracted from the document (see later for more details). From this list of legal provisions, keyword matching is applied to check the presence of legal provisions that indicate a disclosure decision, such as 'article 3.1 from Woo'. If a match is found, the document is removed from the selection. Regarding appeal decisions, government bodies are required to include an option for the recipient to object to the decision. The time frame to send this objection is legally required to be six weeks and the type of objection differs from administrative fines/penalties and objection to appeal decisions. Sentences that contain the phrase 'six weeks' were extracted from the document, after which the sentence is checked to have the phrase 'notice of objection' present. If no sentence included this word, the document was dropped. This resulted in a selection of administrative fines and penalties, which is visualized in the figure below.

![categorization11(2)](https://github.com/user-attachments/assets/4333b7bb-924e-4c25-97e7-6aec50abb8a9)

Figure 1: Document classification for administrative decisions for both governing bodies. Blue indicates administrative fine, and red administrative penalty decisions. A light color indicates an internal appeal decision.

A code example of this can be found on this GitHub environment on [the Demo](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/demo.ipynb) or the [Python script](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/categorization.py).

## Data Analysis

![boxplots2](https://github.com/user-attachments/assets/7d32ef9f-d699-421a-9b4a-4012fbc9c646)

Figure 2: Document and page analysis for the two government bodies for administrative fine and penalty decisions. Blue and red indicate fines and penalties respectively.

![image](https://github.com/user-attachments/assets/793ab934-ee88-404d-9e2c-a150acc18fbb)

Figure 3: Analysation-scores for documents.


