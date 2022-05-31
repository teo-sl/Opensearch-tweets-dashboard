import json
import csv
import random
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import math
from matplotlib.pyplot import figure
import os
import collections
from collections import defaultdict
from numpy import asarray
from numpy import savetxt



def getLoc(prefix):
    ret=[]
    with open(prefix+'\out.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for line in csv_reader:
            ret.append([line[0],line[1]])
    return ret
    
def update(fileName,prefix):
    locations=getLoc(prefix)
    f=open(prefix + "\\" + fileName,'r')
    newfilename=fileName.replace(".json","")+"_output.json"
    outputFile=open(prefix+"\\"+newfilename,'w')
    lines=f.readlines()
    for line in lines:
        jsonLine=json.loads(line)
        if(jsonLine["coordinates"] is not None):
            outputFile.write(line+"\n")
            continue
        
        position=locations[random.randint(0,len(locations))]
        lat=float(position[0])+random.uniform(0,0.05)
        lon=float(position[1])+random.uniform(0,0.05)

        if(lat>90 or lat<-90):
            lat=float(position[0])

        if(lon>180 or lon<-180):
            lon=float(position[0])
        
        coordinates={"lat":lat,"lon":lon}
        jsonLine["coordinates"]=coordinates
        outputFile.write(json.dumps(jsonLine)+"\n")

def importCoordinates(prefix):
    path1=prefix +'\hashtag_donaldtrump.csv'
    path2=prefix +'\hashtag_joebiden.csv'
    trump_df = pd.read_csv(r""+path1,lineterminator='\n')
    biden_df = pd.read_csv(r""+path2,lineterminator='\n')
    total=trump_df.append(biden_df)
    merged=total[(~total["lat"].isnull()) & (~total["long"].isnull())]
    list=merged[["lat","long"]].to_numpy()
    savetxt(prefix+'\out.csv',list,delimiter=',',fmt='%f')

#importCoordinates(".\pre-processing")
update("us-presidential-tweet-id-2020-10-01-00_hydrated.json",".\pre-processing")


