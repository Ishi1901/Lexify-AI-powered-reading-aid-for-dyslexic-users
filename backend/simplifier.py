import json
import re
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from wordfreq import zipf_frequency
from transformers import pipeline
from simpletransformers.language_representation import RepresentationModel

# Download grammar tools silently
nltk.download('stopwords', quiet=True)

class SimplexEngine:
    def __init__(self):
        print("⏳ Loading BERT Engine 1: The Generative Masked Language Model...")
        # THE NEW GENERATOR
        self.generator = pipeline("fill-mask", model="bert-base-uncased")

        print("⏳ Loading BERT Engine 2: The Sentence Embedding Judge...")
        # THE EXISTING JUDGE
        self.judge = RepresentationModel(
            model_type="bert",
            model_name="bert-base-uncased",
            use_cuda=False
        )
        
        self.stop_words = set(stopwords.words('english'))
        
        # LOAD THE EXTERNAL DICTIONARY
        print("📖 Loading custom dictionary from JSON...")
        try:
            with open("custom_dictionary.json", "r") as file:
                self.custom_dict = json.load(file)
            print(f"✅ Loaded {len(self.custom_dict)} custom word overrides!")
        except FileNotFoundError:
            print("⚠️ Warning: custom_dictionary.json not found. Using empty dictionary.")
            self.custom_dict = {}

    def filter_smart_synonyms(self, predictions, original_word):
        safe_candidates = []
        seen_words = set()
        orig_clean = original_word.lower().strip()
        
        # We now loop through BERT's detailed prediction objects
        for pred in predictions:
            word = pred['token_str'].lower().strip()
            grammar_score = pred['score'] # How well it fits the sentence grammar!
            
            # 1. Grammar & Safety Checks
            if not word.isalpha(): continue 
            if word == orig_clean: continue 
            if len(word) > 12: continue
            
            # 2. THE PRONOUN/PREPOSITION BAN (Fixes the "it/for" caveman bug)
            if word in self.stop_words: continue 
            
            # 3. Readability Check
            zipf = zipf_frequency(word, 'en')
            if zipf < 3.5: continue
            
            # 4. Remove Duplicates while keeping order
            if word not in seen_words:
                seen_words.add(word)
                # Save the word along with its important stats
                safe_candidates.append({
                    'word': word,
                    'zipf': zipf,
                    'grammar_score': grammar_score
                })
                
        return safe_candidates


    def simplify(self, sentence, complex_word):
        clean_target = complex_word.lower().strip()
        
        # 1. THE STOPWORD SHIELD: Ignore basic grammar words instantly
        if clean_target in self.stop_words or len(clean_target) <= 3:
            return sentence

        print(f"\n🔍 Processing: '{complex_word}'")
        
        # Create a safe, case-insensitive regex pattern for exactly this word
        # \b ensures we only match the whole word, not parts of other words
        pattern = re.compile(rf"\b{re.escape(complex_word)}\b", re.IGNORECASE)
        
        # 2. THE OVERRIDE: Check if we have a perfect human-written replacement first
        if clean_target in self.custom_dict:
            # Bypass the AI entirely and apply the human-approved word!
            best_human_word = self.custom_dict[clean_target][0]
            print(f"🎯 Override Dictionary activated! Swapping to: '{best_human_word}'")
            return pattern.sub(best_human_word, sentence, count=1)

        # 3. BERT GENERATOR: Use Fill-Mask to natively guess words
        masked_sentence = pattern.sub("[MASK]", sentence, count=1)
        
        # SAFETY CHECK: Did the replacement actually work?
        if "[MASK]" not in masked_sentence:
            print(f"⚠️ Warning: Failed to insert [MASK] for word '{complex_word}'. Keeping original.")
            return sentence
        
        # Ask BERT for its top 30 grammatically correct guesses safely
        try:
            predictions = self.generator(masked_sentence, top_k=30)
        except Exception as e:
            print(f"⚠️ BERT Generation failed: {e}")
            return sentence
        
        # Pass BERT's raw predictions to our new, stricter Bouncer
        safe_candidates = self.filter_smart_synonyms(predictions, complex_word)

        if not safe_candidates:
            print("⚠️ No safe synonyms found. Keeping original word to preserve grammar.")
            return sentence

        # 4. THE TRI-FACTOR JUDGE (Meaning + Grammar + Simplicity)
        safe_words = [cand['word'] for cand in safe_candidates]
        
        # Safely insert the candidate words into the sentence using our regex pattern
        candidates_text = [pattern.sub(w, sentence, count=1) for w in safe_words]
        
        orig_encoded = self.judge.encode_sentences([sentence], combine_strategy=1)
        cand_encoded = self.judge.encode_sentences(candidates_text, combine_strategy=1)
        
        # Calculate meaning preservation
        scores = cosine_similarity(orig_encoded, cand_encoded)[0]
        
        best_idx = -1
        highest_human_score = -1
        
        for idx, cand in enumerate(safe_candidates):
            sim_score = scores[idx]
            word = cand['word']
            
            # RULE 1: The meaning MUST be at least 82% identical to the original
            if sim_score > 0.82:
                
                # RULE 2: Calculate a balanced "Human Readability" score
                human_score = sim_score + (cand['zipf'] * 0.015) + (cand['grammar_score'] * 0.5)
                
                if human_score > highest_human_score:
                    highest_human_score = human_score
                    best_idx = idx
        
        if best_idx == -1:
            print("⚠️ Words were generated, but none kept the original meaning safely. Keeping original.")
            return sentence
            
        best_word = safe_words[best_idx]
        print(f"🤖 Lexify chose grammatically perfect word: '{best_word}'")
        print(f"   📊 Stats -> Meaning: {scores[best_idx]:.2f} | Simplicity: {safe_candidates[best_idx]['zipf']:.2f} | Grammar: {safe_candidates[best_idx]['grammar_score']:.3f}")
        
        return candidates_text[best_idx]
# Initialize engine
engine = SimplexEngine()