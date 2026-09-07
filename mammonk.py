import requests
import json
import sqlite3
import config
import time

# ======================= TODO: =======================
# andare a dormire

# Openlibrary books are not being processed correctly, I think.

# Access to Google Books API, because all my requests are being blocked.



# ======================= REQUESTS, PARSING & NORMALIZATION ======================= 

# This function receives as input a an endpoint source and a book isbn,
# makes a request for the data of the book to the site,
# then normalizes the request's return data,
# and finally returns the processed, normalized book data
def fetch_book_data(source, isbn, recursion_count):
    url = source["url"]

    # Make a request "r" and receive back a response object
    r = requests.get(url, headers=config.HEADERS)
    
    error_isbn_text = f"Couldn't retrieve book {isbn}."
    error_code_text = f"Error code: {r.status_code}."

    # ------- ERROR HANDLING ------- 
    if r.status_code == 429: # "switch" statement
    # Too many requests in a short time span
        if recursion_count >= 3:
            print(f"Too many calls to {source['name'].strip('[]')}. Skipping {isbn}.")
            return None

        print(f"[{source['name']}] rate limited. Backing off...")
        time.sleep(2)  # Pause to respect API rate boundaries
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
        print(f"Request failed with code: f{r.status_code}")
        return None          
    

    # Parse and normalize data depending on the source site
    data = r.json()
    extracted = source['parser'](data)
    #if extracted and None in extracted.values():
    #    return None
           
    return extracted

# --- PARSING & NORMALIZATION FUNCTIONS ---

def parse_openlibrary(data):        
    try:
        return {
            "title": data.get("title"),
            "publishers": data.get("publishers", ["N/A"])[0]
        }
    except (KeyError, IndexError):
        return None
 

def parse_google_books(data):
    try:
        volume = data['items'][0]['VolumeInfo']
        return {
            "title": volume.get("title"),
            "publishers": volume.get("publishers", ["N/A"])[0]
        }
    except (KeyError, IndexError):
        return None

    
# ======================= MAIN =======================

def main():
    ISBNs = config.ISBNs
    
    # ------- Main Loop -------
    for isbn in ISBNs: #debug
    #while True: #RESTORE

        # ------- Scanning -------
        # Get input from barcode scanner
        print("Waiting for scan...")
        #isbn = input() #RESTORE
        print(f"Scanned: {isbn}.")

        endpoints = [
            {
                "name": "Openlibrary",
                "url": f"https://openlibrary.org/isbn/{isbn}.json",
                "parser": parse_openlibrary
            },
            {
                "name": "Google Books",
                "url": f"https://www.googleapis.com/books/v1/volumes?q={isbn}",
                "parser": parse_google_books
            }
        ]


        # --------- Data Processing ---------
        for source in endpoints:
            recursion_count = 0
            #FIXME: cycles through whole urls for each isbn, even though book was found 
            extracted = fetch_book_data(source, isbn, recursion_count)

            if not extracted:
                continue

            # Append extracted data to .json file
            with open("bookdata.json", "w"): #FIXME: it doesn't append
                json.dumps(extracted)


            print(extracted)
    

        print("\n-----------------\n")

    # out of the loop
            

if __name__ == "__main__":
    main()


# ~~~~~~~~~~ NOTES TO SELF: ~~~~~~~~~~

# 2026-09-02
# I have been coding in C lately;
# first time properly coding in python (without AI).
# Python is so criminally simple that it is hard.
# OK, now it's just criminally hard

# 2026-09-07
# I feel in the stream
# Even though I used AI and feel a bit guilty about it,
# I could have easily relied on it much more than I did.
# I think I am starting to get the gist of it  