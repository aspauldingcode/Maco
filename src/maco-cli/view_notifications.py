import pandas as pd
import os
from termcolor import colored
import textwrap

# Path to the CSV file
csv_file_path = "/tmp/Maco-notifications.csv"

# Read the CSV file
try:
    df = pd.read_csv(csv_file_path, delimiter='\t', encoding='utf-16')
except UnicodeDecodeError:
    # If UTF-16 fails, try reading with 'utf-8' encoding
    df = pd.read_csv(csv_file_path, delimiter='\t', encoding='utf-8')

# Remove the first row if it contains BOM (Byte Order Mark)
if df.columns[0].startswith('\ufeff'):
    df.columns = df.columns.str.lstrip('\ufeff')

# Remove any completely empty rows
df = df.dropna(how='all').reset_index(drop=True)

# Replace 'NaN' with empty string for display purposes
df = df.fillna('')

# Display the notifications in a stylish format
if not df.empty:
    for _, row in df.iterrows():
        print(colored('=' * 80, 'cyan'))
        print(colored(textwrap.fill(f"Time: {row['Time']}", width=80), 'yellow'))
        print(colored(textwrap.fill(f"App: {row['Bundle']}", width=80), 'green'))
        print(colored(textwrap.fill(f"Title: {row['Title']}", width=80), 'magenta', attrs=['bold']))
        if row['SubTitle']:
            print(colored(textwrap.fill(f"Subtitle: {row['SubTitle']}", width=80), 'magenta'))
        print(colored(textwrap.fill(f"Message: {row['Message']}", width=80), 'white'))
        print(colored('=' * 80, 'cyan'))
        print()  # Empty line for separation
else:
    print(colored(textwrap.fill("No notifications found. Please check if the CSV file contains data.", width=80), 'red'))
