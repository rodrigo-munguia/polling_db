from time import sleep
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
 
# Creates a default Background Scheduler
sched = BackgroundScheduler()

def prompt():
    print("Executing Task...")
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

sched.add_job(prompt,'interval', seconds=5)
 
# Starts the Scheduled jobs
sched.start()
 
# Runs an infinite loop
while True:
    sleep(1)