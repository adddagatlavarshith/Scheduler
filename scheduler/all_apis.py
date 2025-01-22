from flask import Flask, request, jsonify
import datetime as dt
import threading
import time
from scheduler import Scheduler  # Import the existing Scheduler class
from scheduler.trigger import Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

app = Flask(__name__)

# Initialize the Scheduler
scheduler = Scheduler()

# Dummy task for demonstration purposes
def foo():
    print("foo")

class API:
    enter_the_time: str
    interval_minutes: int
    job_id_counter = 1
    jobs = {}

    @classmethod
    def _generate_job_id(cls):
        job_id = cls.job_id_counter
        cls.job_id_counter += 1
        return job_id


    # [ # thi is the sintax for the start time
    # # "start_time": "2024-08-25T14:30:00" ]

    @app.route("/schedule/cyclic", methods=["POST"])
    def schedule_cyclic_task():
        try:
            data = request.json
            time_unit = data.get('time')
            interval_value = data.get('interval_time')
            start_time_str = data.get('start_time')  # Get the start time as a string

            if time_unit is None or interval_value is None:
                return jsonify({"error": "time and interval_time are required"}), 400

            # Define the interval based on the time unit
            if time_unit.lower() == "minutes":
                interval = dt.timedelta(minutes=interval_value)
            elif time_unit.lower() == "seconds":
                interval = dt.timedelta(seconds=interval_value)
            elif time_unit.lower() == "hours":
                interval = dt.timedelta(hours=interval_value)
            elif time_unit.lower() == "days":
                interval = dt.timedelta(days=interval_value)
            else:
                return jsonify({"error": "Invalid time unit. Use 'seconds', 'minutes', 'hours', or 'days'."}), 400

            # Parse the start time, if provided
            if start_time_str:
                start_time = dt.datetime.fromisoformat(start_time_str)  # ISO 8601 format (e.g., "2024-08-17T16:53:00")
                if start_time < dt.datetime.now():
                    return jsonify({"error": "Start time cannot be in the past"}), 400
            else:
                start_time = dt.datetime.now()  # If no start time is provided, start immediately

            job_id = API._generate_job_id()

            # Delay the scheduling until the start time
            def schedule_task():
                scheduled_task = scheduler.cyclic(timing=interval, handle=foo)
                API.jobs[job_id] = scheduled_task

            # Schedule the task to start at the specified start_time
            delay_seconds = (start_time - dt.datetime.now()).total_seconds()
            threading.Timer(delay_seconds, schedule_task).start()

            return jsonify(
                {
                    "message": f"Task scheduled to run every {interval_value} {time_unit}(s) starting from {start_time_str}",
                    "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/delay", methods=["POST"])
    def delay_scheduled_task():
        try:
            data = request.json
            job_id = data.get('job_id')
            delay_minutes = data.get('delay_time')
            start_time_str = data.get('start_time')
            end_time_str = data.get('end_time')

            if job_id not in API.jobs:
                return jsonify({"error": "Invalid job_id"}), 400

            if delay_minutes is None or start_time_str is None or end_time_str is None:
                return jsonify({"error": "delay_time, start_time, and end_time are required"}), 400

            # Parse the start and end times
            start_time = dt.datetime.fromisoformat(start_time_str)
            end_time = dt.datetime.fromisoformat(end_time_str)

            if start_time < dt.datetime.now():
                return jsonify({"error": "Start time cannot be in the past"}), 400

            if start_time >= end_time:
                return jsonify({"error": "Start time must be before end_time"}), 400

            # Delay the task
            def delay_task():
                scheduled_job = API.jobs[job_id]["task"]
                interval = API.jobs[job_id]["timing"]

                if scheduled_job:
                    scheduler.delete_job(scheduled_job)  # Remove the currently scheduled job
                    delay_duration = dt.timedelta(minutes=delay_minutes)
                    new_start_time = start_time + delay_duration

                    if new_start_time <= end_time:
                        delay_seconds = (new_start_time - dt.datetime.now()).total_seconds()
                        new_job = threading.Timer(delay_seconds, lambda: scheduler.cyclic(timing=interval, handle=foo))
                        new_job.start()

                        # Update the job reference in the API.jobs dictionary
                        API.jobs[job_id]["task"] = new_job

                        return jsonify({"message": f"Task delayed by {delay_minutes} minutes"}), 200
                    else:
                        return jsonify({"error": "Delay exceeds end_time limit"}), 400

            return delay_task()
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/minutely", methods=["POST"])
    def schedule_minutely_task():
        try:
            data = request.json
            second = data.get('second')
            start_time_str = data.get('start_time')  # Get the start time as a string

            if second is None or not (0 <= second < 60):
                return jsonify({"error": "Valid 'second' value (0-59) is required"}), 400

            # Parse the start time, if provided
            if start_time_str:
                start_time = dt.datetime.fromisoformat(start_time_str)  # ISO 8601 format (e.g., "2024-08-15T15:30:00")
                if start_time < dt.datetime.now():
                    return jsonify({"error": "Start time cannot be in the past"}), 400
            else:
                start_time = dt.datetime.now()  # If no start time is provided, start immediately

            job_id = API._generate_job_id()

            # Delay the scheduling until the start time
            def schedule_task():
                scheduled_task = scheduler.minutely(timing=dt.time(second=second), handle=foo)
                API.jobs[job_id] = scheduled_task

            # Schedule the task to start at the specified start_time
            delay_seconds = (start_time - dt.datetime.now()).total_seconds()
            threading.Timer(delay_seconds, schedule_task).start()

            return jsonify(
                {"message": f"Task scheduled to run at {second} seconds of every minute starting from {start_time_str}",
                 "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/hourly", methods=["POST"])
    def schedule_hourly_task():
        try:
            data = request.json
            minute = data.get('minute')
            second = data.get('second')
            start_time_str = data.get('start_time')  # Get the start time as a string

            if minute is None or not (0 <= minute < 60):
                return jsonify({"error": "Valid 'minute' value (0-59) is required"}), 400
            if second is None or not (0 <= second < 60):
                return jsonify({"error": "Valid 'second' value (0-59) is required"}), 400

            # Parse the start time, if provided
            if start_time_str:
                start_time = dt.datetime.fromisoformat(start_time_str)  # ISO 8601 format (e.g., "2024-08-17T16:53:00")
                if start_time < dt.datetime.now():
                    return jsonify({"error": "Start time cannot be in the past"}), 400
            else:
                start_time = dt.datetime.now()  # If no start time is provided, start immediately

            job_id = API._generate_job_id()

            # Delay the scheduling until the start time
            def schedule_task():
                scheduled_task = scheduler.hourly(timing=dt.time(minute=minute, second=second), handle=foo)
                API.jobs[job_id] = scheduled_task

            # Calculate delay and schedule the task
            delay_seconds = (start_time - dt.datetime.now()).total_seconds()
            threading.Timer(delay_seconds, schedule_task).start()

            return jsonify(
                {
                    "message": f"Task scheduled to run at {minute} minutes and {second} seconds of every hour, starting from {start_time_str}",
                    "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/daily", methods=["POST"])
    def schedule_daily_task():
        try:
            data = request.json
            hour = data.get('hour')
            minute = data.get('minute')
            start_time_str = data.get('start_time')  # Get the start time as a string

            if hour is None or not (0 <= hour < 24):
                return jsonify({"error": "Valid 'hour' value (0-23) is required"}), 400
            if minute is None or not (0 <= minute < 60):
                return jsonify({"error": "Valid 'minute' value (0-59) is required"}), 400

            # Parse the start time, if provided
            if start_time_str:
                start_time = dt.datetime.fromisoformat(start_time_str)  # ISO 8601 format (e.g., "2024-08-17T16:53:00")
                if start_time < dt.datetime.now():
                    return jsonify({"error": "Start time cannot be in the past"}), 400
            else:
                start_time = dt.datetime.now()  # If no start time is provided, start immediately

            job_id = API._generate_job_id()

            # Delay the scheduling until the start time
            def schedule_task():
                scheduled_task = scheduler.daily(timing=dt.time(hour=hour, minute=minute), handle=foo)
                API.jobs[job_id] = scheduled_task

            # Calculate delay and schedule the task
            delay_seconds = (start_time - dt.datetime.now()).total_seconds()
            threading.Timer(delay_seconds, schedule_task).start()

            return jsonify(
                {
                    "message": f"Task scheduled to run at {hour} hours and {minute} minutes every day, starting from {start_time_str}",
                    "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/exponential", methods=["POST"])
    def schedule_exponential_task():
        try:
            data = request.json
            initial_seconds = data.get('initial_seconds')
            factor = data.get('factor')

            if initial_seconds is None or initial_seconds < 0:
                return jsonify({"error": "Valid 'initial_seconds' value is required"}), 400
            if factor is None or factor <= 1:
                return jsonify({"error": "Valid 'factor' value greater than 1 is required"}), 400

            job_id = API._generate_job_id()
            scheduled_task = schedule_exponential(initial_seconds, factor, foo)
            API.jobs[job_id] = scheduled_task
            return jsonify({"message": f"Task scheduled to run with exponential intervals starting from {initial_seconds} seconds", "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/schedule/delete", methods=["POST"])
    def delete_task():
        try:
            data = request.json
            job_id = data.get('job_id')

            if job_id is None:
                return jsonify({"error": "job_id is required"}), 400

            if job_id in API.jobs:
                scheduler.delete_job(API.jobs[job_id])
                del API.jobs[job_id]
                return jsonify({"message": f"Task with job_id {job_id} deleted successfully"})
            else:
                return jsonify({"error": f"No task found with job_id {job_id}"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/jobs", methods=["GET"])
    def print_schedule():
        try:
            schedule_info = {job_id: str(task) for job_id, task in API.jobs.items()}
            return jsonify({"schedule": schedule_info})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route("/schedule/weekly", methods=["POST"])
    def schedule_weekly_task():
        try:
            data = request.json
            week_type = data.get('week_type')
            hour = data.get('hour')
            minute = data.get('minute')

            if week_type is None or hour is None or minute is None:
                return jsonify({"error": "week_type, hour, and minute are required"}), 400

            # Convert week_type to appropriate Weekday class instances
            weekdays = {
                "monday": Monday,
                "tuesday": Tuesday,
                "wednesday": Wednesday,
                "thursday": Thursday,
                "friday": Friday,
                "saturday": Saturday,
                "sunday": Sunday
            }
            week_classes = [weekdays[day.strip().lower()](dt.time(hour=hour, minute=minute)) for day in week_type.split(",")]

            job_id = API._generate_job_id()
            scheduled_task = scheduler.weekly(timing=week_classes, handle=foo)
            API.jobs[job_id] = scheduled_task
            return jsonify({"message": f"Task scheduled to run on {week_type} at {hour}:{minute}", "job_id": job_id})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

def schedule_exponential(initial_seconds, factor, task):
    job_id = API._generate_job_id()

    def wrapper(next_interval):
        task()
        next_interval *= factor
        run_time = dt.datetime.now() + dt.timedelta(seconds=next_interval)
        scheduled_task = scheduler.once(timing=run_time, handle=lambda: wrapper(next_interval))
        API.jobs[job_id] = scheduled_task

    wrapper(initial_seconds)
    return job_id

# Function to run the scheduler
def run_scheduler():
    while True:
        scheduler.exec_jobs()
        time.sleep(1)

# Start the scheduler in a separate thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
# this is very boring what if we can schedule take based on in put time other than giving hours minutes seperately.