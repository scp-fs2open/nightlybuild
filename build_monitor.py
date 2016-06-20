#!/bin/env python3

import argparse
import sys
import datetime

import time
import yaml

import monitors

parser = argparse.ArgumentParser()
parser.add_argument("tag_name", help="The tag name to monitor")
parser.add_argument("--config", help="Sets the config file", default="config.yml")
parser.add_argument("--interval", help="The interval in which the job status should be checked", type=float,
                    default=20.)

args = parser.parse_args()

options = {}

with open(args.config, "r") as f:
    try:
        options = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)

monitor_list = [monitors.TravisMonitor(options, args.tag_name), monitors.AppveyorMonitor(options, args.tag_name)]

interval = args.interval

while len(monitor_list) > 0:
    next_check = datetime.datetime.now() + datetime.timedelta(0, interval)

    new_list = []
    for mon in monitor_list:
        try:
            sys.stdout.write("Checking state of {}...".format(mon.name))
            sys.stdout.flush()  # Normally only newline cause a flush

            mon.update_state()

            print(" {}".format(mon.state))

            if mon.running:
                new_list.append(mon)
            else:
                print("The build of {} has ended with state {}.".format(mon.name, mon.state))
        except Exception as e:
            print()  # Finish line
            print("The monitor of {} has generated an error: {}".format(mon.name, e))
            new_list.append(mon)  # Retry in the next iteration

    monitor_list = new_list

    sleep_time = next_check - datetime.datetime.now()
    sleep_seconds = max(0, sleep_time.total_seconds())
    if sleep_seconds > 0.:
        time.sleep(sleep_seconds)
