from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
import spacy
from spacy import displacy
import searchmodule
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re

def clean(text):
    text = re.sub('[0-9]+.\t', '', str(text))
    text = re.sub('\n ', '', str(text))
    text = re.sub('\n', ' ', str(text))
    text = re.sub("'s", '', str(text))
    text = re.sub("-", '', str(text))
    text = re.sub("— ", '', str(text))
    text = re.sub('\"', '', str(text))
    text = re.sub(',','',str(text))
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
    stop_words = set(stopwords.words("English"))
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
    insight =[]
    for token in doc:
        if token.pos_=="NOUN":
            insight.append(token.text)
        elif token.pos_ =="ADJ":
            insight.append(token.text)
            
    if(len(insight)==0):return None
    index = searchmodule.searching(insight)
    print(index)
    line = None
    if(index!= None):
        if index == 8:
            line = "Check out EduBuddy: " + "https://edu-buddy.herokuapp.com/"
        else:
            line = index
            # y = str(index)
            # x = "data"+ str(index) +".txt"
            # f = open(x, "r")
            # line = f.read()
            # f.close() 
    else:
        line = "Sorry, I didn't understand. Rephrase and ask again"
    print(line)   
    return line


