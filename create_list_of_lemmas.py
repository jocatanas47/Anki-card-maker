import os
import argparse
import spacy

nlp = spacy.load("de_core_news_sm")

def get_input_sentences(filename):
    first_column = []
    with open(filename, 'r') as file:
        for line in file:
            columns = line.strip().split('\t')
            first_column_value = columns[0]
            first_column.append(first_column_value)
    return first_column

def load_dictionary(filename):
    dictionary = {}
    with open(filename, 'r') as file:
        for line in file:
            key = line.strip()
            dictionary[key] = True
    return dictionary

def add_lemmas(dictionary, sentences):
    for sentence in sentences:
        doc = nlp(sentence)
        for token in doc:
            lemma = token.lemma_
            if lemma not in dictionary:
                dictionary[lemma] = True
    return dictionary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    input_txt = args.input
    output_txt = args.output

    if os.path.exists(output_txt):
        lemmas = load_dictionary(output_txt)
    else:
        lemmas = {}
    
    sentences = get_input_sentences(input_txt)
    lemmas = add_lemmas(lemmas, sentences)

    with open(output_txt, 'w', encoding='utf-8') as file:
        for lemma in lemmas:
            if not lemma.isdigit():
                file.write(lemma + '\n')

if __name__ == "__main__":
    main()