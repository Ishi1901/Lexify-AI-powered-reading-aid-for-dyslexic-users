import numpy as np
import joblib
from nltk.corpus import wordnet
from wordfreq import word_frequency, zipf_frequency
import os

class ComplexityClassifier:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), '../models/simplex_mlp.pkl')
        try:
            # 🚀 Loads the Random Forest Gatekeeper pipeline
            self.clf = joblib.load(model_path)
            self.is_trained = True
        except FileNotFoundError:
            print("WARNING: Model file not found. Please run train_model.py first.")
            self.is_trained = False

    def extract_features(self, word):
        word = str(word).lower()
        
        # Extract the EXACT 4 features used in Random Forest training
        unigram_prob = word_frequency(word, 'en')
        sent_freq = zipf_frequency(word, 'en')
        length = len(word)
        synsets = wordnet.synsets(word)
        synset_size = len(synsets)
        
        # Return 4 features (appearance removed to prevent shape mismatch crash)
        return [unigram_prob, sent_freq, length, synset_size]

    def is_complex(self, word):
        if not self.is_trained:
            return False # Failsafe
            
        features = np.array([self.extract_features(word)])
        prediction = self.clf.predict(features)
        return prediction[0] == 1

complexity_gatekeeper = ComplexityClassifier()