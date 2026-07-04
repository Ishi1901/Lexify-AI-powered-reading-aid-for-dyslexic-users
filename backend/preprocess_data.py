import pandas as pd

def clean_mwe_dataset():
    input_file = "final_MWE_dataset.tsv"
    output_file = "training_data.csv"
    
    print(f"Reading your dataset: {input_file}...")
    
    # Read the TSV file
    df = pd.read_csv(input_file, sep='\t')
    df = df[['Expression', 'Complex_binary']].copy()
    df = df.dropna()
    
    new_rows = []
    
    # NEW LOGIC: Instead of throwing phrases away, we split them into single words!
    for index, row in df.iterrows():
        phrase = str(row['Expression']).lower()
        label = row['Complex_binary']
        
        # Split the phrase by spaces
        words = phrase.split()
        
        for w in words:
            # Clean the word of any weird punctuation
            clean_w = "".join(filter(str.isalpha, w))
            
            # Only keep words that are 3 letters or longer (ignores 'a', 'to', 'on')
            if len(clean_w) > 2:
                new_rows.append({'word': clean_w, 'label': label})
                
    # Convert back to a dataframe and remove duplicate words
    new_df = pd.DataFrame(new_rows)
    new_df = new_df.drop_duplicates(subset=['word'])
    
    # Save it as the final training_data.csv
    new_df.to_csv(output_file, index=False)
    
    print(f"✅ Scrubbing Complete!")
    print(f"Usable single words extracted for training: {len(new_df)}")
    print(f"Saved perfectly formatted data to: {output_file}")

if __name__ == "__main__":
    clean_mwe_dataset()