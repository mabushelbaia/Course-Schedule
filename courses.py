from bs4 import BeautifulSoup
import re 
class Course:
    def __init__(self, array):
        self.code = array[0]
        self.Class = array[1]
        self.title = array[2]
        self.instructor = array[3]
        self.time = []
        self.room = []
        if "," not in array[4] and len(array[4]) > 1:
            array[4] = tuple([array[4][i]for i in range(len(array[4]))])
            for i in range(0, len(array[5]), 13):
                self.time.append(array[5][i:i+13].split(" - "))

            self.hasMultipleRooms = True
            self.room = [elem for elem in array[6].split(" ") if elem.isalnum()]
            maintext = re.sub(r'[^a-zA-Z0-9 ]', '', str(array[6]))
            self.room = maintext.split()
            maintext = re.sub(r'[a-zA-Z0-9]', '#', str(array[6]))
            maintext = maintext.split("#")
            self.building = [x.strip() for x in maintext if len(x.strip()) > 0]
        else:
            array[4] = tuple(array[4].split(", "))
            self.time = array[5].split(" - ")
            self.hasMultipleRooms = False
            self.room = array[6].split(" ")[0]
            self.building = " ".join(array[6].split(" ")[1:])
        self.days = array[4]
    def __str__(self):
        return f"Course Code: {self.code} \nClass: {self.Class} \nTitle: {self.title} \nInstructor: {self.instructor} \nDays: {self.days} \nTime: {self.time} \nRoom: {self.room} \nBuilding: {self.building}"
    
def get_courses():
    with open('index.html', encoding='utf-8') as html_file:
        soup = BeautifulSoup(html_file, 'lxml')
    table = soup.find('table')
    table_rows = table.find_all('tr')
    Courses = []
    for row in table_rows[1:]:
        row = row.text.strip().split("\n")
        row = [x.strip() for x in row if len(x.strip()) > 0]
        Courses.append(Course(row))
    return Courses