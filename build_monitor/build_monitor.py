import datetime
import sys
import time

from build_monitor import monitors


def monitor_builds(tag_name, options):
    used_monitors = [monitors.GitHubMonitor(options, tag_name)]
    interval = options["monitor"]["check_interval"]

    monitor_list = used_monitors
    while True:
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

        if len(monitor_list) <= 0:
            break

        sleep_time = next_check - datetime.datetime.now()
        sleep_seconds = max(0, sleep_time.total_seconds())
        if sleep_seconds > 0.:
            time.sleep(sleep_seconds)

    return all((m.success for m in used_monitors))
