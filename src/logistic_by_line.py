import pymongo
import string
import warnings
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


def get_phrase_for_chord(one_parsed_song):
    word_list = one_parsed_song['words']
    chord_phrase_tuples = []
    for chord_set in one_parsed_song['chord_idxs']:
        word_idx = chord_set[0]
        chord_name = chord_set[1]
        phrase = ' '.join(word_list[(word_idx - 8):(word_idx + 3)])
        chord_phrase_tuples.append((chord_name, phrase))
    return chord_phrase_tuples


def make_phrase_is_minor_list(chord_phrase_tuples):
    phrases = []
    chords = []
    is_minor = []
    for chord_phrase_tup in chord_phrase_tuples:
        phrases.append(chord_phrase_tup[1])
        chords.append(chord_phrase_tup[0])
        is_minor.append('m' in chord_phrase_tup[0])
    return phrases, chords, is_minor


def get_full_phrase_is_minor_list(parsed_songs):
    phrases_all = []
    chords_all = []
    is_minor_all = []
    for song in parsed_songs:
        chord_phrase_tups = get_phrase_for_chord(song)
        phrases, chords, is_minor = make_phrase_is_minor_list(chord_phrase_tups)
        phrases_all.extend(phrases)
        chords_all.extend(chords)
        is_minor_all.extend(is_minor)
    return phrases_all, chords_all, is_minor_all

def make_phrase_chord_df(phrases_all, chords_all, is_minor_all):
    df = pd.DataFrame({
        'is_minor': is_minor_all,
        'chords': chords_all,
        'words': phrases_all
    })
    return df

if __name__ == "__main__":

    mc = pymongo.MongoClient()
    db = mc['chordify']

    parsed_songs_db = db["parsed_songs"]
    parsed_songs = list(parsed_songs_db.find())[25:75]

    tfidf = TfidfVectorizer()
    logistic = LogisticRegression()

    phrases_all, chords_all, is_minor_all = get_full_phrase_is_minor_list(parsed_songs)

    df_by_line = make_phrase_chord_df(phrases_all, chords_all, is_minor_all)


    words_train, words_test, is_minor_train, is_minor_test = train_test_split(df_by_line['words'], df_by_line['is_minor'])

    tfidf.fit(words_train)
    train_matrix = tfidf.transform(words_train)
    logistic.fit(train_matrix, is_minor_train)

    test_matrix = tfidf.transform(words_test)

    y_hat_log = logistic.predict_proba(test_matrix)
    is_minor_pred = logistic.predict(test_matrix)
    logistic_score = logistic.score(test_matrix, is_minor_test)