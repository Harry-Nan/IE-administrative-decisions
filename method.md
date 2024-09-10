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


# Machine-Learning

As explained in the paper, the ChatGPT-model [gpt-3.5-turbo-0125](https://platform.openai.com/docs/models/gpt-3-5-turbo) is used to extract information from administrative decisions. The prompt consists of general instructions (introducing the problem, shaping the context and defining the task), followed by specific instructions for each feature (explaination of the feature and how it should be extracted) and the list of sentences. 

The instructions for **administrative fines** is as follows (in Dutch): 

> <quote>De gegeven lijst met zinnen komen uit een enkel sanctiebesluit waarbij ontvanger(s) een artikel heeft/hebben overtreden. Extract uit de lijst met zinnen per ontvanger eenmalig de juiste values voor deze keys in de volgende structuur: 'boete': [{'effect':<hoogte (getal) van opgelegde gekregen boete. Als er besloten wordt om geen bedrag als boete op te leggen, geef dan weer of er een 'waarschuwing' of '0' wordt gegeven. Geen maximale, hypothetische, basisboetes of boetes in het verleden.>, 'ontvanger':<(rechts)persoon die boete/waarschuwing ontvangt, zo volledig mogelijk>, 'overtreden_artikel':<[Welke artikelen worden besproken of deze zijn overtreden. Geef elk artikel zo weer:  artikel + nummer + evt. aanhef + wet]>}], 'type_of_activity': <Wat er is gebeurd waardoor de wet/het artikel is overtreden>, 'dma': <Decision making authority; het bestuursorgaan dat bevoegd is om boete op te leggen>, 'legal_basis': <op basis van welk artikel de dma bevoegd is om een boete op te leggen. Geef het artikel weer als: artikel + nummer + evt. aanhef + wet.>. Geef je antwoord in json-formaat.</quote>


The instructions for **administrative penalties** is as follows (in Dutch): 

> <quote>De gegeven lijst met zinnen komen uit een enkel besluit tot last onder dwangsom waarbij ontvanger(s) een artikel heeft/hebben overtreden. Extract uit de lijst met zinnen per ontvanger eenmalig de juiste values voor deze keys in de volgende structuur: 'boete': [{'effect':<<hoogte (getal) van opgelegde dwangsom> per <eenheid> tot <maximum (getal)>. Als er besloten wordt om geen bedrag als dwangsom op te leggen, geef dan weer of er een 'waarschuwing' of '0' wordt gegeven. Geen maximale, hypothetische, basisboetes of boetes/dwangsommen in het verleden.>, 'ontvanger':<(rechts)persoon die dwangsom/waarschuwing ontvangt, zo volledig mogelijk>, 'overtreden_artikel':<[Welke artikelen worden besproken of deze zijn overtreden. Geef elk artikel zo weer:  artikel + nummer + evt. aanhef + wet]>}], 'type_of_activity': <Wat er is gebeurd waardoor de wet/het artikel is overtreden>, 'dma': <Decision making authority; het bestuursorgaan dat bevoegd is om boete op te leggen>, 'legal_basis': <op basis van welk artikel de dma bevoegd is om een dwangsom op te leggen. Geef het artikel weer als: artikel + nummer + evt. aanhef + wet.>. Geef je antwoord in json-formaat.</quote>

This is followed by a list of sentences. An example is the list of sentences below, from an administrative fine from Ksa ([download pdf](https://pid.wooverheid.nl/?pid=nl.ab5.2k.2014.1.bijlage.1)).

<pre style="max-height: 100px;">['Hij is verantwoordelijk voor de gang van zaken in de winkel en als eigenaar van de eenmanszaak aansprakelijk voor de gehele bedrijfsvoering. De aanwezigheid van de gokzuil in de winkel is aan hem toe te rekenen. 39, Derhalve is de eigenaar aan te merken als overtreder van artikel 30t, eerste lid, aanhef en onder c, van de Wok. 21 Hof Arnhem-Leeuwarden,', 'Inleiding 40. 41. 42. 43. 44, De Raad van Bestuur van de Kansspelautoriteit is ingevolge artikel 35a van de Wok bevoegd een boete op te leggen van ten hoogste het bedrag van de zesde categorie (artikel 23 van het Wetboek van Strafrecht) of - indien dit meer is — 10% van de omzet in het boekjaar voorafgaand aan de beschikking. Bij de vaststelling van de boete houdt de Raad rekening met de ernst van de overtreding en de mate waarin deze aan de overtreder kan worden verweten. Zo nodig houdt de Raad rekening met de omstandigheden waaronder de overtreding is gepleegd (artikel 5:46 van de Algemene wet bestuursrecht). Ingevolge artikel 3.4, tweede lid, van de Algemene wet bestuursrecht neemt de Raad bij het bepalen van de hoogte van de boete het evenredigheidsbeginsel in acht. overtreders een afschrikkende werking heeft (generale preventie). In de onderhavige zaak is de Raad van oordeel dat het passend is een boete op te leggen voor de overtreding van artikel 30t, eerste lid, aanhef en onder c, van de Wok. 8.2 Verwijtbaarheid 45. 46.', 'De Raad kwalificeert het aanwezig hebben van niet tot toelating gemerkte speelautomaten, in casu voor het afsluiten van sportweddenschappen, als zeer ernstig. 53. De Raad stelt vast dat in de periode 10 november 2012 tot en met 20 december 2012 in de winkel Star SAT Electronica op een niet tot toelating gemerkte speelautomaat (gokzuil) gelegenheid was tot het afsluiten van sportweddenschappen. 8.4 Boetevaststelling 54. Gelet op bovenstaande acht de Raad van bestuur van de Kansspelautoriteit een boete van € 20.000 passend en geboden. 8.5 Boeteverhogende of boeteverlagende omstandigheden 55. Er is niet gebleken van boeteverhogende of boeteverlagende omstandigheden. 8.6', 'Besluit De Raad van Bestuur van de Kansspelautoriteit: b. stelt vast dat de eigenaar van Star SAT Electronica, de heer [...] een overtreding heeft begaan van artikel 30t, eerste lid, aanhef en onder c, van de Wok door het aanwezig hebben van een speelautomaat (gokzuil) van een niet toegelaten model en niet voorzien van een bijbehorend merkteken, op een voor het publiek toegankelijke plaats, te weten een winkel. legt aan de eigenaar een boete op van € 20.000. ‘s-Gravenhage 21 november 2013']</pre>

This prompt results in a json-file, which is converted to csv using Panda's ([code](https://github.com/Harry-Nan/IE-administrative-decisions/blob/main/scripts/askGPT.py)), resulting in the following:

| Legal Effect | Ontvanger | Overtreden Artikel | Type of Activity | DMA | Legal Basis | Date       |
|--------------|-----------|--------------------|------------------|-----|-------------|------------|
| [20000]      | [eigenaar van de elektronicawinkel Star SAT Electronics] | [[artikel 30t, eerste lid, aanhef en onder c, d en e van de Wet op de kansspelen]] | Het aanwezig hebben van een speelautomaat (gokautomaat) zonder vergunning | Raad van Bestuur van de Kansspelautoriteit | artikel 35a van de Wet op de kansspelen | 21/11/2013 |

