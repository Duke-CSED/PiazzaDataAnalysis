class Question:

    def __init__(self, q_id="Unknown", student_id="Unkown",
                 subject="Unkown", content="Unknown",
                 tag="Unkown",
                 tag2="Unkown",
                 time="Unknown"):
        self.q_id = q_id
        self.student_id = student_id
        self.subject = subject
        self.content = content
        self.tag = tag
        self.tag2 = tag2
        self.time = time
        self.followups = []
        self.upvotes = 0
        self.student_name = ""

    def __repr__(self):
        return " \n".join([
            "Question ID: " + self.q_id,
            "Student ID: " + self.student_id,
            "Student Name: " + self.student_name,
            "Content: \n" + self.content,
            self.tag,
            self.tag2,
            self.time
        ])

    def __add__(self, other):
        return self.__repr__() + other.__repr__()

    def writeLine(self):
        return [self.q_id, self.subject,
                self.content,
                self.tag, self.tag2, "Yes" if self.tag == self.tag2 else "No",
                self.time]
