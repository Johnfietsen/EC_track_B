""" Little script generate CSV's with robot velocities 
Usage: python read_log.py <robot_number>-<experiment_number>"""

import re
import sys
import csv

robot_name = "robot_" + sys.argv[1]
log_file_path = robot_name + ".log"
regex = '\d.\d+'
 
match_list = []
with open(log_file_path, "r") as file:
    count = 0
    for line in file:
        count += 1
        if (count % 2 == 0):
            for match in re.finditer(regex, line, re.S):
                match_text = match.group()
                match_list.append(match_text)

csvfile = robot_name + ".csv"
with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator=',')
    for val in match_list:
        writer.writerow([val]) 