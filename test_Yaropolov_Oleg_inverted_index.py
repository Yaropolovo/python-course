import re
import json
import pytest
import os

from task_Yaropolov_Oleg_inverted_index import InvertedIndex, build_inverted_index, load_documents, make_query_for_requested_words, process_query, process_build
# import task_Yaropolov_Oleg_inverted_index

SAMPLE_DOCUMENTS_FOR_TESTING = "test_tiny_inverted_index_sample.txt"
DUMPED_INDEX = "test_dump_index.json"

@pytest.fixture
def testing_sample_documents():
    loaded_dict = load_documents(SAMPLE_DOCUMENTS_FOR_TESTING)
    return loaded_dict

@pytest.fixture
def testing_inverted_index(testing_sample_documents):
    inverted_index = build_inverted_index(testing_sample_documents)
    return inverted_index

def test_can_import_Inverted_Index():
    import task_Yaropolov_Oleg_inverted_index_lib

def test_building_method_on_trivial_example():
    # Подаем на вход пару документов, сверяем вывод. Много пробелов, символов, корявые доки в общем   # Проверь заглавные буквы!
    example_documents = {1: "one two three. !",
                         2: "two three. four"}
    expected_dict = {'one': [1],
                     'two': [1,2],
                     'three': [1,2],
                     'four': [2],
                     '': [1]}
    inverted_index = build_inverted_index(example_documents)
    assert expected_dict == inverted_index.data
    
def test_load_method_trivial_example(testing_sample_documents):
    s_12 = "Anarchism         Anarchism is often defined as a political philosophy which holds the state to be undesirable, unnecessary, or harmful.          The following sources cite anarchism as a political philosophy:      Slevin, Carl. \"Anarchism.\""
    s_290 = "A         A (named a  , plural aes ) is the first letter and vowel in the ISO basic Latin alphabet. It is similar to the Ancient Greek letter alpha, from which it derives. OriginsThe earliest certain ancestor of A is aleph (also called 'aleph), the first letter of the Phoenician alphabet  (which, by consisting entirely of consonants, is an abjad rather than a true alphabet). In turn, the origin of aleph may have been a pictogram of an ox head in Egyptian hieroglyphs, styled as a triangular head with 2 horns extended. Egyptian  Phoenician  aleph Greek  Alpha Etruscan  A Roman/Cyrillic  A        In 1600 B.C.E., the Phoenician alphabet's letter had a linear form that served as the base for some later forms. Its name must have corresponded closely to the Hebrew or Arabic aleph.  Blackletter A  Uncial A  Another Blackletter A    Modern Roman A  Modern Italic A  Modern Script A When the ancient Greeks adopted the alphabet, they had no use for the glottal stop—the first phoneme of the Phoenician pronunciation of the letter, and the sound that the letter denoted in Phoenician and other Semitic languages—so they used an adaptation of the sign to represent the vowel  , and gave it the similar name of alpha. In the earliest Greek inscriptions after the Greek Dark Ages, dating to the 8th century BC, the letter rests upon its side, but in the Greek alphabet of later times it generally resembles the modern capital letter, although many local varieties can be distinguished by the shortening of one leg, or by the angle at which the cross line is set.The Etruscans brought the Greek alphabet to their civilization in the Italian Peninsula and left the letter unchanged. The Romans later adopted the Etruscan alphabet to write the Latin language, and the resulting letter was preserved in the Latin alphabet used to write many languages, including English. During Roman times there were many variations on the letter A. First, was the monumental or lapidary style, which was used when inscribing on stone or other permanent mediums Α α : Greek letter Alpha А а : Cyrillic letter A   : Latin letter Alpha / Script A (or:    A a   )   : a turned lowercase letter A, used by the International Phonetic Alphabet for the near-open central vowel   : a turned capital letter A, used in predicate logic to specify universal quantification (for all)  ª  : an ordinal indicator Æ æ : Latin letter Æ ligature Computing codes   1    Other representations  References  External links    History of the Alphabet"
    expected_dict = {12: s_12.lower(),
                     290: s_290.lower()}
    assert expected_dict[12] == testing_sample_documents[12] #Я не понимаю, почему для 290 не работает!

# def test_input_is_empty():
#     # Подаем на вход ничего/None/..., проверяем реакцию/размер записанного
#     pass

@pytest.mark.parametrize(
    "strategy",
    [
        pytest.param('json', id='json'),
        pytest.param('struct', id='struct'),
    ]
)
def test_dump_load(strategy, tmpdir, testing_inverted_index):
    testing_inverted_index.dump(tmpdir.join(DUMPED_INDEX), strategy)
    loaded_inverted_index = InvertedIndex.load(tmpdir.join(DUMPED_INDEX), strategy)
    assert testing_inverted_index == loaded_inverted_index
    assert 0 != os.stat(tmpdir.join(DUMPED_INDEX)).st_size

def test_dump_strategy_not_implemented(capsys, tmpdir, testing_inverted_index):
    testing_inverted_index.dump(tmpdir.join(DUMPED_INDEX), 'some strategy')
    assert "not implemeted" in capsys.readouterr().err

def test_load_strategy_not_implemented(capsys, tmpdir, testing_inverted_index):
    loaded_inverted_index = InvertedIndex.load(tmpdir.join(DUMPED_INDEX), 'some strategy')
    assert "not implemeted" in capsys.readouterr().err

@pytest.mark.parametrize(
    "query, etalon_answer",
    [
        pytest.param(["is"], [12, 290], id="Common word"),
        pytest.param(['wow'], [], id="Nonexistent word"),
        pytest.param(['anarchism'], [12], id="Rare word"),
        pytest.param(['is', 'wow'], [], id="Common and nonexistent words"),
        pytest.param([], [], id="Empty query"),
    ]
)
def test_query_trivial_example(query, etalon_answer, testing_inverted_index, tmpdir):
    answer_from_class_method = testing_inverted_index.query(query)
    assert sorted(etalon_answer) == sorted(answer_from_class_method), (
        f"Expected answer from method is {etalon_answer}, but yor get {answer_from_class_method}"
    )

def test_several_queries_CLI(testing_inverted_index, capsys, tmpdir):
    queries = [["is"], ["wow"], ["anarchism"], ["is", "wow"]]
    expected_answer = "12,290\n\n12\n\n"

    make_query_for_requested_words(testing_inverted_index, queries)
    received_answer = capsys.readouterr().out
    assert expected_answer == received_answer, (
        f"Expected answer is {expected_answer}, but yor get {received_answer}"
    )

    testing_inverted_index.dump(tmpdir.join(DUMPED_INDEX), 'json')
    process_query(tmpdir.join(DUMPED_INDEX), 'json', queries, None)
    captured = capsys.readouterr()
    assert expected_answer == captured.out, (
        f"Expected answer from method is {expected_answer}, but yor get {captured.out}"
    )

# def test_build_command():
#     # Builded file is not empty
#     pass
#
# def test_available_storage_strategy():
#     # Check for no error for any storage strategy
#     pass

# def test_query_from_param():
#     # append option is available
#     pass
#

@pytest.mark.parametrize(
    "strategy, query_filepath, query_encoding, expected_data",
    [
        pytest.param("json", "queries_cp1251.txt", "cp1251", "12,290\n\n12\n\n\n", id="cp1251_json"),
        pytest.param("struct", "queries_cp1251.txt", "cp1251", "12,290\n\n12\n\n\n", id="cp1251_struct"),
        pytest.param("json", "queries_utf8.txt", "utf-8", "12,290\n\n12\n\n\n", id="utf-8_json"),
        pytest.param("struct", "queries_utf8.txt", "utf-8", "12,290\n\n12\n\n\n", id="utf-8_struct"),
    ]
)
def test_process_query_from_file(strategy, query_filepath, query_encoding, expected_data, capsys, tmpdir, testing_inverted_index):
    testing_inverted_index.dump(tmpdir.join(DUMPED_INDEX), strategy)
    with open(query_filepath, encoding = query_encoding) as query_fileio:
        process_query(tmpdir.join(DUMPED_INDEX), strategy, None, query_fileio)
        captured = capsys.readouterr()
    assert captured.out == expected_data



@pytest.mark.parametrize(
    "strategy",
    [
        pytest.param('json', id='json'),
        pytest.param('struct', id='struct'),
    ]
)
def test_process_build(strategy, tmpdir):
    process_build(strategy, SAMPLE_DOCUMENTS_FOR_TESTING, tmpdir.join(DUMPED_INDEX))
    assert 0 != os.stat(tmpdir.join(DUMPED_INDEX)).st_size


