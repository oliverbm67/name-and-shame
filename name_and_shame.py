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

def get_usage(top_output, level=10.0):
    """Return all processes above the CPU_USAGE level"""
    process = {}
    for line in top_output.split("\n"):
        row = line.split()
        if len(row) != 0:
            ## Retrieve only row starting with a number (PID)
            try:
                pid = int(row[0])
                user = row[1]
                cpu = float(row[8].replace(",","."))        ## Convert CPU usage to float value
                command = " ".join(row[11:])                ## Recover command
                if cpu > level:
                    process[pid] = [user,cpu,command]
            except ValueError:
                pass
    return process

## Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--level", help="Threshold for the CPU level",
                    type=float, default=80.0)
parser.add_argument("--time", help="How long a process has before being reported",
                    type=float, default=20.0)
parser.add_argument("--name", help="Display the name of offending user",
                    action="store_true")
parser.add_argument("--shame", help="Use Wall to send the message instead of stdout",
                    action="store_true")
args = parser.parse_args()
cpu_level = args.level
SAMPLING_TIME = args.time
NAMED_USER = args.name
PUBLIC = args.shame

## High PID counter
PREVIOUS_PROCESS = None
while True:
    top_out = get_top()
    high_process = get_usage(top_out, cpu_level)
    if PREVIOUS_PROCESS is not None:            ## Starting condition
        for new_pid, new_process in high_process:
            if new_pid in PREVIOUS_PROCESS:
                if NAMED_USER:
                    OFFENDER = new_process[0]
                else:
                    OFFENDER = "someone"
                report_message = f"{OFFENDER} is using too much CPU for {new_process[2]}"
                if PUBLIC:
                    public_shame(report_message)
                else:
                    print(report_message)
    ## Copy the high process
    PREVIOUS_PROCESS = copy.deepcopy(high_process)
    ## Delay
    time.sleep(SAMPLING_TIME)
