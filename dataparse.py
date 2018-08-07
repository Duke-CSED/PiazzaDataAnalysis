import codecs
import csv
import json
import os
import html
import re

"""
A simple module with some dataparsing methods, many of which have 
probably been written many times before. 
"""

base_data_path = "../"


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
    ("\\u00a0", " "),
    ("\n", " ")
]

class NoDataError(Exception):
    pass


def getFilesWithName(name, suffix="", searchDirectory="."):
    """
    Gets all files with the given name and suffix in the given directory
    :param name: Filename (ignoring file extension)
    :param suffix: File extension
    :param searchDirectory: Directory in which to search
    :return: A list of files matching those parameters
    """
    files = []
    for fileObject in os.listdir(searchDirectory):
        joinedPath = os.path.join(searchDirectory, fileObject)
        if os.path.isdir(joinedPath) and fileObject is not None:
            files.extend(getFilesWithName(name, suffix, joinedPath))
        else:
            if (name, suffix) == os.path.splitext(fileObject):
                files.append(joinedPath)
    return files


def printDict(dictionary, separator=":", sortedKeys=False):
    """
    Prints the given dictionary in key, value order
    :param dictionary: to be printed
    :param separator: how to separate the key and value
        (i.e. key : value)
    :param sortedKeys: whether to sort the dictionary by key
    :return: True if object is a dictionary and print was successful,
        False otherwise
    """
    if not isinstance(dictionary, dict):
        return False
    try:
        if not sortedKeys:
            items = dictionary.items()
        else:
            items = sorted(dictionary.items(), key=lambda x: x[0])
        for key, value in items:
            print(key, separator, value)
        return True
    except KeyError:
        return False


def getReadableJSON(json_data, dent=4, printData=True):
    """
    Gets JSON data in readable string format with sorted keys
    :param json_data: A loaded json object
    :param dent: how many spaces you want indentation
    :param print: prints the data
    :return: NA
    """
    son = json.dumps(json_data, indent=dent, sort_keys=True)
    if printData:
        print(son)
    else:
        return son


def getJSONData(path):
    """
    Loads JSON data from a filepath
    (Because I'm too lazy to keep typing with statements)
    :param path: Filepath of a Json file
    :return: False if not a json file, the loaded data otherwise
    """
    if not path.endswith(".json"):
        return False
    with open(path, 'r') as fp:
        loadedData = json.load(fp)
    return loadedData


def cleanhtml(rawHTML):
    """
    Cleans up raw HTML-formatted text by removing all tags
    i.e. <p>, <h1>, etc.
    :param rawHTML: the text to be formatted
    :return: the clean text without tags
    """
    cleanr = re.compile('<.*?>')
    cleanText = re.sub(cleanr, '', rawHTML)
    return cleanText


def cleanText(text, subs=substitutions):
    """
    Replaces instances of a set of specified substitutions, strips newlines
        and whitespace
    :param text: A string
    :param subs: List of tuples representing replacements
    :return: the clean text
    """
    text = html.unescape(text)
    text = text.replace("\"", "\\")
    text = cleanhtml(text)
    for tup in subs:
        text = text.replace(tup[0], tup[1])
    return text


def getClassContentFiles(dir=base_data_path):
    """ Gets class content files from the piazza data"""
    files = getFilesWithName("class_content", ".json", dir)
    checkFiles("class_content", ".json", dir, files)
    return files


def getUserFiles(baseDir=base_data_path):
    """ Gets the user files from the piazza data"""
    files = getFilesWithName("users", ".json", baseDir)
    checkFiles("users", ".json", baseDir, files)
    return files


def getRosterFiles(baseDir=base_data_path):
    files = getFilesWithName("piazza-compsci201_roster", ".csv", baseDir)
    checkFiles("piazza-compsci201_roster", ".csv", baseDir, files)
    return files


def getGradeFiles(baseDir=base_data_path):
    files = getFilesWithName("grades", ".csv", baseDir)
    checkFiles("grades", ".csv", baseDir, files)
    return files


def checkFiles(prefix, suffix, directory, fileList):
    if len(fileList) == 0:
        raise NoDataError("NO files found for name: {}{} in directory {}"
                          .format(prefix, suffix, directory))


def executeForAllUsers(lam, path):
    count = 0
    for item in getUserFiles(path):
        for user in getJSONData(item):
            lam(user)
            count += 1
    return count


def executeForAllPosts(lam, path):
    results = []
    for item in getClassContentFiles(path):
        for post in getJSONData(item):
            results.append(lam(post))
    return results


def convertFileName(filename):
    return (filename
            .replace("data", "")
            .replace("./piazza/", "")
            .replace("../src/piazza", "")
            .replace(".csv", "")
            .replace("piazza-compsci201_roster", "")
            .replace("./", "")
            .replace("/", "")
            .replace(".json", "")
            .replace("compsci201_", "")
            .replace("users", "")
            .replace("class_content", "")
            .replace("fall", "fa")
            .replace("spring", "sp")
            .replace("20", "")
            .replace(".", "")
            )


def parseRosterData(filename):
    """
    Gets CSV Data in the very specific format required
        by the compsci201 piazza roster files
    :param filename: Roster file to be searched
    :return: A dictionary with the parsed roster information
    """
    users = {}
    with open(filename, 'r') as file:
        for line in csv.reader(file):
            users[line[1]] = line[2]
            users[line[0].lower()] = line[2]
    return users
