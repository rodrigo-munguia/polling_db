from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
 
# Creates a default Background Scheduler
sched = BackgroundScheduler()

def prompt():
    print("Executing Task...")

sched.add_job(prompt,'interval', seconds=5)
 
# Starts the Scheduled jobs
sched.start()
 
# Runs an infinite loop
while True:
    sleep(1)