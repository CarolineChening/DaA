import schedule
import time
import threading
from datetime import datetime, time as dt_time
from typing import Callable
from utils.time_utils import get_beijing_time

class ReminderScheduler:
    def __init__(self):
        self.jobs = []
        self.running = False
        self.thread = None
    
    def add_daily_reminder(self, hour, minute, callback: Callable, days=[0, 1, 2, 3, 4]):
        def wrapper():
            today = get_beijing_time().weekday()
            if today in days:
                callback()
        
        job = schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(wrapper)
        self.jobs.append(job)
        return job
    
    def add_morning_reminder(self, callback: Callable):
        return self.add_daily_reminder(10, 0, callback)
    
    def add_afternoon_reminder(self, callback: Callable):
        return self.add_daily_reminder(14, 30, callback)
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
    
    def _run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def get_next_reminder_time(self):
        now = get_beijing_time()
        today = now.weekday()
        
        morning_time = datetime(now.year, now.month, now.day, 10, 0)
        afternoon_time = datetime(now.year, now.month, now.day, 14, 30)
        
        if today >= 5:
            days_until_monday = 7 - today
            next_monday = now + timedelta(days=days_until_monday)
            return next_monday.replace(hour=10, minute=0, second=0, microsecond=0)
        
        if now < morning_time:
            return morning_time
        elif now < afternoon_time:
            return afternoon_time
        else:
            next_day = now + timedelta(days=1)
            while next_day.weekday() >= 5:
                next_day += timedelta(days=1)
            return next_day.replace(hour=10, minute=0, second=0, microsecond=0)
    
    def is_working_hours(self):
        now = get_beijing_time()
        weekday = now.weekday()
        hour = now.hour
        
        if weekday >= 5:
            return False
        
        return 9 <= hour <= 15
