import random
from datetime import datetime, timedelta
import pytz

class Schedule:
    def __init__(self, name, start_time, end_time, days, timezone, daily_limit, min_interval, max_interval):
        self.name = name
        self.start_time = start_time  # Time format (e.g., "9:00 AM")
        self.end_time = end_time      # Time format (e.g., "6:00 PM")
        self.days = days              # List of selected days (e.g., ['Monday', 'Tuesday', ...])
        self.timezone = timezone      # Timezone info (e.g., "US/Eastern")
        self.daily_limit = daily_limit  # Max emails per day
        self.min_interval = min_interval  # Minimum interval between emails (in minutes)
        self.max_interval = max_interval  # Maximum interval between emails (in minutes)
        self.emails_sent_today = 0  # Counter for emails sent today
        self.last_email_time = None  # Timestamp of the last email sent

    def is_within_schedule(self, current_time):
        """Check if the current time falls within the scheduled days and hours."""
        tz = pytz.timezone(self.timezone)
        local_time = current_time.astimezone(tz)
        current_day = local_time.strftime('%A')  # e.g., "Monday"
        current_hour = local_time.strftime('%I:%M %p')  # e.g., "9:30 AM"

        # Check if the current day is within the scheduled days
        if current_day not in self.days:
            return False

        # Check if the current time is within the start and end time
        return self.start_time <= current_hour <= self.end_time

    def can_send_email(self):
        """Determine if an email can be sent based on the daily limit and schedule."""
        current_time = datetime.now(pytz.utc)

        # Check if we are within the schedule
        if not self.is_within_schedule(current_time):
            return False
        
        # Reset daily counter if the day has changed
        if self.last_email_time:
            if self.last_email_time.date() != current_time.date():
                self.emails_sent_today = 0

        # Check if the daily limit is reached
        if self.emails_sent_today >= self.daily_limit:
            return False

        # If all conditions are met, allow email sending
        return True

    def get_next_send_time(self):
        """Get the next send time based on a random interval."""
        if self.last_email_time is None:
            # If no email has been sent, the next time is now
            return datetime.now(pytz.utc)

        # Calculate a random interval between min_interval and max_interval
        interval_minutes = random.randint(self.min_interval, self.max_interval)
        next_send_time = self.last_email_time + timedelta(minutes=interval_minutes)

        return next_send_time

    def send_email(self):
        """Simulate sending an email and updating the schedule."""
        if self.can_send_email():
            next_send_time = self.get_next_send_time()
            current_time = datetime.now(pytz.utc)

            # Wait until the next send time
            if current_time >= next_send_time:
                # Simulate sending the email
                print(f"Sending email at {current_time.astimezone(pytz.timezone(self.timezone)).strftime('%Y-%m-%d %I:%M %p')}")

                # Update the last email time and increment the daily counter
                self.last_email_time = current_time
                self.emails_sent_today += 1
            else:
                print("Waiting for the next interval to send email.")
        else:
            print("Cannot send email: Out of schedule or daily limit reached.")

    def __repr__(self):
        return (f"Schedule(name='{self.name}', start_time='{self.start_time}', end_time='{self.end_time}', "
                f"days={self.days}, timezone='{self.timezone}', daily_limit={self.daily_limit}, "
                f"min_interval={self.min_interval}, max_interval={self.max_interval})")


# Example usage
default_schedule = Schedule(
    name="Daily Outreach",
    start_time="9:00 AM",
    end_time="6:00 PM",
    days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    timezone="US/Eastern",
    daily_limit=20,
    min_interval=5,  # Minimum interval between emails in minutes
    max_interval=10   # Maximum interval between emails in minutes
)

# Simulate the process of sending emails based on the schedule
default_schedule.send_email()