import pandas as pd
import os, sys
import time
import re

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python filter_content.py <inputDir> <outputDir>")
        exit(1)
    
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]
    print("Read from inputDir %s" % inputDir)
    files = os.listdir(inputDir)
    outfiles = os.listdir(outputDir) 
    for dfile in files:
        print("Read from %s" % dfile)
        code = dfile.split('_')[0]
        ftype = dfile.split('_')[1].split('.')[0]
        data = pd.read_csv(inputDir+"/"+dfile,dtype=str)
        new_contents = []
        for c in data['content']:
            new_contents.append(re.sub(r'\s+',' ', str(c)))
        data['content'] = new_contents
        if ftype == 'tiezi':
            new_titles = []
            for t in data['title']:
                new_titles.append(re.sub(r'\s+',' ',str(t)))
            data['title'] = new_titles
        data.to_csv(outputDir+"/"+dfile,index=False)