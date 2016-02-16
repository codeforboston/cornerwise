from collections import defaultdict
import nltk, redis

def group_true(pred, l):
    """Group adjacent elements in the collection l for which pred(element)
    is true.

    :param pred: A test function that will be run on each member of l
    :param l: a collection

    :returns: A generator that emits lists of elements from l
    """
    group = []

    for elem in l:
        if pred(elem):
            group.append(elem)
        elif group:
            yield group
            group = []

    if group:
        yield group


def is_noun_phrase(tagged):
    """
    :param tagged: An iterable of tagged words (i.e., (word, tag) tuples)

    :returns: boolean
    """
    return tagged[-1][1] == "NN"


def noun_phrases(tagged):
    groups =  group_true(lambda tw: tw[1] in set(["NN", "JJ"]), tagged)

    return filter(is_noun_phrase, groups)

def remove_subphrases(tagged):
    last_terms = defaultdict(int)
    for term in tagged:
        last_terms[term[-1]] = max(len(term), last_terms[term[-1]])

    return [term for term in tagged if len(term) == last_terms[term[-1]]]


def join_words(tagged):
    return " ".join(tw[0] for tw in tagged)


def keywords(text):
    """
    :param text: a text string to be evaluated

    :returns: An iterable of strings containing the recognized
    """
    tokenized = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokenized)
    return list(map(join_words, noun_phrases(tagged)))


def setup():
    "Install required NLTK corpora"
    return nltk.download("punkt") and \
        nltk.download("averaged_perceptron_tagger")

setup()
