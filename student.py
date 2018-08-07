

class Student:

    def __init__(self, id, name):
        self.piazza_questions = []
        self.gradescope_submissions = []
        self.id = id
        self.name = name

    def __repr__(self):
        ret = ""
        ret += "NAME: {} \nID: {} \n\n".format(self.name, self.id)
        for count, question in enumerate(self.piazza_questions):
            ret += "Question number {}: \n ".format(count + 1)
            ret += question + "\n\n"
        return ret