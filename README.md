# Monthly Calendar Generator

This Python script generates a monthly calendar in PDF format based on a YAML configuration file.

## Requirements

*   Python 3.6+
*   ReportLab library
*   PyYAML library

## Installation

Install the required libraries using pip:

> pip install reportlab PyYAML

## Usage
Create a Configuration File:

Create a YAML file (e.g., config.yaml) to specify the months to print and any events. You can generate a template config file using the --template option:

Bash
> python calendar_generator.py --template

This will create a template_config.yaml file that you can modify.  The config file has the following structure:

YAML

    months_to_print:
       - YYYY-MM  # Example: 2024-10
       - YYYY-MM
     
     events:
       single_events:
         - date: YYYY-MM-DD
           description: Event Description
         # ... more single events ...
     
       recurring_events:
         - recurrence: nW  # n weeks (e.g., 1w, 2w)
           start_date: YYYY-MM-DD
           description: Event Description
           end_date: YYYY-MM-DD  # Optional
         - recurrence: nM  # n months (e.g., 1m, 3m)
           start_date: YYYY-MM-DD
           description: Event Description
         - recurrence: nY  # n years (e.g., 1y, 2y)
           start_date: YYYY-MM-DD
           description: Event Description
           
months_to_print: A list of months to include in the calendar, in YYYY-MM format.

events: A dictionary containing single_events and recurring_events.

single_events: A list of dictionaries, each with a date (YYYY-MM-DD) and a description.

recurring_events: A list of dictionaries, each with:

recurrence: The recurrence interval (nW, nM, or nY, where n is a number).

start_date: The start date (YYYY-MM-DD).

description: The event description.

end_date: (Optional) An end date (YYYY-MM-DD). If omitted, the event recurs indefinitely.

## Run the Script:

Run the script with the config file as an argument. You can optionally provide a custom output filename:

Bash

    python calendar_generator.py config.yaml -o my_calendar.pdf

Bash

    python calendar_generator.py config.yaml

*Replace config.yaml with the actual path to your config file. If you do no specify a custom output name, then calendar.pdf will be generated.*

Output:

The script will generate a PDF file.

# Example Config File (config.yaml):

    months_to_print:
    - 2025-01
    - 2025-02
    events:
      single_events:
      - date: '2025-01-01'
        description: New Year's Day
      - date: '2025-02-14'
        description: Valentine's Day
      recurring_events:
      - recurrence: 1w
        start_date: '2025-01-06'
        description: Weekly Meeting
        end_date: '2025-03-31'
      - recurrence: 1m
        start_date: '2025-01-15'
        description: Monthly Report Due



<img width="970" alt="image" src="https://github.com/user-attachments/assets/45d7fcf7-1d51-42ef-87b2-57f9d93de282" />
