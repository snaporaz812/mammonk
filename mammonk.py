import requests
import json
import sqlite3

# ======================= TODO: =======================
# andare a dormire


    
# ======================= MAIN =======================

def main():
    # ------- Define Request Parameters -------
    HEADERS = {"User-Agent": "Mozilla/5.0"}

    isbns = [ #debug
                "9788807904783", # "il Coccodrillo", F. Dostoevskij, Feltrinelli, Italiano, 2024 o 2026,
                "9780261102217", # "The Hobbit", English #debug
                "9780679720201"  # "The Stranger", A. Camus, English #debug
            ]

    # ------- Main Loop -------
    for isbn in isbns: #debug
    #while True:

        # ------- Scanning  -------
        # Get input from barcode scanner
        print("Waiting for scan...")
        #isbn = input()
        print(f"Scanned: {isbn}.")
        
        isbn = isbn.strip()
        URLS = [f"https://www.googleapis.com/books/v1/volumes?q={isbn}", f"https://openlibrary.org/isbn/{isbn}.json"]

        for url in URLS:
            # Make a request to site and get a response object
            r = requests.get(url, headers=HEADERS)
            print(r.url)
                
            with open("bookdata.json", mode="w", encoding="utf-8") as wf:
                
                if r.status_code == 200: # Everything is alright
                    # Convert the contents of the Request object into a json object 
                    data = r.json()


                    # Normalize json entries           
                    extracted_info = {
                        "title": data.get("title"),
                        "publishers": data.get("publisher", ["N/A"])[0]
                    }

                    # Check if values are valid
                    if None in extracted_info.values():
                        continue

                    # Print book metadata to .json file
                    json.dump(extracted_info, wf, indent=4)
                    break
                    
                else:
                    print(f"Couldn't retrieve book {isbn}.")
                    print(f"Error: {r.status_code}.\n")
                    continue

        print("\n-----------------\n")
            


if __name__ == "__main__":
    main()


# ~~~~~~~~~~ NOTES TO SELF: ~~~~~~~~~~

# 2026-02-09
# I have been coding in C lately;
# first time properly coding in python (without AI).
# Python is so criminally simple that it is hard.
# OK, now it's just criminally hard