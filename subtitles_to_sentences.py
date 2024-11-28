import os
import argparse
import nltk
from HanTa import HanoverTagger as ht
from note_utils import load_dictionary
from note_utils import get_newest_file

def is_valid_sentence(sentence):
    return any(p in sentence for p in ".!?")

def process_srt(subtitles):
    blocks = subtitles.strip().split('\n\n')

    sentences = []
    current_sentence = ""

    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            subtitle_text = ' '.join(lines[2:])
            current_sentence += ' ' + subtitle_text.strip()
            if is_valid_sentence(current_sentence):
                sentences.append(current_sentence.strip())
                current_sentence = ""
    
    if current_sentence:
        sentences.append(current_sentence.strip())

    return sentences

def process_sentences(sentences, dictionary):
    tagger = ht.HanoverTagger ('morphmodel_ger.pgz')
    processed_sentences = []
    for sentence in sentences:
        sentence_tokens = nltk.word_tokenize(sentence)
        analyzed_sentence = tagger.tag_sent(sentence_tokens)
        for word, lemma, _ in analyzed_sentence:
            if lemma not in dictionary:
                processed_sentences.append(sentence)
                break
    return processed_sentences

def main():
    dictionary_folder = "dictionaries"

    parser = argparse.ArgumentParser()
    parser.add_argument("input_subtitles")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--dictionary", "-d", default=None)

    args = parser.parse_args()
    subtitles_file = args.input_subtitles
    output_file = args.output
    dictionary_file = args.dictionary

    output_folder = os.path.dirname(subtitles_file)

    if output_file:
        output_path = os.path.join(output_folder, output_file)
    else:
        output_path = os.path.join(output_folder, "extracted_sentences")

    if not dictionary_file:
        dictionary_file = get_newest_file(dictionary_folder)

    with open(subtitles_file, 'r', encoding='utf-8') as f:
        subtitles = f.read()
    
    lemmas = load_dictionary(dictionary_file)
    sentences = process_srt(subtitles)
    processed_sentences = process_sentences(sentences, lemmas)
    with open(output_path, "w", newline="") as f:
        for processed_sentence in processed_sentences:
            f.write(processed_sentence + "\n")

if __name__ == "__main__":
    main()
