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