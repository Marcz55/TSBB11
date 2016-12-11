
from os import listdir
from os.path import isfile, join
from os import rename
import random
import os




g_nof_subfolders = 30
g_path = "/home/yaiban/courses/tsbb11/data/"





def main():
    for i in range(0,g_nof_subfolders):
        if not os.path.exists(g_path + "seq" + format(i, "02d")):
            os.makedirs(g_path + "seq" + format(i, "02d"))
    
    random.seed(1337)
    files = [f for f in listdir(g_path+"without_green") if isfile(join(g_path+"without_green",f))];
    folder = []
    for file in files:
        os.rename(g_path + "without_green/" + file,
                  g_path +
                  "seq" +
                  format(random.randint(0,g_nof_subfolders-1), "02d") +
                  "/" +
                  file)
                  

main()
