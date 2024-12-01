import nltk
import wiktionary_parser_modified
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from HanTa import HanoverTagger as ht

app = Flask(__name__)

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

@app.route("/process_sentences", methods=["POST"])
def process_sentences():
    data = request.json
    sentences = data.get("sentences")
    lemmas = data.get("dictionary")

    if not sentences:
        return jsonify({"error": "No sentences provided"}), 400
    if not lemmas:
        return jsonify({"error": "No dictionary provided"}), 400
    
    notes, lemmas = sentences_to_notes(sentences, lemmas)

    return jsonify({"notes": notes, "dictionary": lemmas}), 200

if __name__ == "__main__":
    app.run()
