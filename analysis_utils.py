

def executeSQLFile(filename, cursor):
    with open(filename, "r") as sql_file:
        sql_script = sql_file.read()
    cursor.executescript(sql_script)


def populateUsers2Questions(posts):
    users2Questions = {}
    for row in posts.itertuples():
        item = row._asdict()
        if item['piazzaId'] in users2Questions.keys():
            users2Questions[item['piazzaId']]['questions'].append(
                item['content'])
            users2Questions[item['piazzaId']]['tagNames'].append(
                item['tagName'])
            users2Questions[item['piazzaId']]['numConstructive'] += int(
                item['tagName'] == 'GQ' or item['tagName'] == 'DK')
            users2Questions[item['piazzaId']]['numActive'] += int(
                item['tagName'] == 'CD')
        else:
            insert = {'grade': item['grade'],
                      'questions': [item['content'], ],
                      'tagNames': [item['tagName'], ],
                      'numConstructive': int(
                          item['tagName'] == 'GQ' or item['tagName'] == 'DK'),
                      'numActive': int(item['tagName'] == 'CD')}
            users2Questions[item['piazzaId']] = insert

    return users2Questions


def compareIgnoreMiddleName(name1, name2):
    """ Takes two names, and compares only the first
    and last names"""
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

def sameUser(user, entry):
    """ Checks if the users are the same by comparing names,
    emails, and netIDs"""
    try:
        return (
            user['name'] == entry['name']
            or entry['email'] == user['email']
            or entry['netID'] in user['email']
            or compareIgnoreMiddleName(user['name'], entry['name']))
    except KeyError:
        return False

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