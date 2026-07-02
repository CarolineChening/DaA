import time
import threading
import json
import os
from utils.time_utils import get_beijing_time

class ReminderScheduler:
    def __init__(self):
        self.reminders = []
        self.is_running = False
        self.thread = None
        self.last_triggered = {}
        
    def add_daily_reminder(self, hour, minute, callback, label=""):
        key = f"{hour:02d}:{minute:02d}"
        self.reminders.append({
            'hour': hour,
            'minute': minute,
            'label': label,
            'callback': callback,
            'key': key
        })
        self.last_triggered[key] = None
        return key
    
    def _run_callback(self, callback, label):
        try:
            callback(label)
        except Exception as e:
            print(f"⚠️ 定时任务执行失败: {e}")
    
    def start(self):
        if self.is_running:
            return
        
        self.is_running = True
        
        now = get_beijing_time()
        current_date = now.date()
        current_time_str = f"{now.hour:02d}:{now.minute:02d}"
        
        for reminder in self.reminders:
            key = reminder['key']
            if self.last_triggered.get(key) != current_date:
                if current_time_str >= key:
                    self.last_triggered[key] = current_date
                    self._run_callback(reminder['callback'], reminder['label'])
        
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        print("✅ 定时提醒服务已启动")
    
    def _run_scheduler(self):
        while self.is_running:
            now = get_beijing_time()
            current_time = f"{now.hour:02d}:{now.minute:02d}"
            current_date = now.date()
            
            for reminder in self.reminders:
                key = reminder['key']
                if current_time == key:
                    last_date = self.last_triggered.get(key)
                    if last_date != current_date:
                        self.last_triggered[key] = current_date
                        self._run_callback(reminder['callback'], reminder['label'])
            
            time.sleep(30)
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        print("⏹️ 定时提醒服务已停止")
    
    def get_scheduled_jobs(self):
        jobs = []
        for reminder in self.reminders:
            jobs.append({
                'hour': reminder['hour'],
                'minute': reminder['minute'],
                'label': reminder['label']
            })
        return jobs
    
    def is_scheduler_running(self):
        return self.is_running

class PriceAlert:
    def __init__(self):
        self.alerts = []
        self.load_alerts()
    
    def add_alert(self, symbol, target_price, condition, callback):
        alert = {
            'id': len(self.alerts) + 1,
            'symbol': symbol,
            'target_price': target_price,
            'condition': condition,
            'callback': callback,
            'triggered': False,
            'created_at': get_beijing_time().isoformat()
        }
        self.alerts.append(alert)
        self.save_alerts()
        return alert
    
    def check_alerts(self, symbol, current_price):
        triggered_alerts = []
        for alert in self.alerts:
            if alert['symbol'] == symbol and not alert['triggered']:
                if alert['condition'] == 'above' and current_price >= alert['target_price']:
                    alert['triggered'] = True
                    triggered_alerts.append(alert)
                elif alert['condition'] == 'below' and current_price <= alert['target_price']:
                    alert['triggered'] = True
                    triggered_alerts.append(alert)
        
        if triggered_alerts:
            self.save_alerts()
        
        return triggered_alerts
    
    def remove_alert(self, alert_id):
        self.alerts = [a for a in self.alerts if a['id'] != alert_id]
        self.save_alerts()
    
    def reset_alert(self, alert_id):
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['triggered'] = False
        self.save_alerts()
    
    def get_alerts(self):
        return self.alerts
    
    def save_alerts(self):
        try:
            with open('/Users/ccchen/Downloads/DaA/data/alerts.json', 'w') as f:
                alerts_to_save = [a for a in self.alerts if 'callback' not in a or not callable(a['callback'])]
                json.dump(alerts_to_save, f, indent=2)
        except Exception as e:
            print(f"⚠️ 保存预警失败: {e}")
    
    def load_alerts(self):
        try:
            with open('/Users/ccchen/Downloads/DaA/data/alerts.json', 'r') as f:
                self.alerts = json.load(f)
        except FileNotFoundError:
            self.alerts = []
        except Exception as e:
            print(f"⚠️ 加载预警失败: {e}")
            self.alerts = []

scheduler = ReminderScheduler()
price_alert = PriceAlert()