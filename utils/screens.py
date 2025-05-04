import mss

SCT = mss.mss()

def list_monitors():
    # List all monitors
    monitors = SCT.monitors

    # NOTE: in windows, monitors[0] is a special combined region
        # covering all monitors.
        # let's remove this for now
        # reference: https://www.reddit.com/r/learnpython/comments/rkyq4v/question_about_mss_and_monitor_selection/?rdt=35944
    monitors = monitors[1:]
        
    monitor_names = ["Display {}".format(i + 1) for i in range(len(monitors))]
    return monitor_names