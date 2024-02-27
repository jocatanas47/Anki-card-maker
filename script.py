from deep_translator import GoogleTranslator
import spacy
import wiktionaryparser
import csv
import argparse
from utils import load_dictionary
from utils import load_sentences

def get_wiktionary_entries(word):
    parser = wiktionaryparser.WiktionaryParser()
    entry = parser.fetch(word, "german")
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

def sentences_to_notes(sentences, lemmas):
    nlp = spacy.load("de_core_news_sm")
    translator = GoogleTranslator(source="de", target="en")
    notes = []
    for sentence in sentences:
        note = []

        modified_sentence = ""
        definitions = ""

        doc = nlp(sentence)
        for token in doc:
            lemma = token.lemma_
            if lemma in lemmas:
                modified_sentence += token.text
            else:
                modified_sentence += f"<b>{token.text}</b>"
                definitions += word_to_definition(lemma)
            modified_sentence += " "

        note.append(modified_sentence)
        note.append(translator.translate(sentence))
        note.append(definitions)
        notes.append(note)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_sentences")
    parser.add_argument("input_dictionary")
    parser.add_argument("output")
    args = parser.parse_args()
    sentences_txt = args.input_sentences
    dictionary_txt = args.input_dictionary
    output_csv = args.output

    sentences = load_sentences(sentences_txt)
    lemmas = load_dictionary(dictionary_txt)

    notes = sentences_to_notes(sentences, lemmas)
    
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(notes)

if __name__ == "__main__":
    main()
