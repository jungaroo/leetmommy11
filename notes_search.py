import requests
import pandas as pd
import bs4
import re
import argparse
import sys

# Create the command-line argument. Which is just a single word
parser = argparse.ArgumentParser(
    description="Searches for the given word in Rithm 11 notes.")
parser.add_argument('word', help="Word to search for in files.")

# Show the help if no arguments are given
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit()

# Get the word
args = vars(parser.parse_args())
word = args['word']
print(f"Searching for the word: {word}")

BASE_URL = "http://curric.rithmschool.com/r11/lectures/"

# Search
response = requests.get(BASE_URL)
soup = bs4.BeautifulSoup(response.text, features='html5lib')

# First grab all the href links for the lectures
html_links = soup.find_all('a', href=True)
links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]

# search for the word
for link in links:
    response = requests.get(BASE_URL + link)
    soup = bs4.BeautifulSoup(response.text, features='html5lib')
    if word in soup.text:  # regular expression
        print("Try checking in:", f"{BASE_URL}{link}")
else:
    print("Done searching.")
