def load_dictionary(filename):
    dictionary = {}
    with open(filename, "r") as file:
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

def load_sentences(filename):
    sentences = []
    with open(filename, "r") as file:
        for line in file:
            sentences.append(line)
    return sentences