import re
import sys

resfile = open("result.txt","w")

if __name__ == "__main__":
    inputFile = open(sys.argv[1])
    data = inputFile.read()
    #resfile.write(data)
    while True:
        p = re.search('\n[\d]+?,[\d]+?,[\d]+?,[\d]+?,[\s\S]+?,\"/news.+?\"',data)
        if p is None:
            break
        s = p.span()[0]
        e = p.span()[1]
        resfile.write(data[:s+1])
        tstr = data[s+1:e].strip().replace("\n","").replace("^M","")
        print(tstr)
        resfile.write(tstr)
        data = data[e:]
    resfile.write(data)