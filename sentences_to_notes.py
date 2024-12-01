import os
import csv
import argparse
import nltk
import wiktionary_parser_modified
from datetime import datetime
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from HanTa import HanoverTagger as ht
from note_utils import load_dictionary
from note_utils import load_sentences
from note_utils import get_newest_file

def get_wiktionary_entries(word):
    parser = wiktionary_parser_modified.WiktionaryParser()
    entry = parser.fetch(word, "german")
    return entry

def word_to_definition(word):
    entries = get_wiktionary_entries(word)
    definition_parts = []
    for entry in entries:
        definitions = entry["definitions"]
        for definition in definitions:
            definition_parts.append(definition["partOfSpeech"])
            definition_parts.append("<br>")
            flag_first = True
            for line in definition["text"]:
                if flag_first:
                    definition_parts.append(f"<b>{line}</b>")
                    definition_parts.append("<ol>")
                    flag_first = False
                else:
                    definition_parts.append(f"<li>{line}</li>")
                definition_parts.append("<br>")
            definition_parts.append("</ol>")
    return definition_parts

def sentences_to_notes(sentences, lemmas):
    tagger = ht.HanoverTagger ('morphmodel_ger.pgz')
    translator = GoogleTranslator(source="de", target="en")

    notes = []
    helper_dictionary = {}
    for sentence in sentences:
        note = []

        modified_sentence_parts = []
        definitions_parts = []

        sentence_tokens = nltk.word_tokenize(sentence)
        analyzed_sentence = tagger.tag_sent(sentence_tokens)
        for word, lemma, _ in analyzed_sentence:
            if lemma in [".", ",", ":", ";", "?", "!", "...", "'s"] and modified_sentence_parts:
                modified_sentence_parts.pop()
            if lemma in helper_dictionary:
                modified_sentence_parts.append(word)
            else:
                helper_dictionary[lemma] = True
                if lemma in lemmas:
                    modified_sentence_parts.append(word)
                else:
                    modified_sentence_parts.append(f"<b>{word}</b>")
                    definitions_parts.extend(word_to_definition(lemma))
            modified_sentence_parts.append(" ")

        note.append("".join(modified_sentence_parts))
        note.append(translator.translate(sentence))
        note.append("".join(definitions_parts))
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
