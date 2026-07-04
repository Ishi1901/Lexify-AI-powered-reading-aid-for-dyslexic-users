import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier # 🚀 THE NEW KING OF TABULAR DATA
from nltk.corpus import wordnet
from wordfreq import word_frequency, zipf_frequency
import joblib
import os

class SimplexTrainer:
    def __init__(self):
        # 🚀 NO SCALER, NO SMOTE. Just pure, balanced decision trees.
        self.clf = RandomForestClassifier(
            n_estimators=300,        # Builds 300 different decision trees
            max_depth=15,            # Stops them from memorizing noise
            class_weight='balanced', # 🚀 THE MAGIC: Forces it to respect Simple words!
            random_state=42,
            n_jobs=-1                # Uses all your CPU cores to train instantly
        )

    def extract_features(self, word):
        word = str(word).lower()
        # Keeping the 4 highly optimized features
        unigram_prob = word_frequency(word, 'en')
        sent_freq = zipf_frequency(word, 'en')
        length = len(word)
        synsets = wordnet.synsets(word)
        synset_size = len(synsets)
        
        return [unigram_prob, sent_freq, length, synset_size]

    def train_and_save(self, csv_path, save_path):
        print("Loading dataset...")
        df = pd.read_csv(csv_path)
        
        print("Extracting features...")
        X = np.array([self.extract_features(word) for word in df['word']])
        y = np.array(df['label']) 
        
        print("Splitting data into training and testing sets...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        print("Training Random Forest Ensemble...")
        self.clf.fit(X_train, y_train)
        
        y_pred = self.clf.predict(X_test)

        print("\n --- DETAILED MODEL EVALUATION ---")
        print(f"Testing Accuracy: {self.clf.score(X_test, y_test):.2f}")
        
        print("\n Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        if cm.shape == (2, 2):
            print(f"True Negatives (Simple kept Simple): {cm[0][0]}")
            print(f"False Positives (Simple flagged Complex): {cm[0][1]}")
            print(f"False Negatives (Complex missed): {cm[1][0]}")
            print(f"True Positives (Complex flagged Complex): {cm[1][1]}")

        print("\n Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Simple (0)', 'Complex (1)']))
        
        joblib.dump(self.clf, save_path)
        print(f"\n✅ Random Forest successfully saved to {save_path}")

if __name__ == "__main__":
    os.makedirs("../models", exist_ok=True)
    trainer = SimplexTrainer()
    trainer.train_and_save("training_data.csv", "../models/simplex_mlp.pkl")