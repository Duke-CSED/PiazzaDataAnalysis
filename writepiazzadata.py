import csv
import dataparse
from question import Question

csv_header = ["Question ID",
              "Question Subject", "Question Content",
              "Question Tag 1", "Question Tag 2",
              "Tags Agree?", "Timestamp"]

data_path = "./data"

class_content_files = dataparse.getFilesWithName("class_content", ".json",
                                                 data_path)
user_files = dataparse.getFilesWithName("users", ".json", data_path)

#dataparse.printReadableJSONFile(dataparse.getJSONData(class_content_files[4]))

substitutions = [  # All of the wacky formatting stuff from the Piazza data
    ("&#39;", "\'"),
    ("<p>", " "),
    ("</p>", " "),
    ("<li>", " "),
    ("</li>", " "),
    ("&#64;", "@"),
    ("&#34;", "\""),
    ("<b>", " "),
    ("</b.", " "),
    ("<ul>", " "),
    ("</ul>", " "),
    ("&amp;", "&"),
    ("&lt;", "<"),
    ("&gt;", ">"),
    ("&#43;", "+"),
    ("<pre>", " "),
    ("</pre>", " "),
    ("\\u00a0", ""),
    ("URL:Â <a href=", " "),
    ("</a>", " "),
    ("URL:Â ", " "),
    ("Â", " "),
    ("\xa0", " "),
    ("\n", " "),
    ("\'", "'")
]


def getQuestion(item):
    question = Question()
    question.q_id = item['id']
    question.subject = item['history'][0]['subject']
    question.content = item['history'][0]['content']
    question.student_id = item['history'][0].get('uid',
                                                  item['history'][0].get(
                                                      'id',
                                                    "Not found"
                                                  ))
    if question.student_id == "Not found":
        pass
    question.tag = "Incomplete tag"
    question.tag2 = "Incomplete tag"
    question.time = item['history'][0]['created']
    question.upvotes = len(item['tag_good'])
    question.content = dataparse.cleanText(
        question.content, substitutions)
    return question


def getChildren(item):
    children = []
    for entry in item['children']:
        try:
            question = Question(q_id=entry['id'],
                                student_id=entry.get('uid', "None"),
                                content=entry.get('subject', "None"),  # Apparently replies are encoded as subject?
                                time=entry['created']
                                )
        except KeyError:
            print("KeyError", entry.keys())
            question = Question()
        question.content = dataparse.cleanText(question.content)
        children.append(question)
        if len(entry["children"]) > 0:
            children.extend(getChildren(entry))
    return children


def getQuestions(class_content_files):
    """
    Gets the relevant data from each element of the list of Piazza entries
        in each class_content.json file
    :param class_content_files:
    :return:
    """
    all_questions = []
    for path in class_content_files:
        json_data = dataparse.getJSONData(path)  # This data should be a list
        if not isinstance(json_data, list):  # If it isn't, we'll throw an error
            print("JSON Data returned is in the wrong format. It should be a"
                  "list of dictionaries representing Piazza questions")
            raise ValueError
        for i, item in enumerate(json_data):
            if i < 5:
                continue
            #dataparse.printReadableJSONFile(item['children'])
            current_question = getQuestion(item)
            current_question.followups = [
                dataparse.cleanText(x.content, substitutions) for x in getChildren(item)]
            current_question.followups = [dataparse.cleanText(x, substitutions) for x in current_question.followups if x != "None"]
            if i == 62:
                current_question.content = "Extra credit assignment submission" \
                                   " -- that super annoying one " \
                                   "that messes up the spreadsheet"
            all_questions.append(current_question)
    return all_questions

# --------------
# BODY
# --------------


piazza_questions = getQuestions(class_content_files)


master_student_list = []

for file in user_files:
    data = dataparse.getJSONData(file)
    for entry in data:
        entry['semester'] = dataparse.convertFileName(file)
    master_student_list.extend(data)
master_student_dict = {x['user_id']: x for x in master_student_list}
for question in piazza_questions:  # map student ids to our main csv
    temp = master_student_dict.get(question.student_id, {'name': "Not found"})
    question.student_name = temp['name']




# with open("class_content.csv", 'w') as outfile:
#     writer = csv.writer(outfile)
#     writer.writerow(csv_header)
#     for i, question in enumerate(piazza_questions):
#         writer.writerow(question.writeLine())



# printReadableJSONFile(getJSONData(class_content_files[0]))
