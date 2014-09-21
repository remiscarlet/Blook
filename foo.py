f = ["(1:2:1,2,3)","(1:2:1,2,5)","(1:3:1,4,3)"]

notes = dict()
for line in f:
	line.strip("()")
	line = line.split(",")
	time = line[0]
	val = [[line[1],line[2]]]
	if time in notes:
		val.extend(notes[time])
	notes[time] = val

print notes