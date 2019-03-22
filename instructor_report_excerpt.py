### testing code

shazam_students = ["Ernest", "Ernest Lim", "Koh John"]
cl = ["Ernest Tan", "Ernest Lim", "John Koh"]
attendance_list = []

### to be placed in code
shazam_students = [x for x in shazam_students if len(x.split()) > 1]
for l in cl:
    for s in shazam_students:
        if all(item in l.split() for item in s.split()):
            attendance_list.append(l)
absent_from_list = list(set(cl) - set(attendance_list))
