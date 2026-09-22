import requests
import config
import json
import time

def main():
    isbn = config.ISBNs[0]
    endpoints = [
        {
            "name": "Openlibrary",
            "base_url": "https://openlibrary.org",
            "url": f"https://openlibrary.org/isbn/{isbn}.json",
            "params": {}
        },
        {
            "name": "Google Books",
            "url": f"https://www.googleapis.com/books/v1/volumes",
            "params": {
                "q": f"{isbn}",
                "key": config.key
                }
                
        }
    ]

    for source in endpoints:
        if source == endpoints[1]:
            continue
        
        """  url = source.get("url")

        r = requests.get(url, params=source.get("params"), headers=config.HEADERS)

        print(r.status_code)
        print(r.url)
        data = r.json()
        print(data)

        with open("prova.json", "w") as f:
            json.dump(data, f)"""
        
        print("-----------------------\n")

        time.sleep(2)

        #url2 = f"{source.get("base_url")}{data.get("works")[0].get("key")}" 
        url2 = "https://openlibrary.org/works/OL27482W"
        print(url2)

        r2 = requests.get(url=url2, headers=config.HEADERS)

        print(r2.status_code)
        print(r2.url)
         
         
        try:
            print(r2.json())
        except (requests.exceptions.JSONDecodeError):
            print("error")
            return

if __name__ == "__main__":
    main()

    