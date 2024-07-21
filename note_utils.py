import os
import nltk
from HanTa import HanoverTagger as ht

def get_newest_file(folder):
    files = os.listdir(folder)
    files = [os.path.join(folder, file) for file in files]
    newest_file = max(files, key=os.path.getmtime)
    return newest_file

def load_dictionary(filename):
    dictionary = {}
    with open(filename, "r") as file:
        for line in file:
            key = line.strip()
            dictionary[key] = True
    return dictionary

def add_lemmas(dictionary, sentences):
    tagger = ht.HanoverTagger ('morphmodel_ger.pgz')
    for sentence in sentences:
        sentence_tokens = nltk.word_tokenize(sentence)
        analyzed_sentence = tagger.tag_sent(sentence_tokens)
        lemmata = [analysis[1] for analysis in analyzed_sentence]
        for lemma in lemmata:
            if lemma not in dictionary:
                dictionary[lemma] = True
    return dictionary

def load_sentences(filename):
    sentences = []
    with open(filename, "r") as file:
        for line in file:
            sentences.append(line)
    return sentences