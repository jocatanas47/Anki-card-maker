import os
import argparse
from note_utils import load_dictionary
from note_utils import add_lemmas

def get_input_sentences(filename):
    first_column = []
    with open(filename, "r") as file:
        for line in file:
            columns = line.strip().split("\t")
            first_column_value = columns[0]
            first_column.append(first_column_value)
    return first_column

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

    with open(output_txt, "w", encoding="utf-8") as file:
        for lemma in lemmas:
            if not lemma.isdigit():
                file.write(lemma + "\n")

if __name__ == "__main__":
    main()
