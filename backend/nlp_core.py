import spacy
import nltk
import pyinflect
from nltk.corpus import stopwords
from functools import lru_cache
from simplifier import engine

print("⏳ Loading Grammar Engine & NLP Tools...")
nlp = spacy.load('en_core_web_sm')
nltk.download('stopwords', quiet=True)

# Create an impenetrable shield of common English words
english_stopwords = set(stopwords.words('english'))
custom_ignore = {"name", "human", "system", "very", "this", "that", "with"} 
combined_shield = english_stopwords.union(custom_ignore)   
print("✅ NLP Tools Loaded!")

# 🧠 THE MEMORY CACHE
@lru_cache(maxsize=1000)
def cached_simplify(sentence, word):
    print(f"⚙️ Running heavy AI math for: '{word}'...")
    return engine.simplify(sentence, word)

# 🪄 THE GRAMMAR MATCHER
def match_grammar(original_word, simplified_word):
    orig_token = nlp(original_word)[0]
    target_tag = orig_token.tag_
    new_token = nlp(simplified_word)[0]
    
    # Force the simple word to bend to the target tag!
    inflected_word = new_token._.inflect(target_tag)
    return inflected_word if inflected_word else simplified_word