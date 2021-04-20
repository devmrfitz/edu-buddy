import pprint
pp = pprint.PrettyPrinter(indent=4)

data_file_loc = 'data/course_ids'

with open(data_file_loc, 'r') as f:
    current = eval(f.read())

course = input("Please enter course ID:")
# Check if course already exists
found = False
for i in current:
    if i['course_id'] == course:
        print("Course found.")
        print("Pre-existing topic IDs are:")
        for j in i['topic_ids']:
            print(j, end="\t")
        print()
        topic = str(input("Please enter your topic ID:"))
        if topic not in i['topic_ids']:
            i['topic_ids'].append(topic)
        found = True
        break
if not found:
    print("Creating new course")
    topic = input("Please enter your topic ID:")
    current.append(dict(course_id=str(course), topic_ids=[str(topic)]))

with open(data_file_loc, 'w') as f:
    f.write(pp.pformat(current))

print("Operation successful. Please commit submit pull request.")
