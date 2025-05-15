
import requests
import csv
import logging
from pathlib import Path
import re
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("PONS_API_KEY")
DICTIONARY = 'deen'  # German ⇄ English
INPUT_FILE = 'german_vocab.txt'
OUTPUT_FILE = 'anki_cards.tsv'

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def clean_headword(word):
    # Remove pipes, middots, and extra whitespace
    return re.sub(r'[|·]', '', word).strip()

def lookup_word(word):
    url = "https://api.pons.com/v1/dictionary"
    headers = {"X-Secret": API_KEY}
    params = {
        "q": word,
        "l": DICTIONARY,
        "in": "de",
        "ref": "true",
        "fm": "1"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch '{word}': {response.status_code}")
        return None

    data = response.json()
    if not data or not data[0].get("hits"):
        logging.info(f"No results found for '{word}'")
        return None

    try:
        rom = data[0]["hits"][0]["roms"][0]
        raw_headword = rom.get("headword", word)
        headword = clean_headword(raw_headword)
        wordclass = rom.get("wordclass", '')

        translations = []
        sources = []
        for arab in rom["arabs"]:
            for trans in arab.get("translations", []):
                source = trans.get("source", "").strip()
                target = trans.get("target", "").strip()
                if target:
                    sources.append(source)
                    translations.append(target)


        return {
            "headword": headword,
            "part_of_speech": wordclass,
            "translations": list(set(translations)),
            "sources": list(set(sources))
        }

    except (KeyError, IndexError) as e:
        logging.error(f"Parse error for '{word}': {e}")
        return None

def html_list(items):
    return '<br>• ' + '<br>• '.join(items)

def html_block(items):
    return '<br>'.join(items)

# --- Main ---
def generate_flashcards():
    output_rows = []

    with open(INPUT_FILE, encoding="utf-8") as file:
        for line in file:
            if "-" not in line:
                continue

            germanEntry, english = map(str.strip, line.strip().split("-", 1))
            german = ''
            if germanEntry.find('+') >= 0:
                german = germanEntry.split(' + ')[0]
            else:
                german = germanEntry
            
            logging.info(f"Looking up '{german}'")

            info = lookup_word(german)
            if info:
                front = f"<strong>{germanEntry.replace(' + ', ', ')}</strong> <br><br> <span style='font-size:75%'>{info['headword']} ({info['part_of_speech']}) {html_list(info['sources'])}</span>"

                back = english + "<br><br> <span style='font-size:75%'>" + "Automated translations:" + html_list(info['translations']) + "</span>"

            else:
                front = german
                back = english

            output_rows.append([front, back])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(output_rows)

    logging.info(f"Done! Cards saved to {OUTPUT_FILE}")

# --- Run ---
if __name__ == "__main__":
    generate_flashcards()
