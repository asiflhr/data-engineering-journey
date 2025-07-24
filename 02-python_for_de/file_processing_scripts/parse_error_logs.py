import json

def parse_error_logs(log_fliepath):
    """
    Reads a JSON log file, filters for 'ERROR' level messages,
    and prints their timestamp and message.
    """

    print(f"--- Parsing error logs from {log_fliepath} ---")

    with open(log_fliepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                log_entry = json.loads(line.strip())
                if log_entry.get('level') == 'ERROR':
                    timestamp = log_entry.get('timestamp', 'N/A')
                    message = log_entry.get('message', 'No message')
                    print(f"Timestamp: {timestamp}, Message: {message}")
            except json.JSONDecodeError:
                print(f"Warning: Could not parse line {line_num} as JSON: {line.strip()}")
            except KeyError as e:
                print(f"Warning: Missing key {e} in log entry on line {line_num}: {line.strip()}")

    print(f"--- Finished parsing error logs ---")

if __name__ == "__main__":
    log_file = 'app_logs.json'
    parse_error_logs(log_file)