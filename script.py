from deep_translator import GoogleTranslator
import spacy
import wiktionaryparser
import csv

def get_wiktionary_entries(word):
    parser = wiktionaryparser.WiktionaryParser()
    entry = parser.fetch(word, 'german')
    return entry

def word_to_definition(word):
    entries = get_wiktionary_entries(word)
    string = ""
    for entry in entries:
        definitions = entry["definitions"]
        for definition in definitions:
            string += definition["partOfSpeech"]
            string += "<br>"
            for line in definition["text"]:
                string += line
                string += "<br>"
    return string

nlp = spacy.load("de_core_news_sm")

translator = GoogleTranslator(source='de', target='en')

sentences = []
output = []
with open('izvuceni', 'r') as file:
    for line in file:
        sentences.append(line)

def load_dictionary(filename):
    dictionary = {}
    with open(filename, 'r') as file:
        for line in file:
            key = line.strip()
            dictionary[key] = True
    return dictionary

lemmas = load_dictionary("test_lemas.txt")

new_sentences = []
for sentence in sentences:
    new_output = []
    new_sentence = ""
    new_definitions = ""
    doc = nlp(sentence)
    for token in doc:
        lemma = token.lemma_
        if lemma in lemmas:
            new_sentence += token.text
        else:
            new_sentence += f"<b>{token.text}</b>"
            new_definitions += word_to_definition(lemma)
        new_sentence += " "
    new_sentences.append(new_sentence)
    new_output.append(new_sentence)
    new_output.append(translator.translate(sentence))
    new_output.append(new_definitions)
    output.append(new_output)

# print(output)

file_name = 'data.csv'

# Write the data to a CSV file
with open(file_name, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(output)

a = 24
b = 2
c = a