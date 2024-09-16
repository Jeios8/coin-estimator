# Coin Counter System

This project is a Coin Counter System, designed to track and log coin insertion data from various machines and consolidate the results into a CSV report. It comprises both client-side and server-side components.

## Client-Side Script (coin-estimator.pyw)

The client-side script runs on individual PCs and periodically updates the coin count by monitoring the coin board signals via the COM port.

### Features
- Retrieves the PC name dynamically.
- Loads and saves the current coin count state.
- Updates the coin count periodically (default is every 5 minutes).
- Tracks missed intervals and adds them to the count.

## Server-Side Script (coin-data-consolidator.py)
The server-side script is responsible for consolidating coin count data from various PCs, archiving old data, and running file synchronization commands.

### Features
- Consolidates data from multiple .txt files into a CSV report.
- Archives old files into a designated folder with timestamped names.
- Executes file copy commands using Robocopy to sync directories.
