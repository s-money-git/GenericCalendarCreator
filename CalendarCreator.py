import argparse
import yaml
import calendar
from datetime import datetime, date
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors

# --- Configuration Validation Functions ---

def is_valid_date(date_str, date_format="%Y-%m-%d"):
    """Checks if a date string is valid and matches the given format."""
    try:
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def validate_config(config):
    """Validates the structure and content of the configuration data."""
    errors = []

    # Check for required top-level keys
    if 'months_to_print' not in config:
        errors.append("Missing 'months_to_print' key in config file.")
    if 'events' not in config:
        errors.append("Missing 'events' key in config file.")

    # Validate months_to_print
    if 'months_to_print' in config:
        if not isinstance(config['months_to_print'], list):
            errors.append("'months_to_print' must be a list.")
        else:
            for month_str in config['months_to_print']:
                if not is_valid_date(month_str + "-01", "%Y-%m-%d"):  # Add "-01" for day
                    errors.append(f"Invalid month format: '{month_str}'. Use '%Y-%m'.")

    # Validate events
    if 'events' in config:
        if not isinstance(config['events'], dict):
            errors.append("'events' must be a dictionary.")
        else:
            # Validate single_events
            if 'single_events' in config['events']:
                if not isinstance(config['events']['single_events'], list):
                    errors.append("'single_events' must be a list.")
                else:
                    for event in config['events']['single_events']:
                        if not isinstance(event, dict):
                            errors.append("Each entry in 'single_events' must be a dictionary.")
                            continue
                        if 'date' not in event or 'description' not in event:
                            errors.append("Each single event must have 'date' and 'description' keys.")
                            continue
                        if not is_valid_date(event['date']):
                            errors.append(f"Invalid date format: '{event['date']}'. Use '%Y-%m-%d'.")
                        if not isinstance(event['description'], str):
                            errors.append(f"Description must be a string: '{event['description']}'.")

            # Validate recurring_events
            if 'recurring_events' in config['events']:
                if not isinstance(config['events']['recurring_events'], list):
                    errors.append("'recurring_events' must be a list.")
                else:
                    for event in config['events']['recurring_events']:
                        if not isinstance(event, dict):
                            errors.append("Each entry in 'recurring_events' must be a dictionary.")
                            continue
                        if 'recurrence' not in event or 'start_date' not in event or 'description' not in event:
                            errors.append("Each recurring event must have 'recurrence', 'start_date', and 'description' keys.")
                            continue
                        if not isinstance(event['recurrence'], str) or not (event['recurrence'].endswith('w') or event['recurrence'].endswith('m') or event['recurrence'].endswith('y')) or not event['recurrence'][:-1].isdigit():
                            errors.append(f"Invalid recurrence format: '{event['recurrence']}'. Use 'nW', 'nM', or 'nY'.")
                        if not is_valid_date(event['start_date']):
                            errors.append(f"Invalid start_date format: '{event['start_date']}'. Use '%Y-%m-%d'.")
                        if 'end_date' in event and not is_valid_date(event['end_date']):
                            errors.append(f"Invalid end_date format: '{event['end_date']}'. Use '%Y-%m-%d'.")
                        if not isinstance(event['description'], str):
                           errors.append(f"Description must be a string: '{event['description']}'.")


    return errors

# --- YAML Template Generation ---

def create_template_config(filename="template_config.yaml"):
    """Generates a template YAML config file."""

    template = {
        'months_to_print': [
            '2025-01',
            '2025-02'
        ],
        'events': {
            'single_events': [
                {'date': '2025-01-01', 'description': 'New Year\'s Day'},
                {'date': '2025-02-14', 'description': 'Valentine\'s Day'}
            ],
            'recurring_events': [
                {'recurrence': '1w', 'start_date': '2025-01-06', 'description': 'Weekly Meeting', 'end_date': '2025-03-31'},
                {'recurrence': '1m', 'start_date': '2025-01-15', 'description': 'Monthly Report Due'}
            ]
        }
    }
    try:
        with open(filename, 'w') as f:
            yaml.dump(template, f, indent=2, sort_keys=False)
        print(f"Template config file created: {filename}")
    except Exception as e:
        print(f"Error creating template config file: {e}")


# --- PDF Generation Functions ---

def create_calendar_page(canvas, year, month, events):
    """Creates a single calendar page on the given ReportLab canvas."""

    # Page setup
    canvas.setPageSize(landscape(letter))
    canvas.setFont("Helvetica", 12)

    # Dimensions and margins
    page_width, page_height = landscape(letter)
    margin = inch
    cell_width = (page_width - 2 * margin) / 7
    cell_height = (page_height - 2 * margin) / 7  #  row for weekdays
    header_height = 0.5 * inch #seperate header
    x_start = margin
    y_start = page_height - margin - header_height

    # Month title
    canvas.setFont("Helvetica-Bold", 24)
    canvas.drawString(x_start, page_height - margin + 0.25 * inch, calendar.month_name[month] + " " + str(year)) #move title
    #y_start -= 0.5 * inch  # Space after title REMOVE


    # Weekday headers (starting with Sunday)
    canvas.setFont("Helvetica-Bold", 12)
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, day in enumerate(weekdays):
        x = x_start + i * cell_width
        canvas.drawString(x + 0.2 * inch, y_start + 0.2 * inch, day) #shift

    #y_start -= cell_height #No need to subtract here

     # Get calendar data (starting with Sunday)
    cal_instance = calendar.Calendar(firstweekday=6)
    cal = cal_instance.monthdayscalendar(year, month)

    # Draw calendar grid and numbers
    canvas.setFont("Helvetica", 10)
    y = y_start
    for week in cal:
        x = x_start
        for day in week:
            # Draw cell rectangle
            canvas.rect(x, y-cell_height, cell_width, cell_height) #shift

            # Draw day number
            if day != 0:
                canvas.drawString(x + 0.1 * inch, y + cell_height - 0.2 * inch - cell_height, str(day)) #Shift
                # Lookup if this is in the events, and render.
                date_str = f"{year}-{month:02}-{day:02}"
                draw_events_for_date(canvas, events, date_str, x, y-cell_height, cell_width, cell_height) #Shift

            x += cell_width
        y -= cell_height

def draw_events_for_date(canvas, events, date_str, x, y, cell_width, cell_height):
    """
    Draws events for a given date on the canvas.  Handles stacking and basic truncation.

    Args:
        canvas: Reportlab canvas
        events: Dict of events from config
        date_str: "YYYY-MM-DD" string of day to render
        x: top-left x
        y: top-left y
        cell_width: Day cell width
        cell_height: Day cell height

    """

    event_strings = [] # Array of strings to write

    # Single Events first
    if 'single_events' in events:
        for event in events['single_events']:
            if event['date'] == date_str:
                event_strings.append(event['description'])

    # Recurring Events second.
    if 'recurring_events' in events:
        for event in events['recurring_events']:
            start_date_obj = datetime.strptime(event['start_date'], '%Y-%m-%d').date()

            #check end_date
            if 'end_date' in event:
                end_date_obj = datetime.strptime(event['end_date'], '%Y-%m-%d').date()
            else:
                end_date_obj = None


            current_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            if start_date_obj <= current_date_obj and (end_date_obj is None or current_date_obj <= end_date_obj):
                recurrence_num = int(event['recurrence'][:-1])
                recurrence_unit = event['recurrence'][-1]

                difference = current_date_obj - start_date_obj

                if recurrence_unit == 'w':
                    if difference.days % (recurrence_num*7) == 0:
                        event_strings.append(event['description'])
                elif recurrence_unit == 'm':
                    #For monthly, we want same *day number*.  So, 5th of every month.
                    if current_date_obj.day == start_date_obj.day:
                        #Calculate number of months different.  Can't use days difference.
                        month_diff = (current_date_obj.year - start_date_obj.year) * 12 + (current_date_obj.month - start_date_obj.month)
                        if month_diff % recurrence_num == 0:
                            event_strings.append(event['description'])
                elif recurrence_unit == 'y':
                    if current_date_obj.month == start_date_obj.month and current_date_obj.day == start_date_obj.day:
                         year_diff = current_date_obj.year - start_date_obj.year
                         if year_diff % recurrence_num == 0:
                             event_strings.append(event['description'])

    #Now draw the events.
    canvas.setFont("Helvetica", 8)  # Changed font size to 8
    y_offset = 0.1 * inch  # Start at bottom
    for event_str in event_strings:
        canvas.drawString(x + 0.1*inch, y + y_offset, event_str)
        y_offset += 0.15 * inch #move up



# --- Main Script ---

def main():
    """Main function to parse arguments, load config, and generate the calendar."""

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Generate a monthly calendar PDF.")
    parser.add_argument("config_file", nargs='?', help="Path to the YAML configuration file.")
    parser.add_argument("--template", action="store_true", help="Generate a template YAML config file.")
    parser.add_argument("-o", "--output", default="calendar.pdf", help="Output PDF filename (default: calendar.pdf)") #Added output
    args = parser.parse_args()

    if args.template:
        create_template_config()
        return

    if args.config_file is None:
        parser.error("You must specify a config file or use --template.")

    # --- Config File Loading ---
    try:
        with open(args.config_file, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config_file}")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file: {e}")
        return

    # --- Config Validation ---
    validation_errors = validate_config(config)
    if validation_errors:
        print("Errors in config file:")
        for error in validation_errors:
            print(f"- {error}")
        return

    # --- PDF Generation ---
    c = canvas.Canvas(args.output, pagesize=landscape(letter)) #Use output here

    for month_str in config['months_to_print']:
        year, month = map(int, month_str.split('-'))
        create_calendar_page(c, year, month, config['events'])
        c.showPage()  # Finish the current page and start a new one

    c.save()
    print(f"Calendar PDF generated: {args.output}") #Use variable here

if __name__ == "__main__":
    main()
