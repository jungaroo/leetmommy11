import requests
import bs4
import re
import argparse
import sys
import asyncio


BASE_URL = "http://curric.rithmschool.com/r11/lectures/"

async def search_links(link, word):
    """ Asynchronously searches for word in the link """
    response = requests.get(BASE_URL + link)
    soup = bs4.BeautifulSoup(response.text, features='html5lib')
    if word in soup.text: 
        print("Try checking in:", f"{BASE_URL}{link}")

async def get_all_links():
    """ Asynchronously searches for all links """
    response = requests.get(BASE_URL)
    soup = bs4.BeautifulSoup(response.text, features='html5lib')

    # First grab all the href links for the lectures
    html_links = soup.find_all('a', href=True)
    links = [a['href'] for a in html_links if not a['href'].endswith('.zip')][1:]
    return links

async def main():
    """
    Command line script to search through notes.
    Usage:
    python3 notes_search.py [word]

    word is a word to search for.
    """
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


    # Grab all links
    links = await get_all_links()

    # search for the word
    await asyncio.gather(*[search_links(link, word) for link in links])
    
    print("Done searching.")

if __name__ == "__main__":
    asyncio.run(main())