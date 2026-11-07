import json
from time import sleep

import requests

import config


# ======================= HELPERS =======================

# Returns the first element of a list, or None if it's not a list / it's empty
def first(lst):
    if isinstance(lst, list) and lst:
        return lst[0]
    return None


# Makes a GET request and returns the parsed JSON (a dict), or None on any failure
def makeRequest(url, params=None):
    try:
        r = requests.get(url, params=params, headers=config.HEADERS, timeout=10)
        print(r.status_code, r.url)
        if r.status_code != 200:
            return None
        return r.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        # ValueError covers JSONDecodeError (e.g. HTML instead of JSON)
        print(f"Request failed: {e}")
        return None


# ======================= REQUESTS & PARSING =======================

def fetch_book_data(source, isbn, recursion_count=0):
    r = requests.get(source["url"], headers=config.HEADERS,
                     params=source.get("params"), timeout=10)
    if source["name"] == "Google Books":
        sleep(1)

    if r.status_code == 429:
        if recursion_count >= 3:
            print(f"Too many calls to {source['name']}. Skipping {isbn}.")
            return None
        print(f"[{source['name']}] rate limited. Backing off...")
        sleep(2)
        return fetch_book_data(source, isbn, recursion_count + 1)
    elif r.status_code == 404:
        print(f"{source['name']}: book {isbn} not found.")
        return None
    elif r.status_code != 200:
        print(f"{source['name']}: request failed with code {r.status_code}.")
        return None

    try:
        data = r.json()
    except ValueError:
        print(f"{source['name']}: response is not JSON.")
        return None

    extracted = source["parser"](data, source)
    if extracted:
        print(f"Parsed with {source['name']}.")
    return extracted


# Needs the edition data already downloaded, so it only makes 2 more requests
def fetchAuthorOpenlibrary(source, edition):
    work_key = (first(edition.get("works")) or {}).get("key")
    if not work_key:
        return None

    work = makeRequest(f"{source['base_url']}{work_key}.json")
    if not work:
        return None
    sleep(1)

    entry = first(work.get("authors")) or {}
    author_key = (entry.get("author") or {}).get("key")
    if not author_key:
        return None

    author = makeRequest(f"{source['base_url']}{author_key}.json")
    if not author:
        return None

    return author.get("personal_name") or author.get("name")


# --- PARSERS: every parser returns the same keys, or None on failure ---

def parse_openlibrary(data, source):
    name = fetchAuthorOpenlibrary(source, data)
    if not name:
        print("Open Library: author not found.")
        return None  # treated as failure -> next source is tried

    lang_key = (first(data.get("languages")) or {}).get("key", "")

    return {
        "title": data.get("title"),
        "authors": [name],
        "publishers": first(data.get("publishers")) or "N/A",
        "language": lang_key.split("/")[-1] or None,
    }


def parse_google_books(data, source):
    volume = (first(data.get("items")) or {}).get("volumeInfo")
    if not volume:
        print("Google Books: no volume found.")
        return None

    return {
        "title": volume.get("title"),
        "authors": volume.get("authors") or [],
        "publishers": volume.get("publisher") or "N/A",  # a string, not a list
        "language": volume.get("language"),
    }


def parse_opac_sbn(data, source):
    extracted = {
        "title": data.get("briefRecords")[0].get("titolo"),
        "authors": data.get("briefRecords")[0].get("autorePrincipale"),
        "publishers": data.get("briefRecords")[0].get("pubblicazione"),
        "language": data.get("facetRecords")[5].get("facetValues")[0][1]
    }
    return extracted 

# ======================= MAIN =======================

def main():
    key = config.key
    jsonfile = "bookdata.json"

    # Check if jsonfile exists, then load it to python as a dict. Else, create an empty dict
    try:
        with open(jsonfile, "r") as f:
            library = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        library = {}

    # --- Main loop: scan books ---
    while True:
        print("Waiting for scan...")
        isbn = input().strip()
        if not isbn:
            continue
        print(f"Scanned: {isbn}.")

        if isbn in library:
            print("Already in library, skipping.")
            continue

        endpoints = [
            {
                "name": "Openlibrary",
                "base_url": "https://openlibrary.org",
                "url": f"https://openlibrary.org/isbn/{isbn}.json",
                "parser": parse_openlibrary,
                "params": None,
            },
            {
                "name": "Google Books",
                "url": "https://www.googleapis.com/books/v1/volumes",
                "parser": parse_google_books,
                "params": {"q": f"isbn:{isbn}", "key": key},
            },
            {
                "name": "OPAC SBN",
                "url": "https://opac.sbn.it/opacmobilegw/search.json",
                "params": {
                    "isbn": isbn,
                },
                "parser": parse_opac_sbn,
            }
        ]

        # Safety net: a problem with one book must not kill the whole program
        try:
            # --- EXTRACTION & PARSING 
            for source in endpoints:
                extracted = fetch_book_data(source, isbn)
                if not extracted:
                    continue

                library[isbn] = extracted
                print(extracted)

                # Update jsonfile
                with open(jsonfile, "w") as f:
                    json.dump(library, f, indent=4)
                break
            else:
                print(f"Data extraction failed for {isbn}.")
        except Exception as e:
            print(f"Unexpected error on {isbn}: {e!r}")

        print("\n--------------\n")


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
# that I am trying write the script to communicate with higher deities.
# I am grasping the object philosophy but boy is it different.

# 2026-11-07
# Project ended. I was able to do some work by myself with the Openlibrary parser part.
# The majority of the code was written by AI, though.