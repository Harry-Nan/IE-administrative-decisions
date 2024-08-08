![pipeline(2)](https://github.com/user-attachments/assets/fffe1870-ceae-408b-b45a-cfa2788510a5)

# Rule Based

### Date

The date of the decision is the only type of information that is solely found by using rule-based methods. Date included patterns that were uniform across documents, decisions, and government bodies. The following rule-based approach is applied to find the date of the decision:
- **Matching on date-patterns**. Firstly, the pre-trained NLP model was fine-tuned to detect dates and date patterns. This results in results with high recall but low precision, so additional DateTime-checks are applied to ensure the extracted match is a date.
- **Date presence**. In some decisions, the date of the decision is present on every page, for example, the header or footer. If an extracted date is thus present on all pages, it is likely the 'Date' is extracted, and the following steps are halted.
- **Keyword matching**. If no 'Date' was found in step 2, keywords were matched based on the context of the pattern (2 tokens before and after). If any token contains the word 'date', it is saved as a candidate date. Additionally, a database of Dutch cities (https://metatopos.dijkewijk.nl/) was used to check if any city is present in any context-token. This approach works for decisions that are written in letter format, where the date is often followed by a city, or vice versa. From all found candidate dates, the most recent date is chosen as 'Date'. If no candidate date was found, 'unknown' is returned for 'Date'.

Code: [extract_date.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_date.py)

![image](https://github.com/user-attachments/assets/53cc4acc-01ff-4b84-9611-0830ef20c81a)

**Figure 1:** Example of (uniform) structure of date in letter format and in header/footer.
 

#

### Violated Article and Legal Basis

These information types can be identified by rule-based methods, but require extensive pattern detection to correctly identify. This is often due to the required context-aware characteristic of these data. To identify for example the violated legal provision, an analysis of the context needs to be applied.

The violated legal provision(s) (Violated Article) and the legal provision that explains the legal basis of the decision-making authority (Legal Basis) are recognizable as they contain a consistent pattern since they are a reference to a certain piece of legislation. An example of a legal provision is: 'article 30t, first paragraph, opening words and under c, of the Wok'. This pattern is consistent, as the word 'article' is always present and followed by a number (or a sequence of numbers) and/or letter,  which is then linked to a law, in the example's case the Wok. In between the word 'article' and law, extra text can be added that specify what part of the article is being treated. Slight variations exist, such as naming multiple articles at the same time, often with the word 'juncto'. To extract the articles and their corresponding sentences, the following steps have been taken:

- **Keyword matching**. The words 'article' and its multiplication are identified, after which its sentence is extracted. The sentence is cut short and starts at the keyword.
- **POS-tagging**. After extracting the (shortened) sentence, POS-tagging is applied to the sentence and is cut short at the first appearance of a token being identified as a verb, or until the end of the sentence is reached. This is based on a pre-trained NLP model on Dutch text. This approach is effective, as there are no verbs when describing articles, but are often linked to verbs (such as the verb 'is violated').  This shortened sentence acts as the possible article for Violated Article or Legal Basis. 
- **Context-aware matching**. After identifying the article, the context of the article is taken into account. This is done by taking the sentence of which the article is part and 3 tokens from its neighbour sentences. This context is checked for words that indicate it is a violated article (Violated Article) or an article for the authority to make decisions (Legal Basis). For efficiency, verb-tokens are stemmed using SpaCy's tokenizer. For Violated Article, these words include 'violate', and for Legal Basis, these include 'basis', and 'qualified'. If the context matches any of these, its sentence and its neighbor sentence are saved to be analyzed by the machine-learning method.

Code: [extract_article.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_article.py)

#

### Legal Effect
Due to the choice to select administrative fines and penalties (as mentioned in section 3.1), the Legal Effect follows a similar pattern, as it always consists of a monetary amount, zero/nothing, or a warning. An example of a Legal Effect from an administrative fine is '€ 20.000,-', and for administrative penalty decisions '€ 1.000,- for each day until a maximum of € 10.000,-'. To identify the Legal Effect and extract its sentences for the machine learning method, the following steps have been taken:

- **Money-pattern matching**. By applying a combination of RegEx and NER, money patterns are being recognized and extracted. Since the pre-trained NLP model was deemed ineffective for correctly recognizing money instances through NER, RegEx has been added to the matcher to increase performance. For each match, the match and the sentence are extracted.
- **POS-tagging**. Similarly to section Violated Article and Legal Basis, POS-tagging is applied to the sentence, which shows the dependencies of the matched words. Through these dependencies, parent tokens from matched tokens are analysed, and the associated noun from the matched token is extracted, including extra information such as adjectives. See figure below. 

In some decisions, the Legal Effect is a conclusion of not giving the recipient a penalty, or giving them a warning. To include these types of Legal Effects for analysis by the machine learning model, keyword matching has been applied, selecting the sentences (and their neighbors) that contain words such as 'warning' or 'no fine'.     

Code: [extract_legal_effect.py](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/extract_legal_effect.py)

![POS(1)](https://github.com/user-attachments/assets/90070fc1-698f-4060-8e14-42fc884470ae)

