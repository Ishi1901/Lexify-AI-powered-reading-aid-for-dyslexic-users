import urllib.request
import json

# The URL where your Flask server is listening
url = "http://127.0.0.1:5000/simplify"

# The highly academic test paragraph
text_to_simplify = "The weary traveler sought immediate refuge as the tempestuous weather rapidly approached the coastal village. Although the local inhabitants frequently warned visitors about the unpredictable climate, he had underestimated the severity of the impending storm. The turbulent winds began to violently agitate the surrounding vegetation, creating a cacophony of sound. Fortunately, he discovered a sturdy structure that provided sufficient protection from the torrential downpour. He remained there until the hazardous conditions finally subsided."

# The "Gold Standard" human translation for the SARI metric
human_reference = "The tired traveler looked for quick shelter as the severe weather quickly neared the seaside town. Even though the local people often warned guests about the changing weather, he guessed wrong about the strength of the coming storm. The rough winds began to strongly shake the nearby plants, making a loud noise. Luckily, he found a strong building that gave enough cover from the heavy rain. He stayed there until the dangerous weather finally ended."
data = json.dumps({
    "text": text_to_simplify,
    "reference": human_reference
}).encode("utf-8")

# Creating the request
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

print("Sending text to backend...")

try:
    # Sending the request and reading the response
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        
        print("\n✅ SUCCESS! Here is what the backend returned:")
        print("-" * 60)
        print(f"📚 Original Text: {text_to_simplify}")
        print(f" General Level: {result['original_grade']}")
        print(f" Flesch Reading Ease: {result['fk_ease_original']} / 100 (Higher is easier)")
        print(f" Flesch-Kincaid Grade: {result['fk_grade_original']}")
        print("-" * 60)
        print(f"✨ Simplified Text: {result['simplified']}")
        print(f" General Level: {result['simplified_grade']}")
        print(f" Flesch Reading Ease: {result['fk_ease_simplified']} / 100 (Higher is easier)")
        print(f" Flesch-Kincaid Grade: {result['fk_grade_simplified']}")
        print("-" * 60)
        
        # 📚 NEW: Print the Glossary!
        if result.get('glossary'):
            print(" Glossary of Swapped Words:")
            for item in result['glossary']:
                print(f"   • {item['original']} ➔ {item['simplified']}")
            print("-" * 60)
            
        print(f"🏆 SARI Score: {result['sari_score']} / 100")
        print("-" * 60)
        
except Exception as e:
    print("\n❌ ERROR: The backend crashed or isn't running.")
    print("Error details:", e)