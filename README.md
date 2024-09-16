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


## Server-Side Script
The server-side script is responsible for consolidating coin count data from various PCs, archiving old data, and running file synchronization commands.

### Features
- Consolidates data from multiple .txt files into a CSV report.
- Archives old files into a designated folder with timestamped names.
- Executes file copy commands using Robocopy to sync directories.

### Server-Side Script Overview

```python
import os
import csv
import shutil
import subprocess
from datetime import datetime

def get_txt_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt') and os.path.isfile(os.path.join(directory, f))]

def read_coincounter_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) >= 2:
            total_coins = int(lines[0].strip())
            last_update_str = lines[1].strip()
            last_update_time = datetime.fromisoformat(last_update_str)
            return total_coins, last_update_time
    return None, None

def consolidate_to_csv(directory):
    files = get_txt_files(directory)
    data = []
    summary = {}

    for file in files:
        file_path = os.path.join(directory, file)
        total_coins, last_update_time = read_coincounter_file(file_path)
        if total_coins is not None and last_update_time is not None:
            file_name = os.path.splitext(file)[0]
            date = datetime.now().date()
            data.append([file_name, date, total_coins])
            if file_name in summary:
                summary[file_name] += total_coins
            else:
                summary[file_name] = total_coins

    now = datetime.now()
    month_year = now.strftime("%B_%Y")
    output_csv = f'{month_year}.csv'
    output_path = os.path.join(directory, output_csv)
    write_header = not os.path.exists(output_path)

    with open(output_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        if write_header:
            csvwriter.writerow(['File Name', 'Date', 'Total Estimated Coin'])
        csvwriter.writerows(data)

    print(f'Consolidated data has been written to {output_csv}')
    return output_path, summary

def archive_files(directory):
    now = datetime.now()
    month_year = now.strftime("%B_%Y")
    archive_dir = os.path.join(directory, '#Archive', month_year)
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    files = get_txt_files(directory)
    for file in files:
        base_name = os.path.splitext(file)[0]
        timestamp = now.strftime("%m%d%y%H%M%S")
        new_name = f"{base_name}_{timestamp}.txt"
        original_path = os.path.join(directory, file)
        new_path = os.path.join(archive_dir, new_name)
        shutil.move(original_path, new_path)
        print(f"Moved {file} to {new_path}")

def run_robocopy_commands():
    commands = [
        'ROBOCOPY "C:\\ProgramData\\Riot Games" "D:\\Launchers\\Valorant" /mir',
        'ROBOCOPY "C:\\ProgramData\\Epic" "D:\\Launchers\\Epic" /mir'
    ]
    for command in commands:
        process = subprocess.run(command, shell=True)
        if process.returncode == 0:
            print(f'Successfully executed: {command}')
        else:
            print(f'Error executing: {command}, Return code: {process.returncode}')

def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    consolidate_to_csv(directory)
    archive_files(directory)
    run_robocopy_commands()

if __name__ == "__main__":
    main()
