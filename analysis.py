import csv
import os
import dataparse as dp

import pandas as pd
import sqlite3 as sq
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import writepiazzadata as wp


connection = sq.connect("csdata.sqlite3")
cursor = connection.cursor()

with open("CreateAnalysisTables.sql", "r") as sql_file:
    sql_script = sql_file.read()

cursor.executescript(sql_script)
# df = pd.read_sql_query("SELECT * FROM all_data_tags WHERE semId = 8;", connection)
# df = df.drop(["id", "id:1", "postId:1", "semId:1", "id:2"], axis=1)

cursor.execute("SELECT * FROM all_data_tags WHERE semId = 8;")
names = [description[0] for description in cursor.description]

rows = []
for row in cursor.fetchall():
    row_dict = dict(
        zip(list(description[0] for description in cursor.description), row))
    rows.append(row_dict)


users2Questions = {}
for item in rows:
    if item['userId'] in users2Questions.keys():
        users2Questions[item['userId']]['questions'].append(item['content'])
        users2Questions[item['userId']]['tagNames'].append(item['tagName'])
    else:
        insert = {'grade': item['grade'],
                  'questions': [item['content'], ],
                  'tagNames': [item['tagName'],]}
        users2Questions[item['userId']] = insert

count = 0
for userId, dicti in sorted(users2Questions.items(), key= lambda x: x[0]):
    if dicti['grade'] != "Not found":
        # print(userId, len(dicti['questions']), dicti['tagNames'],
        #     dicti['grade'])
        count += 1

tags = [x['tagName'] for x in rows]
counts = np.asarray(np.unique(tags, return_counts=True)).T
total = sum([int(x[1]) for x in counts])
print("Total posts:", total)
for tup in counts:
    print(tup[0], tup[1], round(float(tup[1])/total, 2))

tag_range = np.arange(len(counts))
tag_names = [tup[0] for tup in counts]
tag_counts = [tup[1] for tup in counts]
tag_props = [round(float(tup[1]))/total for tup in counts]

plt.bar(tag_range, tag_counts, align='center', alpha=.5)
plt.xticks(tag_range, tag_names)
plt.ylabel('Number of questions tagged')
plt.title('Tagging')
plt.savefig("tags.png", bbox_inches='tight')
plt.show()


gradeFiles = dp.getFilesWithName("grades", ".csv",
                                 os.path.join("./data", "grades"))
grades = []
for gradeFile in gradeFiles:
    with open(gradeFile, "r") as file:
        reader = csv.reader(file)
        for line in reader:
            lineArray = line[5].split(",")
            line[5] = " ".join([lineArray[1], lineArray[0]])
            entry = {'name': line[5],
                     'netID': line[0],
                     'email': line[9],
                     'grade': line[10]}
            grades.append(entry)
count = 0
sp18_students = list(filter(lambda x: x['semester'] == 'sp18', wp.master_student_list))


def compareIgnoreMiddleName(name1, name2):
    name_array1 = name1.split(" ")
    name_array2 = name2.split(" ")
    if len(name_array1) == 3:
        short_name1 = [name_array1[0], name_array1[2]]
    else:
        short_name1 = name_array1
    if len(name_array2) == 3:
        short_name2 = [name_array2[0], name_array2[2]]
    else:
        short_name2 = name_array2
    map(lambda x: x.strip().lower(), short_name1)
    map(lambda x: x.strip().lower(), short_name2)
    return short_name1 == short_name2


for user in sp18_students:
    for entry in grades:
        if (user['name'] == entry['name'] or entry['email'] == user['email']
                or entry['netID'] in user['email'] or compareIgnoreMiddleName(user['name'], entry['name'])):
            user['grade'] = entry['grade']
            # print("Found grade for user {}".format(user))
            break
    if user.get('grade', None) is None:
        user['grade'] = "Not found"
        count += 1
        #print("NOT FOUND: USER ", count, user)
        #print(count, user['name'])

    else:
        #count += 1
        pass

user_frame = pd.DataFrame(sp18_students)

questioner_df = user_frame[(user_frame['asks'] >= 1) & (user_frame['grade'] != "Not found") & (user_frame['grade'] != "W")]
no_questions_df = user_frame[(user_frame['asks'] < 1) & (user_frame['grade'] != "Not found") & (user_frame['grade'] != "W")
                    & (user_frame['grade'] != "S") & (user_frame['grade'] != "D")]

questioner_grades = questioner_df['grade'].value_counts()
print()
question = {}
for tup in zip(questioner_grades.index, questioner_grades):
    question[tup[0]] = (tup[1], round(float(tup[1]) / sum(questioner_grades), 2))
    print(tup[0], question[tup[0]])
questioner_grades.plot(kind='bar')
plt.savefig("plot")

no_questioner_grades = no_questions_df['grade'].value_counts()
print()
no_question = {}
for tup in zip(no_questioner_grades.index, no_questioner_grades):
    no_question[tup[0]] = (tup[1], round(float(tup[1]) / sum(no_questioner_grades), 2))
    print(tup[0], no_question[tup[0]])
no_questioner_grades.plot(kind='bar')
plt.savefig("no_questions_plot")

prop_dict = {}

for item in question.keys():
    prop_dict[item] = [question[item][1],]
for item in no_question.keys():
    if prop_dict.get(item, None) is not None:
        prop_dict[item].append(no_question.get(item, (0, 0))[1])
    else:
        prop_dict[item] = [0, no_question['item'][1]]
for key, value in prop_dict.items():
    if len(value) == 1:
        prop_dict[key].append(0)
print(prop_dict)
# 0 index of list is people who asked questions, 1 index is not

prop_frame = pd.DataFrame(prop_dict)
prop_frame = prop_frame.T.sort_index(ascending=True)
prop_frame.rename(index=str, columns={0: "Question-Askers",
                                      1: "No Questions Asked"}, inplace=True)
prop_frame.plot(kind='bar', secondary_y='No Questions Asked')
plt.ylabel("Proportion of total grades")
plt.xlabel("Letter Grades")
plt.title("Proportion of grades at each letter rank, divided by question asking")
plt.savefig("compare")
plt.close()
print(user_frame.keys())
user_frame['askedquestion'] = np.where(user_frame['asks'] >= 1, "yes", "no")

gpa = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 1.0,
    "F": 0.0,
    "Not found": None,
    "W": None,
    "S": None
}

def getGPA(row):
    return gpa[row]


user_frame['gpa'] = user_frame['grade'].apply(getGPA)

print(user_frame.groupby("askedquestion")["gpa"].std())
print(user_frame.groupby("askedquestion").count())
plt.savefig("gpa")