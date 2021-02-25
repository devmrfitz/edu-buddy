

from googlesearch import search


def reply(msg):
    if (msg[0] == "/"):
        if (msg == "/start"):
            reply = "hey there, let's get started"
        elif ("/search" in msg):
            reply = "Sure!, here you go: "
            query = msg
            query = "https://www.iiitd.ac.in:" + query.replace("/search", "")
            for j in search(query, tld="co.in", num=1, stop=1, pause=1):
                reply = reply + j
            return reply
        elif (msg == "/help"):
            reply = "have a look at our documentations"
        else:
            reply = "lemme have a look..."
    elif msg.lower() == "thanks":
        reply = "no problem"
    else:
        line = execute(msg)
        try:
            if type(line) is int:
                x = "app/data/data" + str(line) + ".txt"
                f = open(x, "r")
                line = f.read()
                f.close()
            reply = line
        except:
            reply = "Unsupported"

    if reply is None:
        reply = ""
    return reply


from nltk.stem import PorterStemmer
import spacy
from nltk.corpus import stopwords
import re
import nltk

nltk.download('stopwords')


def clean(text):
    text = re.sub('[0-9]+.\t', '', str(text))
    text = re.sub('\n ', '', str(text))
    text = re.sub('\n', ' ', str(text))
    text = re.sub("'s", '', str(text))
    text = re.sub("-", '', str(text))
    text = re.sub("— ", '', str(text))
    text = re.sub('\"', '', str(text))
    text = re.sub(',', '', str(text))
    text = re.sub("Mr\.", 'Mr', str(text))
    text = re.sub("Mrs\.", 'Mrs', str(text))
    text = re.sub("[\(\[].*?[\)\]]", "", str(text))

    return text


def sentences(text):
    text = re.split('[!.?]', text)
    clean_sent = []
    for sent in text:
        clean_sent.append(sent)
    return clean_sent


def stop_words(text):
    stop_words = set(stopwords.words("english"))
    filter_sentence = [i for i in text.split() if not i in stop_words]
    print(filter_sentence)
    return stemmer(filter_sentence)


def stemmer(filter_sentence):
    sentence = ""
    ps = PorterStemmer()
    for i in filter_sentence:
        sentence += str(ps.stem(i)) + " "
    sentence.strip()
    return sentence


def execute(text):
    nlp = spacy.load('en_core_web_sm')
    sentence = stop_words((clean(text)))
    doc = nlp(sentence)
    insight = []
    for token in doc:
        if token.pos_ == "NOUN":
            insight.append(token.text)
        elif token.pos_ == "ADJ":
            insight.append(token.text)
    print(insight)
    if (len(insight) == 0):
        return None
    index = searching(insight)
    line = None
    if (index != None):
        line = index
    else:
        line = "Sorry, I didn't understand. Rephrase and ask again"
    return line


def searching(mylist):
    insights = mylist
    # insights = ["tell","cricket", "stadium"]

    game = ["game", "centre", "gaming", "gamer", "games", "gam"]  # 0
    library = ["lib", "library", "libraries", "books", "book", "sit", "sitting area", "area", "libs"]  # 1
    infrastruture = ["infra", "buildings", "building", "build", "built", "many", "height", "block", "blocks"]  # 2
    field = ["ground", "field", "cricket", "stadium", "stadiums", "courts", " basketball", "infrastruture"]  # 3
    incubation = ["incubation", "incube", "incub", "centre", "center", "benifits", "benifit", "special"]  # 4
    swimpool = ["swim", "swimming", "pool", "pools", "water", "backstroke"]  # 5
    edubuddy = ['edubuddy', "education", "edubuddi", 'lecture', "lectur", "googl", 'download', 'help', 'lectures',
                'iiitd', 'classroom', 'google', 'syllabus', 'course']  # 6

    checklist = [game, library, infrastruture, field, incubation, swimpool, edubuddy]

    matches = [0, 0, 0, 0, 0, 0, 0]
    for u in insights:
        for j in checklist:
            for k in j:
                if u == k:
                    matches[checklist.index(j)] += 1
                    break

    index_max = max(range(len(matches)), key=matches.__getitem__)

    match_percentage = matches[index_max] / len(insights)
    if (match_percentage >= 0.5):
        return index_max
