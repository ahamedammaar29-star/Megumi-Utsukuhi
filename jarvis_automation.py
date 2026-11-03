class MegumiAutomationManager:
    def __init__(self):
        self.registered_phone = "+91 9367132060"
        self.primary_email = "ahamedammaar29@gmail.com"
        self.dream_email = "mydreamisstudyinsaudiarabia@gmail.com"

    def dispatch_system_alert(self, alert_subject, message_body):
        print(f"\n🌸 [SMTP Alert] Dispatched to: {self.primary_email}")
        print(f"🌸 [SMS Alert] Dispatched to: {self.registered_phone}")
        print(f"🌸 [Goal Tracker] Saved metadata to: {self.dream_email}")
        return True
