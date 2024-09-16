# Coin Counter System

This project is a Coin Counter System, designed to track and log coin insertion data from various machines and consolidate the results into a CSV report. It comprises both client-side and server-side components.

## Client-Side Script

The client-side script runs on individual PCs and periodically updates the coin count by monitoring the coin board signals via the COM port.

### Features
- Retrieves the PC name dynamically.
- Loads and saves the current coin count state.
- Updates the coin count periodically (default is every 5 minutes).
- Tracks missed intervals and adds them to the count.

### Client-Side Script Overview

```python
import time
import os
import platform
from datetime import datetime, timedelta

# Function to get the PC name
def get_pc_name():
    return platform.node()

# Function to load previous state from the file
def load_state(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 2:
                last_count = int(lines[0])
                last_update_str = lines[1].strip()
                last_update_time = datetime.fromisoformat(last_update_str)
                return last_count, last_update_time
    return 0, None

# Function to save current state to the file
def save_state(file_path, count, last_update_time):
    with open(file_path, 'w') as file:
        file.write(f"{count}\n")
        file.write(f"{last_update_time.isoformat()}\n")

# Function to calculate missed intervals, only within the last 5 minutes
def calculate_missed_intervals(last_update_time, interval_minutes):
    now = datetime.now()
    if last_update_time is None:
        return 0
    elapsed_time = now - last_update_time
    max_interval = timedelta(minutes=interval_minutes)
    if elapsed_time <= max_interval:
        return elapsed_time // max_interval
    return 0

# Function to update coin count
def update_coin_count(file_path, interval_minutes):
    count, last_update_time = load_state(file_path)
    missed_intervals = calculate_missed_intervals(last_update_time, interval_minutes)
    count += missed_intervals + 1
    last_update_time = datetime.now()
    save_state(file_path, count, last_update_time)

# Main function to run the background task
def main():
    pc_name = get_pc_name()
    file_path = f"\\\\SERVER\\timer\\{pc_name}.txt"
    interval_minutes = 5

    # Track when the last update happened
    last_update_time = datetime.now()
    
    while True:
        now = datetime.now()
        # Update the coin count if the interval has passed
        if (now - last_update_time).total_seconds() >= interval_minutes * 60:
            update_coin_count(file_path, interval_minutes)
            last_update_time = now
        
        # Sleep for 1 second before checking again
        time.sleep(1)

if __name__ == "__main__":
    main()
