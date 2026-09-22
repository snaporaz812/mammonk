import requests
import json
#import sqlite3
import config
from time import sleep

# ======================= TODO: =======================
# Understand which OpenLibrary url contains the author

# Access to Google Books API, because all my requests are being blocked.

# Understand how sqlite3 could be useful in storing data

# When I enable the barcode scanner, put the scanned ISBNs into a queue list
# to elaborate a new http request when previous one has finished.
# Servono 2 programmi che lavorano separatamente? uno per il while-loop dello scanner
# e uno per gestire il processo di richiesta, formattazione e salvataggio?

# Further on (when not in debugging phase) check if isbn was already saved.
# If some fields are missing, try with the next url. If the next url fetches the needed fields,
# save them. Else discard the request.



# ======================= REQUESTS, PARSING & NORMALIZATION ======================= 

# This function receives as input an endpoint source (aka a site & its metadata) and a book isbn,
# makes a request for the data of the book to the site,
# formats it into json, then normalizes the request's return data,
# and finally returns the processed, normalized book data
def fetch_book_data(source, isbn, recursion_count):
    url = source["url"]

    # Make a request "r" and receive back a response object
    r = requests.get(url, headers=config.HEADERS, params=source.get("params"))
    if source.get("name") == "Google Books":
        sleep(1)
    
    error_isbn_text = f"Couldn't retrieve book {isbn}."
    error_code_text = f"Error code: {r.status_code}."

    # ------- ERROR HANDLING ------- 
    if r.status_code == 429: # "switch" statement
    # Too many requests in a short time span
        if recursion_count >= 3:
            print(f"Too many calls to {source.get("name").strip('[]')}. Skipping {isbn}.")
            return None

        print(f"[{source.get("name")}] rate limited. Backing off...")
        sleep(2)  # Pause to respect API rate boundaries
        return fetch_book_data(source, isbn, recursion_count+1)

    # Client error
    elif 400 <= r.status_code and r.status_code < 500:
        print("Client error.")
        print(error_isbn_text)
        print(error_code_text)
        return None
    # Server error
    elif 500 <= r.status_code and r.status_code < 600:
        print("Server error.")
        print(error_isbn_text)
        print(error_code_text)
        return None
    # Generic error
    elif r.status_code != 200:
        print(f"Request failed with code: {r.status_code}")
        return None          
    

    # Parse and normalize data depending on the source site
    data = r.json()
    extracted = source['parser'](data)
    print("Parsed!")
    """if extracted and None in extracted.values():
        return None"""
           
    return extracted


# --- PARSING & NORMALIZATION FUNCTIONS ---
# Parse the json-formatted book site data
# and returns a normalized dictionary

def parse_openlibrary(data):        
    try:
        isbn = data.get("isbn_13")[0]
        return {
            "title": data.get("title"),
            "isbn": isbn,
            #"authors": requests.get(url=f"https://openlibrary.org/isbn/{isbn}/", headers=config.HEADERS), # Manca il campo nella richiesta! Dove cazzo lo trovo io l'autore?
            "publishers": data.get("publishers", ["N/A"])[0],
            "language": data.get("languages")[0].get("key").split("/languages/")[1]
        }
    except (KeyError, IndexError):
        return None
 

def parse_google_books(data):
    try:
        volume = data['items'][0]['VolumeInfo']
        return {
            "title": volume.get("title"),
            "authors": volume.get("authors"),
            "publishers": volume.get("publisher", ["N/A"])[0],
            "language": volume.get("language")
        }
    except (KeyError, IndexError):
        return None

    
# ======================= MAIN =======================

def main():
    ISBNs = config.ISBNs
    key = config.key
    
    # ------- Main Loop -------
    for isbn in ISBNs: #debug
    #while True: #TODO: RESTORE to enable barcode scanner

        # ------- Scanning -------
        # Get input from barcode scanner
        print("Waiting for scan...")
        #isbn = input() #RESTORE
        print(f"Scanned: {isbn}.")

        endpoints = [
            {
                "name": "Openlibrary",
                "url": f"https://openlibrary.org/isbn/{isbn}.json",
                "parser": parse_openlibrary,
                "params": ""
            },
            {
                "name": "Google Books",
                "url": f"https://www.googleapis.com/books/v1/volumes",
                "parser": parse_google_books,
                "params": {
                    "q": f"isbn:{isbn}",
                    "key": key
                    }
            }
        ]


        # --------- Data Processing ---------
        for source in endpoints:
            recursion_count = 0

            extracted = fetch_book_data(source, isbn, recursion_count)

            if not extracted:
                continue

            # Append extracted data to .json file
            with open("bookdata.json", "w") as f:
                json.dump(extracted, f)


            print(extracted)

            break
            
    

        print("\n--------------\n")

    # out of the loop
            

if __name__ == "__main__":
    main()


# ~~~~~~~~~~ NOTES TO SELF: ~~~~~~~~~~

# 2026-09-02
# I have been coding in C lately;
# first time properly coding in python (without AI).
# Python is so criminally simple that it is hard.
# OK, now it's just criminally hard.

# 2026-09-07
# I feel in the stream
# Even though I used AI and feel a bit guilty about it,
# I could have easily relied on it much more than I did.
# I think I am starting to get the gist of it.

# 2026-09-21
# I feel completely lost because. It feels like far fewer words are needed,
# as if python does it all automatically, but at the same time I get the impression
# as if I am trying write the script to communicate with higher deities.
# I am grasping the object philosophy but boy is it different.