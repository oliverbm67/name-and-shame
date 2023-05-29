#!/usr/bin/python3
"""This program monitors the process CPU usage via top and can report abnormal activities"""
import os
import time
import copy
import argparse

def get_top():
    """Return the configured top command"""
    # -b : batch mode
    # -n 1 : only do 1 iteration
    top_cmd ="top -b -n 1"
    process = os.popen(top_cmd)
    raw_out = process.read()
    process.close()
    return raw_out

def public_shame(msg):
    """Use wall to broadcast the message msg"""
    cmd = f"wall -t 10 {msg}"
    process = os.popen(cmd)
    process.close()

def get_usage(top_output, CPU_LEVEL=10.0):
    """Return all processes above the CPU_USAGE level"""
    high_process = {}
    for line in top_output.split("\n"):
        row = line.split()
        if len(row) != 0:
            ## Retrieve only row starting with a number (PID)
            try:
                pid = int(row[0])
                user = row[1]
                cpu = float(row[8].replace(",","."))        ## Convert CPU usage to float value
                command = " ".join(row[11:])                ## Recover command
                if cpu > CPU_LEVEL:
                    high_process[pid] = [user,cpu,command]
            except:
                pass
    return high_process

## Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--level", help="Threshold for the CPU level",type=float, default=80.0)
parser.add_argument("--time", help="How long a process has before being reported",type=float, default=20.0)
parser.add_argument("--name", help="Display the name of offending user",action="store_true")
parser.add_argument("--shame", help="Use Wall to send the message instead of stdout",action="store_true")
args = parser.parse_args()
CPU_LEVEL = args.level
SAMPLING_TIME = args.time
NAMED_USER = args.name
PUBLIC = args.shame

## High PID counter
previous_process = None
while True:
    top_out = get_top()
    high_process = get_usage(top_out, CPU_LEVEL)
    if previous_process is not None:            ## Starting condition
        for new_ps in high_process:
            if new_ps in previous_process:
                if NAMED_USER:
                    offender = high_process[new_ps][0]
                else:
                    offender = "someone"
                report_message = f"{offender} is using too much CPU for {high_process[new_ps][2]}"
                if PUBLIC:
                    public_shame(report_message)
                else:
                    print(report_message)
    ## Copy the high process
    previous_process = copy.deepcopy(high_process)
    ## Delay
    time.sleep(SAMPLING_TIME)
