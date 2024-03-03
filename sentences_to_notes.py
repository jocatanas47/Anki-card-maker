import os
import csv
import argparse
import nltk
import wiktionaryparser
from datetime import datetime
from deep_translator import GoogleTranslator
from HanTa import HanoverTagger as ht
from note_utils import load_dictionary
from note_utils import load_sentences

def get_newest_file(folder):
    files = os.listdir(folder)
    files = [os.path.join(folder, file) for file in files]
    newest_file = max(files, key=os.path.getmtime)
    return newest_file

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
            flag_first = True
            for line in definition["text"]:
                if flag_first:
                    string += f"<b>{line}</b>"
                    string += "<ol>"
                    flag_first = False
                else:
                    string += f"<li>{line}</li>"
                string += "<br>"
            string += "</ol>"
    return string

def sentences_to_notes(sentences, lemmas):
    tagger = ht.HanoverTagger ('morphmodel_ger.pgz')
    translator = GoogleTranslator(source="de", target="en")

    notes = []
    helper_dictionary = {}
    for sentence in sentences:
        note = []

        modified_sentence = ""
        definitions = ""

        sentence_tokens = nltk.word_tokenize(sentence)
        analyzed_sentence = tagger.tag_sent(sentence_tokens)
        for analysis in analyzed_sentence:
            word = analysis[0]
            lemma = analysis[1]
            if lemma in helper_dictionary:
                modified_sentence += word
            else:
                helper_dictionary[lemma] = True
                if lemma in lemmas:
                    modified_sentence += word
                else:
                    modified_sentence += f"<b>{word}</b>"
                    definitions += word_to_definition(lemma)
            modified_sentence += " "

        note.append(modified_sentence)
        note.append(translator.translate(sentence))
        note.append(definitions)
        notes.append(note)
    return notes, {**lemmas, **helper_dictionary}

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    dictionary_folder = "dictionaries"
    input_folder = "inputs"
    output_folder = "outputs"

    output_dictionary = f"{timestamp}.txt"
    output_dictionary_path = os.path.join(dictionary_folder, output_dictionary)

    parser = argparse.ArgumentParser()
    parser.add_argument("input_sentences")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--dictionary", "-d", default=None)

    args = parser.parse_args()
    sentences_file = args.input_sentences
    output_file = args.output
    dictionary_file = args.dictionary

    if output_file:
        output_path = os.path.join(output_folder, output_file)
    else:
        output_path = os.path.join(output_folder, f"{timestamp}.csv")

    if not dictionary_file:
        dictionary_file = get_newest_file(dictionary_folder)
    
    sentences = load_sentences(sentences_file)
    lemmas = load_dictionary(dictionary_file)

    notes, lemmas = sentences_to_notes(sentences, lemmas)
    
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(notes)

    with open(output_dictionary_path, "w", encoding="utf-8") as file:
        for lemma in lemmas:
            if not lemma.isdigit():
                file.write(lemma + "\n")

if __name__ == "__main__":
    main()
