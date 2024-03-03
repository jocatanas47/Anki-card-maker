import csv
import argparse
import spacy
import nltk
import wiktionaryparser
from deep_translator import GoogleTranslator
from HanTa import HanoverTagger as ht
from note_utils import load_dictionary
from note_utils import load_sentences

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

    notes, lemmas = sentences_to_notes(sentences, lemmas)
    
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(notes)

    with open("a_" + dictionary_txt, "w", encoding="utf-8") as file:
        for lemma in lemmas:
            if not lemma.isdigit():
                file.write(lemma + "\n")

if __name__ == "__main__":
    # TODO: choose a better lemmatization algo
    main()
