import pymongo
import string
import warnings
import re
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split


import logistic_many_chords


chord_list = ['A','B','C','D','E','F','G','A7','D7','Em','Am','Bm','Dm','Bb']


class LogisticChordAnalyzer:

    def __init__(self):
        self.chord_list = chord_list
        self.chord_model_dict = {}

    def fit(self, df_train):
        self.tfidf = TfidfVectorizer()
        X_train = df_train['words']
        self.tfidf.fit(X_train)
        for chord in chord_list:
            logistic = LogisticRegression()
            y_train = df_train[chord]
            tr_matrix = self.tfidf.transform(X_train)
            logistic.fit(tr_matrix, y_train)
            self.chord_model_dict[chord] = logistic

    def predict(self, some_words):
        words = [some_words]
        X = self.tfidf.transform(words)
        chord_prob_dict = {}
        for chord in chord_list:
            chord_prob_dict[chord] = self.chord_model_dict[chord].predict_proba(X)[0][1]
        best_chord = max(chord_prob_dict.items(), key=lambda k: k[1])
        # print (chord_prob_dict)
        return best_chord


def fit_lca():
    df_train, df_test = logistic_many_chords.get_data()
    lca = LogisticChordAnalyzer()
    lca.fit(df_train)
    return lca


def get_ten_words():
    while True:
        entry = input("Please enter 10-25 words: ")
        # if 10 <= len(entry.split()) <=25:
        return entry


def save_lca():
    lca = fit_lca()
    with open('lca.pkl', 'wb') as f:
        pickle.dump(lca, f)


def load_lca():
    with open ('lca.pkl', 'rb') as f:
        lca = pickle.load(f)
    return lca


def main():
    lca = load_lca()
    some_words = get_ten_words()

    chord_list = []
    for phrase in re.split('[?.,!]', some_words):
        best_phrase_chord = lca.predict(phrase)
        print (phrase, best_phrase_chord)

    # *******
    # best_chord = lca.predict(some_words)
    # print (best_chord)
    # *******

if __name__ == "__main__":
    main()