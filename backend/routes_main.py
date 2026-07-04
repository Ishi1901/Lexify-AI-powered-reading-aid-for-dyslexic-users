from urllib import response

from flask import Blueprint, request, jsonify
import textstat
import evaluate  
import json
import pytesseract
from PIL import Image
from complexity_model import complexity_gatekeeper
import requests
import os

# Import the logic we separated into nlp_core.py
from nlp_core import nlp, combined_shield, cached_simplify, match_grammar

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Create the Blueprint
main_bp = Blueprint('main', __name__)

sari_metric = None

@main_bp.route('/simplify', methods=['POST', 'OPTIONS'])
def simplify_text():
    if request.method == 'OPTIONS': return jsonify({}), 200

    global sari_metric
    if sari_metric is None:
        print("⏳ Loading SARI Evaluation Metric (First Request Only)...")
        sari_metric = evaluate.load("sari")

    # 1. CRITICAL FIX: Add silent=True to prevent Flask crashing on bad JSON
    data = request.get_json(silent=True)
    
    # 2. CRITICAL FIX: Safety check if data is completely missing or corrupted
    if not data:
        return jsonify({"error": "Invalid or empty JSON payload received."}), 400

    # Safely extract the text
    text = data.get('text', '')
    reference_text = data.get('reference', '') 

    # 3. CRITICAL FIX: Skip processing if the dataset gave us an empty sentence
    if not text.strip():
        return jsonify({"error": "The text provided was empty."}), 400

    try:
        with open('custom_dictionary.json', 'r') as f:
            custom_dict = json.load(f)
    except FileNotFoundError:
        custom_dict = {}

    words = text.split()
    final_words, glossary, i = [], [], 0
    
    while i < len(words):
        match_found = False
        
        # 🪟 THE SLIDING WINDOW
        for window in [3, 2]:
            if i + window <= len(words):
                chunk = words[i:i+window]
                clean_chunk = " ".join(["".join(filter(str.isalnum, w)) for w in chunk]).lower()
                
                if clean_chunk in custom_dict:
                    replacement = custom_dict[clean_chunk][0] 
                    final_words.append(replacement)
                    glossary.append({"original": clean_chunk, "simplified": replacement})
                    i += window
                    match_found = True
                    break 

        if match_found: continue
            
        # 🛑 SINGLE WORD LOGIC
        word = words[i]
        clean_word = "".join(filter(str.isalnum, word))
        
        # 1. Shield Check
        if len(clean_word) <= 3 or clean_word.lower() in combined_shield:
            final_words.append(word)

        # 2. Smart Dictionary Check
        elif clean_word and nlp(clean_word)[0].lemma_.lower() in custom_dict:
            lemma = nlp(clean_word)[0].lemma_.lower()
            base_synonym = custom_dict[lemma][0] 
            perfect_grammar_word = match_grammar(clean_word, base_synonym)
            final_word_with_punct = word.replace(clean_word, perfect_grammar_word)
            final_words.append(final_word_with_punct) 
            glossary.append({"original": clean_word, "simplified": perfect_grammar_word})

        # 3. Gatekeeper Check
        elif clean_word and complexity_gatekeeper.is_complex(clean_word):
            simplified_sentence = cached_simplify(text, clean_word)
            try:
                new_word = simplified_sentence.split()[words.index(word)]
                clean_new_word = "".join(filter(str.isalnum, new_word))
                perfect_grammar_word = match_grammar(clean_word, clean_new_word)
                final_word_with_punct = word.replace(clean_word, perfect_grammar_word)
                final_words.append(final_word_with_punct)
                
                if clean_word.lower() != clean_new_word.lower():
                    glossary.append({"original": clean_word, "simplified": perfect_grammar_word})
            except IndexError:
                final_words.append(word)
        else:
            final_words.append(word)
            
        i += 1 
            
    final_text = " ".join(final_words)
    
    sari_score = "N/A"
    if reference_text:
        results = sari_metric.compute(sources=[text], predictions=[final_text], references=[[reference_text]])
        sari_score = round(results['sari'], 2)

    return jsonify({
        "simplified": final_text,
        "glossary": glossary,
        "original_grade": textstat.text_standard(text),
        "simplified_grade": textstat.text_standard(final_text),
        "fk_ease_original": textstat.flesch_reading_ease(text),
        "fk_ease_simplified": textstat.flesch_reading_ease(final_text),
        "fk_grade_original": textstat.flesch_kincaid_grade(text),
        "fk_grade_simplified": textstat.flesch_kincaid_grade(final_text),
        "sari_score": sari_score 
    })

@main_bp.route('/ocr', methods=['POST', 'OPTIONS'])
def process_image():
    if request.method == 'OPTIONS': return jsonify({}), 200
    file = request.files['image']
    img = Image.open(file.stream)
    text = pytesseract.image_to_string(img) 
    return jsonify({"text": text})

@main_bp.route('/chat-assist', methods=['POST'])
def chat_assist():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({"reply": "Please ask a question!"}), 400

    try:
        system_instruction = (
            "You are Lexify-Bot, a kind and helpful reading assistant for a user with dyslexia. "
            "Keep answers under 3 sentences using simple words.\n"
            f"User: {user_message}"
        )

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": system_instruction}
                ]
            }
        )
    # ✅ ADD THIS BLOCK HERE
        if response.status_code != 200:
            print(response.text)
            return jsonify({"reply": "API limit reached or error occurred."}), 500
        data = response.json()

        reply = data['choices'][0]['message']['content']

        return jsonify({"reply": reply})

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"reply": "AI is temporarily unavailable."}), 500
    
   