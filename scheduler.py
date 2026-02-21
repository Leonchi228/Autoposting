import schedule
import time

# Task: Check news
def check_news():
    # Logic for checking news goes here
    print('Checking news...')
    
# Task: Update subscription days
def update_subscription_days():
    # Logic for updating subscription days goes here
    print('Updating subscription days...')

# Scheduling tasks
schedule.every().day.at('07:00').do(check_news)
schedule.every().day.at('10:00').do(update_subscription_days)

while True:
    schedule.run_pending()
    time.sleep(1)