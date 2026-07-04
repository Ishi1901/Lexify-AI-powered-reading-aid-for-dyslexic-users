# 🧠 Lexify: AI-Powered Lexical Simplification

**Lexify** is an intelligent, dual-pipeline text simplification platform and read-aloud aid explicitly designed to improve reading accessibility for dyslexic users. By leveraging a custom Machine Learning gatekeeper, a deterministic $O(1)$ caching dictionary, and Generative AI, Lexify dynamically adapts complex text into readable, easily digestible content without losing its original meaning or semantic context.

## ✨ Key Features
* **Dual-Pipeline Architecture:** Combines deterministic rules with probabilistic generative AI to prevent "hallucinations" and semantic drift, especially in domain-specific STEM texts.
* **$O(1)$ Dictionary Caching:** A highly optimized JSON whitelist that intercepts known idioms and context-heavy nouns before they reach the generative model.
* **Intelligent CWI Gatekeeper:** A 4-feature Random Forest Classifier that mathematically identifies complex words based on length, frequency, and semantic richness, ensuring only difficult vocabulary is processed by the heavy generative engine.
* **Dyslexia-Optimized UI:** Features the `OpenDyslexic3` font family (preventing letters from "jumping") and an intuitive interface designed according to rigorous HCI (Human-Computer Interaction) standards.
* **Evaluation Metrics:** Built-in benchmarking scripts to calculate SARI and Flesch-Kincaid readability scores.

---

## 🏗️ Project Architecture

The project is structured into a modular architecture to decouple the web server from the heavy machine learning logic:

### 1. The Core Application (`backend/`)
* **`app.py`:** The main entry point initializing the Flask server and database connections.
* **`routes_main.py` & `routes_auth.py`:** API endpoints managing core features (`/simplify`, `/ocr`, `/chat-assist`) and user authentication.
* **`database.py` & `lexify.db`:** SQLite database handling secure user credential storage.

### 2. The AI Engine (`backend/`)
* **`nlp_core.py`:** The primary linguistic engine containing a sliding window `[3, 2]` logic and grammar-matching functions.
* **`complexity_model.py`:** The Random Forest Gatekeeper. It extracts exactly 4 mathematical features (`unigram_prob`, `sent_freq`, `length`, `synset_size`) to determine token complexity via confidence thresholding.
* **`custom_dictionary.json`:** The deterministic caching layer for safe semantic preservation.

### 3. Machine Learning Pipeline
* **`train_model.py`:** Offline script for training the Random Forest Classifier on tabular data.
* **`preprocess_data.py`:** Cleans and formats raw MWE (Multi-Word Expression) datasets.
* **`run_benchmark.py`:** Automates testing for standard academic readability scores.
* **`models/simplex_mlp.pkl`:** The serialized, production-ready Gatekeeper model weights.

### 4. Frontend (`frontend/`)
* **`index.html` & `styles.css`:** The visual structure and responsive layout.
* **`script.js`:** Client-side asynchronous routing via the `fetch()` API for real-time text processing.
* **`OpenDyslexic3` Fonts:** Custom typography assets.

---

## 🛠️ Technology Stack
* **Backend:** Python 3, Flask, SQLite
* **Machine Learning:** Scikit-Learn (Random Forest), NLTK, spaCy, Wordfreq
* **Generative AI:** BERT / Google Gemini API
* **Frontend:** HTML5, CSS3, Vanilla JavaScript

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.8+ installed on your machine.


### Step-by-step Execution
1. **Clone the repository or extract the project folder:**
   ```bash
   cd Lexify