import csv

def clean_and_aggregate_sales(input_filepath, output_filepath):
    """
    Cleans and aggregates sales data from a CSV file.
    Reads sales data from the input CSV file, cleans it, calculates total revenue per product,
    and writes the aggregated data to an output CSV file.

    Args:
        input_filepath (str): Path to the input CSV file containing sales data.
        output_filepath (str): Path to the output CSV file for cleaned and aggregated data.
    """
    
    product_revenue = {}

    with open(input_filepath, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            product = row['Product'].strip()

            try:
                quantity = int(row['Quantity'])
            except ValueError:
                print(f"Warning: Invalid quantity '{row['Quantity']}' for product '{product}'. Skipping row.")
                continue # skip to the nex row if quantity is invalid

            try:
                price = float(row['Price'])
            except ValueError:
                print(f"Warning: Invalid price '{row['Price']}' for product '{product}'. Setting price to 0.")
                price = 0.0

            row_revenue = quantity * price

            # Aggregated revenue by product
            product_revenue[product] = product_revenue.get(product, 0.0) + row_revenue

    # Write aggregated data to a new CSV
    with open(output_filepath, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Product', 'TotalRevenue']) # Write header

        for product, total_rev in product_revenue.items():
            writer.writerow([product, f"{total_rev:.2f}"]) # Format to 2 decimal places

    print(f"Cleaned and aggregated sales data written to {output_filepath}")


if __name__ == "__main__":
    input_file = 'sales_data.csv'
    output_file = 'product_revenue.csv'
    clean_and_aggregate_sales(input_file, output_file)
    
