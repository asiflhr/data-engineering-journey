import csv
import os
import glob
import logging
from collections import defaultdict
import pendulum # For easy date manipulation

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_last_processed_date(state_file):
    """
    Reads the last processed date from a state file.
    """

    if not os.path.exists(state_file):
        return None
    
    with open(state_file, 'r') as f:
        date_str = f.read().strip()
        if date_str:
            return pendulum.parse(date_str)
        return None
    
def update_last_processed_date(state_file, new_date):
    """"Updates the last processed date in the state file."""

    with open(state_file, 'w') as f:
        f.write(new_date.format('YYYY-MM-DD'))
    logging.info(f"Updated last processed date to {new_date.format('YYYY-MM-DD')}")

def process_daily_transactions(data_dir, output_dir, state_file, high_value_threshold=1000):
    """
    Processes daily transaction files incrementally, aggregates data,
    and writes to an output file.
    """

    os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

    last_processed_date = get_last_processed_date(state_file)
    logging.info(f"Last processed date: {last_processed_date.format('YYYY-MM-DD') if last_processed_date else None}")

    all_transaction_files = sorted(glob.glob(os.path.join(data_dir, 'transactions_*.csv')))

    files_to_process = []
    latest_date_in_files = None

    for filepath in all_transaction_files:
        filename = os.path.basename(filepath)
        # Extract date from filename: transactions_YYYYMMDD.csv

        try:
            file_date_str = filename.split('_')[1].split('.')[0]
            file_date = pendulum.parse(file_date_str)
        except (IndexError, ValueError):
            logging.warning(f"Could not parse date from filename: {filename}. Skipping.")
            continue

        if last_processed_date is None or file_date > last_processed_date:
            files_to_process.append(filepath)
            if latest_date_in_files is None or file_date > latest_date_in_files:
                latest_date_in_files = file_date
        else:
            logging.info(f"Skipping already processed file: {filename}")

    if not files_to_process:
        logging.info("No new transaction files to process.")
        return
    
    logging.info(f"Processing {len(files_to_process)} new files")

    # Data structure for aggregation:
    # Key: (ProductCategory, Region)
    # Value: {'total_sales': float, 'transaction_count': int}
    aggregated_data = defaultdict(lambda: {'total_sales': 0.0, 'transaction_count': 0})

    for filepath in files_to_process:
        logging.info(f"Reading file: {filepath}")

        with open(filepath, mode='r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)

            for row_num, row in enumerate(reader, 2): # Start from 2 for row count in error messages
                try:
                    transaction_id = row['TransactionID']
                    product_category = row['ProductCategory'].strip()
                    region = row['Region'].strip()

                    try:
                        amount = float(row['Amount'])
                        if amount <= 0:
                            raise ValueError("Amount must positive")
                    except ValueError:
                        logging.warning(f"File: {os.path.basename(filepath)}, Row {row_num} (ID: {transaction_id}): Invalid or non-positive Amount '{row['Amount']}'. Skipping row.")
                        continue # Skip to the next row if amount is invalid

                    # Add IsHighValue flag
                    is_high_value = "True" if amount >high_value_threshold else "False"

                    # Aggregate
                    key = (product_category, region)
                    aggregated_data[key]['total_sales'] += amount
                    aggregated_data[key]['transaction_count'] += 1

                except KeyError as e:
                    logging.error(f"Missing expected column '{e}' in file: {os.path.basename(filepath)}, row {row_num}. Skipping row.")
                except Exception as e:
                    logging.error(f"An unexpected error occurred processing row {row_num} in {os.path.basename(filepath)}: {e}. Skipping row.")

    # Prepare data for output
    output_rows = []
    for (category, region), values in aggregated_data.items():
        total_sales = values['total_sales']
        transaction_count = values['transaction_count']
        average_price = total_sales / transaction_count if transaction_count > 0 else 0.0
        output_rows.append({
            'ProductCategory': category,
            'Region': region,
            'TotalSales': f"{total_sales:.2f}",
            'AveragePrice': f"{average_price:.2f}",
            'TransactionCount': transaction_count
        })

    # Write aggregated data to output file
    if output_rows:
        current_date_for_output = latest_date_in_files if latest_date_in_files else pendulum.now()
        output_filename = f"daily_aggregated_sales_{current_date_for_output.format('YYYYMMDD')}.csv"
        output_filepath = os.path.join(output_dir, output_filename)

        fieldnames = ['ProductCategory', 'Region', 'TotalSales', 'AveragePrice', 'TransactionCount']

        with open(output_filepath, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
        logging.info(f"Aggregated data written to {output_filepath}")

        # Update the last processed date only if processing was successful and new file rows found
        if latest_date_in_files:
            update_last_processed_date(state_file, latest_date_in_files)
    else:
        logging.info("No new valid transactions to aggregate.")


if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))

    # Define paths relative to the current script
    data_directory = os.path.join(current_script_dir, 'data')
    output_directory = os.path.join(current_script_dir, 'processed_output')
    state_file_path = os.path.join(current_script_dir, 'last_processed_date.txt')

    # Ensure data directory exists and create dummy files if they don't
    os.makedirs(data_directory, exist_ok=True)

    # Create dummy data files if they don't exists
    if not os.path.exists(os.path.join(data_directory, 'transactions_20250723.csv')):
        with open(os.path.join(data_directory, 'transactions_20250723.csv'), 'w', newline='') as f:
            f.write("TransactionID,Timestamp,CustomerID,ProductCategory,Amount,Region\n")
            f.write("T001,2025-07-23 09:00:00,C101,Electronics,500.00,North\n")
            f.write("T002,2025-07-23 09:15:30,C102,Books,35.50,East\n")
            f.write("T003,2025-07-23 10:00:00,C101,Electronics,120.00,North\n")
            f.write("T004,2025-07-23 11:30:00,C103,Clothing,75.00,South\n")
            
    if not os.path.exists(os.path.join(data_directory, 'transactions_20250724.csv')):
        with open(os.path.join(data_directory, 'transactions_20250724.csv'), 'w', newline='') as f:
            f.write("TransactionID,Timestamp,CustomerID,ProductCategory,Amount,Region\n")
            f.write("T005,2025-07-24 10:00:00,C104,Electronics,1500.00,West\n")
            f.write("T006,2025-07-24 10:30:00,C101,Books,20.00,North\n")
            f.write("T007,2025-07-24 11:00:00,C105,Clothing,120.00,East\n")
            f.write("T008,2025-07-24 11:45:00,C102,Books,60.00,South\n")
            f.write("T009,2025-07-24 12:00:00,C104,Electronics,250.00,West\n")

    process_daily_transactions(data_directory, output_directory, state_file_path)

    # Simulate running again to show incremental logic
    logging.info("\n--- Running script again to demonstrate incremental processing ---")
    process_daily_transactions(data_directory, output_directory, state_file_path)

    # To test with a new day's data, create transactions_20250725.csv manually
    # and run the script again.