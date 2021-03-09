import pymongo
import webbrowser

def insert_entry(document):
    inner_dict = {}
    key = input("What is the key? \n")
    desc = input("What is the description? \n")
    ans = input("Any subentries? [y/n]\n")
    while ans.lower() == "y":
        Key = input("Key?\n")
        Desc = input("Description?\n")
        inner_dict[Key] = (Desc, {})
        ans = input("Any more subentries? [y/n]\n")
    dict = {"Key": key,
            "Value": (desc, inner_dict)}
    document.insert_one(dict)
    print("Inserted: ", dict, "\n")


if __name__ == "main":
    client = pymongo.MongoClient(
        "mongodb+srv://devmrfitz:KD2mPyL5QpmjiRVN@cluster0.nyxmm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
    db = client['main']
    document = db.database
    while True:
        ans = input("""Choose an option:
        1) Insert an entry
        2) Modify an entry \n""")
        if ans == "1":
            insert_entry(document)
        elif ans == "2":
            webbrowser.open("http://www.quickmeme.com/img/f5/f54bc7a9503b3f636e43c61c946d746eb2270f671b98886657e8ab64d9f2261b.jpg")
        else:
            break
