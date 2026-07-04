import requests
import time
import textstat
from datasets import load_dataset
import pandas as pd
import warnings

# Suppress HuggingFace warnings for a clean terminal output
warnings.filterwarnings("ignore")

API_URL = "http://127.0.0.1:5000/simplify"

def run_lexify_benchmark(dataset_name, dataset_records, num_to_test):
    orig_grades = []
    simp_grades = []
    sari_scores = []
    successful_swaps = 0

    print(f"\n🚀 ==================================================")
    print(f"🚀 STARTING MASSIVE BENCHMARK: {dataset_name.upper()}")
    print(f"🚀 Processing {num_to_test} Sentences...")
    print(f"==================================================\n")
    
    start_time = time.time()

    for i in range(num_to_test):
        if isinstance(dataset_records, pd.DataFrame):
            complex_text = str(dataset_records.iloc[i]['original'])
            human_reference = str(dataset_records.iloc[i]['simplifications'])
        else:
            complex_text = dataset_records[i]['original']
            human_reference = dataset_records[i]['simplifications'][0]
        
        # FIX 1: Print EVERY sentence so you know it's not stuck!
        print(f"🔄 Processing [{i+1}/{num_to_test}]...")
        
        orig_fk = textstat.flesch_kincaid_grade(complex_text)
        
        try:
            response = requests.post(API_URL, json={
                "text": complex_text, 
                "reference": human_reference
            }, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                simplified_text = result.get("simplified", complex_text)
                
                # FIX 2: Added the tracking logic back in!
                simp_fk = textstat.flesch_kincaid_grade(simplified_text)
                orig_grades.append(orig_fk)
                simp_grades.append(simp_fk)
                
                sari = result.get("sari_score", 0)
                if sari != "N/A" and float(sari) > 0:
                    sari_scores.append(float(sari))
                
                if simplified_text != complex_text:
                    successful_swaps += 1
                    print(f"   ✅ Simplified! Grade: {orig_fk:.1f} -> {simp_fk:.1f}")
                else:
                    print(f"   ⚠️ Kept Original (No safe swaps found)")
                    
            else:
                print(f"  ❌ API Error {response.status_code}. Server said: {response.text[:50]}")
                
        except Exception as e:
            print(f"  ⚠️ Request failed: {e}")
            continue 

    end_time = time.time()
    execution_time = round((end_time - start_time) / 60, 2)

    # --- CALCULATE FINAL METRICS ---
    if orig_grades and simp_grades:
        avg_orig = sum(orig_grades) / len(orig_grades)
        avg_simp = sum(simp_grades) / len(simp_grades)
        grade_drop = avg_orig - avg_simp
        
        avg_sari = sum(sari_scores) / len(sari_scores) if sari_scores else 0
        success_rate = (successful_swaps / num_to_test) * 100
        
        # 1. Create the text block
        final_report = (
            f"\n✅ ==========================================\n"
            f"🏆 FINAL REPORT: {dataset_name.upper()}\n"
            f"==========================================\n"
            f"⏱️ Total Execution Time:  {execution_time} minutes\n"
            f"🔄 Texts Processed:       {successful_swaps}/{num_to_test} ({success_rate:.1f}% Success Rate)\n"
            f"------------------------------------------\n"
            f"📉 Avg. Original FK:      {avg_orig:.2f}\n"
            f"📉 Avg. Simplified FK:    {avg_simp:.2f}\n"
            f"🔥 Total Grade Drop:      -{grade_drop:.2f} Grades!\n"
            f"------------------------------------------\n"
            f"🌟 Average SARI Score:    {avg_sari:.2f} / 100\n"
            f"==========================================\n"
        )
        
        # 2. Print it to the screen like normal
        print(final_report)
        
        # 3. CRITICAL FIX: Save it permanently to a text file!
        with open("lexify_final_results.txt", "a", encoding="utf-8") as file:
            file.write(final_report)
            print("💾 Results successfully saved to 'lexify_final_results.txt'!")
            
    else:
        print("❌ Evaluation failed. No grades were recorded.")

# ==========================================
# 2. RUN WIKILARGE DATASET (1,000 Samples)
# ==========================================
print(f"\n📥 Downloading 1,000 samples from the 'WikiLarge' Dataset...")

# We load exactly 1,000 sentences from the massive training split!
wikilarge = load_dataset("waboucay/wikilarge", "original", split="train[:1000]", trust_remote_code=True)

# Format it into a Pandas DataFrame so our function can read it
wiki_df = pd.DataFrame({
    'original': wikilarge['complex'],
    'simplifications': wikilarge['simple']
})

# Run the benchmark on our custom 1,000 sentence slice!
run_lexify_benchmark("WikiLarge Corpus (1,000 Samples)", wiki_df, 1000)