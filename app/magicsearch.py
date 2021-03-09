from googlesearch import search
from urllib.request import urlopen
from bs4 import BeautifulSoup


def magic_search(query: str):
    for result in search(query + " site:quora.com", num=1, stop=1, pause=1):
        break
    if "https://www.quora.com" in result or "https://quora.com" in result:
        return \
            BeautifulSoup(urlopen(result).read(), features="html.parser").prettify().split(
                '"@type": "Answer", "text": "')[
                1].split("upvoteCount")[0][:-4].replace("\\u2019", "'").replace("\\n", "\n")
    else:
        return "The answer to this question is restricted to Area 51 employees (and possibly aliens)."


if __name__ == "__main__":
    print(magic_search(input("What's the query?\n")))