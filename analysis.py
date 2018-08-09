import csv
import os
import dataparse as dp
import analysis_utils as utils
import pandas as pd
import sqlite3 as sq
import matplotlib.pyplot as plt
plt.rcdefaults()
import numpy as np
import writepiazzadata as wp


figpath = "figs"

connection = sq.connect("analysis.sqlite3")
cursor = connection.cursor()

# Joins together posts and tags
utils.executeSQLFile("CreateAnalysisTables.sql", cursor)

# Gets all post data, including tags
posts = pd.read_sql_query("SELECT * FROM all_data_tags WHERE semId = 8;", connection)

# Maps each user's Piazza ID to some data about the questions
# they asked
users2Questions = utils.populateUsers2Questions(posts)

# Plotting the frequency of the different tags
posts['tagName'].value_counts(normalize=True).plot(kind='bar', )
plt.ylabel('Proportion of questions tagged')
plt.title('Tagging')
plt.savefig("tag2.png", bbox_inches='tight')
plt.close()

# Get all grade data files from the data/grades directory
gradeFiles = dp.getFilesWithName("grades", ".csv",
                                 os.path.join("./data", "grades"))
# Create a list of students and their final grades
graded_students = []
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
            graded_students.append(entry)

# Get all the students originally parsed from the piazza student data
# From Spring 2018
sp18_students = list(filter(lambda x: x['semester'] == 'sp18', wp.master_student_list))


# Compare all students to the graded_student list to see if there's
# a matching person. If so, add the matched grade to the user
# dictionary
for user in sp18_students:
    for entry in graded_students:
        if (utils.sameUser(entry, user)):
            user['grade'] = entry['grade']
            break
    if user.get('grade', None) is None:
        user['grade'] = "Not found"

    # Also add the numConstructive and numActive post entries from the
    # users2Questions dictionary
    user['numConstructive'] = users2Questions.get(user['user_id'], {'numConstructive': -1})['numConstructive']
    user['numActive'] = users2Questions.get(user['user_id'], {'numActive': -1})['numActive']

# Make a data frame with our user data
user_frame = pd.DataFrame(sp18_students)

# Create a new column to indicate whether a user asked a question or not
user_frame['askedquestion'] = np.where(user_frame['asks'] >= 1, "yes", "no")

# Creating a new frame to graph the number of students with each
# letter grade, based on whether they asked a question or not
grades_asked_frame = user_frame[user_frame['grade'] != 'Not found']
grades_asked_frame.groupby('grade')['askedquestion']\
    .value_counts(normalize=False).unstack().plot(kind='bar')
plt.ylabel("Proportion of total grades")
plt.xlabel("Letter Grades")
plt.title("Proportion of grades at each letter rank, divided by question asking")
plt.savefig("compare")
plt.close()

# Create a new column to show whether a student asked a constructive
# question
user_frame['asked_constructive_question'] = \
    np.where((user_frame['numConstructive']) > -1 &
             (user_frame['askedquestion'] == 'yes'),
                "yes", "no")

# Create a new column -- whether a student asked an active question
user_frame['asked_active_question'] = user_frame.apply(
    lambda row: (row['numActive'] > 0) & (row['askedquestion'] == 'yes'), axis=1)

# Create new column GPA which converts grade letters to gpa numbers
user_frame['gpa'] = user_frame['grade'].apply(utils.getGPA)

# Show the proportion of people who asked constructive questions
# Among those who asked any questions at all
print(user_frame.groupby('askedquestion')['asked_constructive_question'].value_counts(normalize=True))
# Does the same for active questions
print(user_frame.groupby('askedquestion')['asked_active_question'].value_counts(normalize=True))


# Show the average GPAs for people who ask constructive questions and
# people who ask active questions
print()
print("MEAN")
print(user_frame.groupby(['askedquestion', 'asked_constructive_question'])['gpa'].mean())
print(user_frame.groupby(['askedquestion', 'asked_active_question'])['gpa'].mean())
print()
print("STD")
print(user_frame.groupby(['askedquestion', 'asked_constructive_question'])['gpa'].std())
print(user_frame.groupby(['askedquestion', 'asked_active_question'])['gpa'].std())
print()
print("COUNT")
print(user_frame.groupby(['askedquestion', 'asked_constructive_question'])['gpa'].value_counts())
print(user_frame.groupby(['askedquestion', 'asked_active_question'])['gpa'].value_counts())
print()

# Creates a plot of Number of students
# vs. Number of constructive and active questions asked
user_frame[user_frame['numConstructive'] != -1]['numConstructive']\
    .value_counts().sort_index().plot(kind='line',
                                      legend=True, xticks=range(0, 21, 2))
user_frame[(user_frame['numActive'] != -1) & (user_frame['numActive'] < 21)]\
    ['numActive'].value_counts().sort_index().plot(kind='line',
                                                   legend=True, xticks=range(0, 21, 2))
plt.xlabel("No. of Questions Asked")
plt.ylabel("No. of Students")
plt.savefig("num_students_vs_num_questions")
plt.close()







