file = open(f"output.csv","r")
newfile = open("newoutput.csv","w")

line = file.readline()
newfile.write("generation, " + line)

i = 0
for line in file.readlines():
    newfile.write(str(i) + ", "+ line)
    i += 1