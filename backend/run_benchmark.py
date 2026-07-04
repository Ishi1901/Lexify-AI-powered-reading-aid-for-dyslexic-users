import requests
import time
import textstat
import nltk
from nltk.tokenize import sent_tokenize

# Download the sentence splitter tool silently
nltk.download('punkt', quiet=True)

# Your Flask API Endpoint
API_URL = "http://127.0.0.1:5000/simplify"

# 📊 THE TESTING CORPUS: Full Paragraphs (Medical, Legal, Tech, Academic)
dataset = [
    # --- MEDICAL PARAGRAPH ---
    "The geriatric patient presented with a multitude of overlapping comorbidities, which significantly complicated the initial prognosis. Intravenous fluids were immediately administered to counteract the severe physiological manifestations of dehydration. Following the stabilization of the patient, the attending physician prescribed a targeted analgesic to mitigate the localized inflammation and alleviate the acute discomfort.",
    
    # --- LEGAL PARAGRAPH ---
    "The defendant was indicted on multiple counts of systemic corporate embezzlement spanning a period of five years. Consequently, the fiduciary responsibilities of the executive board were heavily scrutinized to ensure future organizational stability. The final legal stipulation mandates mandatory arbitration for all subsequent grievances, thereby circumventing the need for further public litigation.",
    
    # --- TECHNICAL / AI PARAGRAPH ---
    "The generative adversarial network successfully synthesized photorealistic avatars by mapping vectors from the latent space. However, during the initial training phase, the heuristic algorithm rapidly converged on a suboptimal global minimum, resulting in severe visual artifacting. To rectify this computational anomaly, the engineering team implemented an intricate mathematical framework to decipher the voluminous dataset and optimize the neural weights.",
    
    # --- ACADEMIC / SOCIOLOGY PARAGRAPH ---
    "Contemporary socioeconomic disparities are frequently exacerbated by systemic institutional biases entrenched within the modern educational framework. A comprehensive synthesis of the available literature revealed a conspicuous gap in the prevailing methodology regarding resource allocation. Consequently, researchers argue that the traditional pedagogical approach must be radically restructured to facilitate equitable and autonomous learning among marginalized cohorts.",
    
    # --- CORPORATE / BUSINESS PARAGRAPH ---
    "The multinational corporation decided to terminate the highly lucrative contract due to unforeseen financial discrepancies discovered during the quarterly audit. The unilateral termination was initially deemed null and void by the presiding magistrate, prompting an immediate appeal. Ultimately, the board of directors unanimously ratified a series of amended corporate bylaws to prevent similar catastrophic financial oversights."
]

print(f"🚀 Starting Lexify Paragraph-Level Benchmarking (with Sentence Splitter)...")
print(f"📚 Total Paragraphs to Process: {len(dataset)}\n")

orig_grades = []
simp_grades = []
successful_swaps = 0

start_time = time.time()

for i, text in enumerate(dataset, 1):
    print(f"\n🔄 Processing Paragraph [{i}/{len(dataset)}]...")
    
    # Calculate Original Grade
    orig_fk = textstat.flesch_kincaid_grade(text)
    
    # 1. SPLIT THE PARAGRAPH INTO BITE-SIZED SENTENCES
    sentences = sent_tokenize(text)
    simplified_sentences = []
    
    try:
        # 2. SEND ONE SENTENCE AT A TIME TO YOUR FLASK API
        for sentence in sentences:
            
            # 🚨 FIX 1: We added the empty "reference" string your API requires!
            response = requests.post(API_URL, json={"text": sentence, "reference": ""})
            
            if response.status_code == 200:
                result = response.json()
                
                # 🚨 FIX 2: We changed "simplified_text" to "simplified" to match your API!
                simplified_sentences.append(result.get("simplified", sentence))
                
            else:
                # 🚨 THE DEBUGGER: If it fails, this will tell us exactly why!
                print(f"   [DEBUG ERROR] API returned status {response.status_code}")
                print(f"   [DEBUG ERROR] API says: {response.text}")
                simplified_sentences.append(sentence)
                
        # 3. GLUE THE PARAGRAPH BACK TOGETHER
        final_simplified_paragraph = " ".join(simplified_sentences)
        
        # Calculate New Grade
        simp_fk = textstat.flesch_kincaid_grade(final_simplified_paragraph)
        
        orig_grades.append(orig_fk)
        simp_grades.append(simp_fk)
        
        if final_simplified_paragraph != text:
            successful_swaps += 1
            print(f"   ✅ Successfully simplified!")
            print(f"   📉 Grade Drop: {orig_fk:.1f} -> {simp_fk:.1f}")
        else:
            print(f"   ⚠️ Unchanged (Bouncer rejected all AI options)")
            
    except Exception as e:
        print(f"   ❌ Connection failed. Error: {e}")
        break

end_time = time.time()
execution_time = round(end_time - start_time, 2)

# ==========================================
# 📊 CALCULATE FINAL CONFERENCE METRICS
# ==========================================
if orig_grades and simp_grades:
    avg_orig = sum(orig_grades) / len(orig_grades)
    avg_simp = sum(simp_grades) / len(simp_grades)
    grade_drop = avg_orig - avg_simp
    
    print("\n✅ ==========================================")
    print("🏆 PARAGRAPH-LEVEL METRICS REPORT")
    print("==========================================")
    print(f"⏱️ Total Execution Time:  {execution_time} seconds")
    print(f"🔄 Paragraphs Processed:  {successful_swaps}/{len(dataset)}")
    print("------------------------------------------")
    print(f"📉 Avg. Original FK Grade:   {avg_orig:.2f} (University Level)")
    print(f"📉 Avg. Simplified FK Grade: {avg_simp:.2f}")
    print(f"🔥 Total Reading Grade Drop: -{grade_drop:.2f} Grades!")
    print("==========================================\n")