import re
import json

from task_Yaropolov_Oleg_inverted_index_lib import InvertedIndex, build_inverted_index, load_documents

def test_can_import_Inverted_Index():
    import task_Yaropolov_Oleg_inverted_index_lib

def test_building_on_trivial_example():
    # Подаем на вход пару документов, сверяем вывод. Много пробелов, символов, корявые доки в общем   # Проверить БОЛЬШИЕ БУКВЫ
    example_documents = {1: "one two three. !",
                         2: "two three. four"}
    expected_dict = {'one': [1],
                     'two': [1,2],
                     'three': [1,2],
                     'four': [2],
                     '': [1]}
    inverted_index = build_inverted_index(example_documents)
    assert expected_dict == inverted_index.data 

def test_load_trivial_example(): 
    loaded_dict = load_documents("test_inverted_index_sample.txt")
    inverted_index = build_inverted_index(loaded_dict)
    s_12 = "Anarchism         Anarchism is often defined as a political philosophy which holds the state to be undesirable, unnecessary, or harmful.          The following sources cite anarchism as a political philosophy:      Slevin, Carl. \"Anarchism.\""
    s_290 = "A         A (named a  , plural aes ) is the first letter and vowel in the ISO basic Latin alphabet. It is similar to the Ancient Greek letter alpha, from which it derives. OriginsThe earliest certain ancestor of A is aleph (also called 'aleph), the first letter of the Phoenician alphabet  (which, by consisting entirely of consonants, is an abjad rather than a true alphabet). In turn, the origin of aleph may have been a pictogram of an ox head in Egyptian hieroglyphs, styled as a triangular head with 2 horns extended. Egyptian  Phoenician  aleph Greek  Alpha Etruscan  A Roman/Cyrillic  A        In 1600 B.C.E., the Phoenician alphabet's letter had a linear form that served as the base for some later forms. Its name must have corresponded closely to the Hebrew or Arabic aleph.  Blackletter A  Uncial A  Another Blackletter A    Modern Roman A  Modern Italic A  Modern Script A When the ancient Greeks adopted the alphabet, they had no use for the glottal stop—the first phoneme of the Phoenician pronunciation of the letter, and the sound that the letter denoted in Phoenician and other Semitic languages—so they used an adaptation of the sign to represent the vowel  , and gave it the similar name of alpha. In the earliest Greek inscriptions after the Greek Dark Ages, dating to the 8th century BC, the letter rests upon its side, but in the Greek alphabet of later times it generally resembles the modern capital letter, although many local varieties can be distinguished by the shortening of one leg, or by the angle at which the cross line is set.The Etruscans brought the Greek alphabet to their civilization in the Italian Peninsula and left the letter unchanged. The Romans later adopted the Etruscan alphabet to write the Latin language, and the resulting letter was preserved in the Latin alphabet used to write many languages, including English. During Roman times there were many variations on the letter A. First, was the monumental or lapidary style, which was used when inscribing on stone or other permanent mediums Α α : Greek letter Alpha А а : Cyrillic letter A   : Latin letter Alpha / Script A (or:    A a   )   : a turned lowercase letter A, used by the International Phonetic Alphabet for the near-open central vowel   : a turned capital letter A, used in predicate logic to specify universal quantification (for all)  ª  : an ordinal indicator Æ æ : Latin letter Æ ligature Computing codes   1    Other representations  References  External links    History of the Alphabet"
    expected_dict = {12: s_12.lower(),
                     290: s_290.lower()}
    assert expected_dict[12] == loaded_dict[12]

# def test_input_is_empty():
#     # Подаем на вход ничего/None/..., проверяем реакцию/размер записанного
#     pass

def test_dump_load():
    loaded_dict = load_documents("test_inverted_index_sample.txt")
    inverted_index = build_inverted_index(loaded_dict)
    inverted_index.dump('test_dump_index.json')
    
    loaded_inverted_index = InvertedIndex.load('test_dump_index.json')
    assert inverted_index == loaded_inverted_index

def test_query_example():
    loaded_dict = load_documents("test_inverted_index_sample.txt")
    inverted_index = build_inverted_index(loaded_dict)

    found_doc_1 = inverted_index.query(['is'])
    found_doc_2 = inverted_index.query(['wow'])
    found_doc_3 = inverted_index.query(['anarchism'])
    found_doc_4 = inverted_index.query(['is', 'wow'])

    expected_doc_1 = [12, 290]
    expected_doc_2 = []
    expected_doc_3 = [12]
    expected_doc_4 = []

    assert expected_doc_1 == found_doc_1
    assert expected_doc_2 == found_doc_2
    assert expected_doc_3 == found_doc_3
    assert expected_doc_4 == found_doc_4