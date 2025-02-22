import json
from collections import defaultdict
import nltk
nltk.download("punkt")
from flask import Flask, request, jsonify
from deep_translator import GoogleTranslator
from HanTa import HanoverTagger as ht

app = Flask(__name__)

def preprocess_jsonl_to_dict(jsonl_file):
    index_dict = defaultdict(list)
    with open(jsonl_file, 'r') as f:
        for line in f:
            obj = json.loads(line)
            key = obj["word"]
            index_dict[key].append(obj)
    return index_dict

def word_to_definition(word, wiktionary):
    entries = wiktionary[word]
    definition_parts = []
    for entry in entries:
        definition_parts.append(entry["head_templates"][0]["expansion"])
        definition_parts.append("<br>")
        definitions = entry["senses"]
        definition_parts.append("<ol>")
        for definition in definitions:
            definition_parts.append(f"<li>{definition['glosses']}</li>")
        definition_parts.append("</ol>")
    return definition_parts

def sentences_to_notes(sentences, lemmas):
    tagger = ht.HanoverTagger ("morphmodel_ger.pgz")
    translator = GoogleTranslator(source="de", target="en")
    wiktionary = preprocess_jsonl_to_dict("kaikki.org-dictionary-German-words.jsonl")

    notes = []
    helper_dictionary = set()
    for sentence in sentences:
        note = {}

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
                helper_dictionary.add(lemma)
                if lemma in lemmas:
                    modified_sentence_parts.append(word)
                else:
                    modified_sentence_parts.append(f"<b>{word}</b>")
                    definitions_parts.extend(word_to_definition(lemma, wiktionary))
            modified_sentence_parts.append(" ")

        note["sentence"] = "".join(modified_sentence_parts)
        note["translation"] = translator.translate(sentence)
        note["info"] = "".join(definitions_parts)
        
        notes.append(note)
    return notes, list(lemmas | helper_dictionary)

@app.route("/process_sentences", methods=["POST"])
def process_sentences():
    data = request.json
    sentences = data.get("sentences")
    lemmas = data.get("dictionary")
    lemmas = set(lemmas)

    if not sentences:
        return jsonify({"error": "No sentences provided"}), 400
    if not lemmas:
        return jsonify({"error": "No dictionary provided"}), 400
    
    notes, lemmas = sentences_to_notes(sentences, lemmas)
    return jsonify({"notes": notes, "dictionary": lemmas}), 200

if __name__ == "__main__":
    app.run()
