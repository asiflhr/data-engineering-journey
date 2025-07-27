import csv
import json
import os
import logging
import configparser
import pendulum
from collections import defaultdict

# --- Database Imports (choose one, SQLAlchemy is more robust)
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Numeric
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import insert as pg_insert

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration Loading ---
def load_config(config_file):
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    config.read(config_file)
    return config

# === Database Setup (SQLAlchemy) ===
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(String(50), primary_key=True)
    product_name = Column(String(255), nullable=False)
    category = Column(String(100))
    base_price = Column(Numeric(10, 2))
    supplier_id = Column(String(50))
    stock_quantity = Column(Integer)
    last_updated = Column(DateTime)
    current_value = Column(Numeric(10, 2))

    def __repr__(self):
        return f"<Product(id='{self.product_id}', name='{self.product_name}')"

def get_db_engine(config):
    db_config = config['database']
    db_url = (
        f"postgresql+psycopg2://{db_config['db_user']}:{db_config['db_password']}@"
        f"{db_config['db_host']}:{db_config['db_port']}/{db_config['db_name']}"
    )
    return create_engine(db_url)

def create_table(engine):
    Base.metadata.create_all(engine)
    logging.info("Ensured 'products' table exists.")

# --- ETL Logic ---
def run_etl_pipeline(config_file):
    try:
        config = load_config(config_file)
        paths = config['paths']
        data_input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), paths['data_input_dir'])
        bad_records_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), paths['bad_records_dir'])
        os.makedirs(bad_records_dir, exist_ok=True)

        current_date_str = pendulum.now().format('YYYYMMDD')
        bad_records_filepath = os.path.join(bad_records_dir, f"bad_records_{current_date_str}.jsonl")

        engine = get_db_engine(config)
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        products_data = {} # To store data from CSV
        inventory_data = {} # To store data from JSON

        # --- Extract Products from CSV ---
        products_csv_file = os.path.join(data_input_dir, f"products_{current_date_str}.csv")
        logging.info(f"Extracting products from {products_csv_file}")
        if os.path.exists(products_csv_file):
            with open(products_csv_file, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                for row_num, row in enumerate(reader, start=2): # Start from the line number 2
                    product_id = row.get("ProductID", '').strip()
                    name = row.get('Name', '').strip()
                    category = row.get('Category', '').strip()
                    base_price_str = row.get('BasePrice', '').strip()
                    supplier_id = row.get('SupplierID', '').strip()

                    validation_errors = []

                    # Validation: ProductID
                    if not product_id:
                        validation_errors.append("Missing ProductID")

                    # Validation: Name
                    if not name:
                        validation_errors.append("Missing Product Name")

                    # Validation: Category
                    validation_categories = {"Electronics", "Books", "Apparel", "Home Goods"}
                    if not category or category not in validation_categories:
                        validation_errors.append(f"Invalid or missing Category: '{category}'")

                    # Validation: BasePrice
                    try:
                        base_price = float(base_price_str)
                        if base_price <= 0:
                            validation_errors.append(f"BasePrice must be positive: '{base_price_str}'")
                    except ValueError:
                        validation_errors.append(f"Invalid BasePrice format: '{base_price_str}'")
                        base_price = None # Set to None if invalid to avoid further errors

                    if validation_errors:
                        with open(bad_records_filepath, 'a', encoding='utf-8') as bad_file:
                            json.dump({
                                "source": "products_csv",
                                "row_data": row,
                                "reason": validation_errors,
                                "timestamp": pendulum.now().to_iso8601_string()
                            }, bad_file)
                            bad_file.write('\n')
                        logging.warning(f"Bad record from CSV (line {row_num}): {', '.join(validation_errors)}. Logged to bad records file.")
                        continue # Skip to next row

                    products_data[product_id] = {
                        'product_id': product_id,
                        'product_name': name,
                        'category': category,
                        'base_price': base_price,
                        'supplier_id': supplier_id
                    }
        else:
            logging.warning(f"Products CSV file not found: {products_csv_file}. Skipping product extraction.")

        
        # Extract Inventory from JSON
        inventory_json_file = os.path.join(data_input_dir, f"inventory_{current_date_str}.json")
        logging.info(f"Extracting inventory from {inventory_json_file}")
        if os.path.exists(inventory_json_file):
            with open(inventory_json_file, mode='r', encoding='utf-8') as infile:
                for row_num, line in enumerate(infile, start=1): # Line numbers for JSON
                    try:
                        inventory_entry = json.loads(line.strip())

                        product_id = inventory_entry.get('product_id', '').strip()
                        stock_quantity_raw = inventory_entry.get('stock_quantity')
                        last_updated_str = inventory_entry.get('last_updated', '').strip()

                        validation_errors = []

                        # Validation: product_id
                        if not product_id:
                            validation_errors.append('Missing product_id')

                        # Validation: stock_quantity
                        try:
                            stock_quantity = int(stock_quantity_raw)
                            if stock_quantity < 0:
                                validation_errors.append(f"Stock quantity must be non-negative: '{stock_quantity_raw}'")
                        except (ValueError, TypeError):
                            validation_errors.append(f"Invalid stock_quantity format: '{stock_quantity_raw}'")
                            stock_quantity = None

                        # Validation: last_updated
                        try:
                            last_updated = pendulum.parse(last_updated_str)
                        except (ValueError, TypeError):
                            validation_errors.append(f"Invalid last_updated format: '{last_updated_str}'")
                            last_updated = None

                        if validation_errors:
                            with open(bad_records_filepath, 'a', encoding='utf-8') as bad_file:
                                json.dump({
                                    "source": "inventory_json",
                                    "row_data": inventory_entry,
                                    "reason": validation_errors,
                                    "timestamp": pendulum.now().to_iso8601_string()
                                }, bad_file)
                                bad_file.write('\n')
                            logging.warning(f"Bad record from JSON (line {row_num}): {', '.join(validation_errors)}. Logged to bad records file.")
                            continue

                        inventory_data[product_id] = {
                            'stock_quantity': stock_quantity,
                            'last_updated': last_updated
                        }
                    except json.JSONDecodeError:
                        logging.error(f"Invalid JSON line (line {row_num}): {line.strip()}. Logged to bad records.")
                        with open(bad_records_filepath, 'a', encoding='utf-8') as bad_file:
                            json.dump({
                                "source": "inventory_json",
                                "raw_line": line.strip(),
                                "reason": ["JSON Decode Error"],
                                "timestamp": pendulum.now().to_iso8601_string()
                            }, bad_file)
                            bad_file.write('\n')
                        continue
        else:
            logging.warning(f"Inventory JSON file not found: {inventory_json_file}. Skipping inventory extraction.")

        # --- Transformation and Merges ---
        transformed_products = []
        for product_id, p_data in products_data.items():
            combined_record = p_data.copy()
            inventory_info = inventory_data.get(product_id)

            if inventory_info:
                combined_record['stock_quantity'] = inventory_info['stock_quantity']
                combined_record['last_updated'] = inventory_info['last_updated']

                # Calculate CurrentValue
                if combined_record['base_price'] is not None and combined_record['stock_quantity'] is not None:
                    combined_record['current_value'] = combined_record['base_price'] * combined_record['stock_quantity']
                else:
                    combined_record['current_value'] = 0.0 # Default if base_price or quantity is invalid
                    logging.warning(f"Could not calculate CurrentValue for ProductID {product_id} due to invalid price/quantity.")
            else:
                logging.warning(f"No inventory data found for ProductID: {product_id}. Setting stock/value to 0/None.")
                combined_record['stock_quantity'] = 0
                combined_record['last_updated'] = None
                combined_record['current_value'] = 0.0

            transformed_products.append(combined_record)

        # Log inventory records that didn't match any product
        for inv_prod_id in inventory_data.keys():
            if inv_prod_id not in products_data:
                logging.warning(f"Inventory record for ProductID {inv_prod_id} has no matching product details. Not loaded.")
                with open(bad_records_filepath, 'a', encoding='utf-8') as bad_file:
                    json.dump({
                        "source": "unmatched_inventory",
                        "product_id": inv_prod_id,
                        "inventory_data": inventory_data[inv_prod_id],
                        "reason": ["No matching product details found"],
                        "timestamp": pendulum.now().to_iso8601_string()
                    }, bad_file)
                    bad_file.write('\n')

        # --- Load into Database ---
        logging.info(f"Loading {len(transformed_products)} valid products into database.")
        for product_dict in transformed_products:
            try:
                # User psycopg2 for direct interaction, or SQLAlchemy's upsert
                stmt = pg_insert(Product.__table__).values(
                    product_id = product_dict['product_id'],
                    product_name = product_dict['product_name'],
                    category = product_dict['category'],
                    base_price = product_dict['base_price'],
                    supplier_id = product_dict['supplier_id'],
                    stock_quantity = product_dict['stock_quantity'],
                    last_updated = product_dict['last_updated'],
                    current_value = product_dict['current_value']
                )
                on_conflict_stmt = stmt.on_conflict_do_update(
                    index_elements=[Product.product_id],
                    set_={
                        'product_name': stmt.excluded.product_name,
                        'category': stmt.excluded.category,
                        'base_price': stmt.excluded.base_price,
                        'supplier_id': stmt.excluded.supplier_id,
                        'stock_quantity': stmt.excluded.stock_quantity,
                        'last_updated': stmt.excluded.last_updated,
                        'current_value': stmt.excluded.current_value
                    }
                )
                session.execute(on_conflict_stmt)
                session.commit()
            except Exception as e:
                session.rollback()
                logging.error(f"Failed to load product {product_dict.get['product_id', 'N/A']} into DB: {e}")
                with open(bad_records_filepath, 'a', encoding='utf-8') as bad_file:
                    json.dump({
                        'source': "db_load_failure",
                        'record': product_dict,
                        'reason': [str(e)],
                        'timestamp': pendulum.now().to_iso8601_string()
                    }, bad_file)
                    bad_file.write('\n')

        session.close()
        logging.info("ETL pipeline completed.")

    except FileNotFoundError as e:
        logging.error(f"Configuration or input file error: {e}")
    except Exception as e:
        logging.critical(f"An unhandled error occured during ETL: {e}", exc_info=True)


if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_script_dir, 'config.ini')

    # Create dummy files and config if they don't exist for easy testing
    data_dir = os.path.join(current_script_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Create config.ini
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as f:
            f.write('[database]\n')
            f.write('db_host = localhost\n')
            f.write('db_port = 5432\n')
            f.write('db-name = your_db_de\n')
            f.write("db_name = your_de_db\n")
            f.write("db_user = your_user\n")
            f.write("db_password = your_password\n") # IMPORTANT: Replace with your actual password!
            f.write("\n[paths]\n")
            f.write("data_input_dir = data\n")
            f.write("processed_output_dir = processed_output\n")
            f.write("bad_records_dir = bad_records\n")
        logging.info(f"Created dummy config.ini at {config_file_path}. Please update database credentials!")
    
    # Create dummy products CSV
    products_csv_path = os.path.join(data_dir, f"products_{pendulum.now().format('YYYYMMDD')}.csv")
    if not os.path.exists(products_csv_path):
        with open(products_csv_path, 'w', newline='') as f:
            f.write("ProductID,Name,Category,BasePrice,SupplierID\n")
            f.write("P001,Laptop Pro,Electronics,1200.00,S001\n")
            f.write("P002,Mechanical Keyboard,Electronics,120.00,S002\n")
            f.write("P003,Mystery Novel,Books,15.50,S003\n")
            f.write("P004,Ergonomic Mouse,Electronics,45.00,S001\n")
            f.write("P005,T-Shirt (Large),Apparel,25.00,S004\n")
            f.write("P006,Damaged Product,Electronics,invalid_price,S001\n") # Bad record
            f.write("P007,New Gadget,Electronics,750.00,S005\n") # New product

    # Create dummy inventory JSONL
    inventory_json_path = os.path.join(data_dir, f"inventory_{pendulum.now().format('YYYYMMDD')}.json")
    if not os.path.exists(inventory_json_path):
        with open(inventory_json_path, 'w', newline='') as f:
            f.write(json.dumps({"product_id": "P001", "stock_quantity": 15, "last_updated": "2025-07-25T10:00:00Z"}) + '\n')
            f.write(json.dumps({"product_id": "P002", "stock_quantity": 50, "last_updated": "2025-07-25T10:05:00Z"}) + '\n')
            f.write(json.dumps({"product_id": "P003", "stock_quantity": 100, "last_updated": "2025-07-25T10:10:00Z"}) + '\n')
            f.write(json.dumps({"product_id": "P005", "stock_quantity": 20, "last_updated": "2025-07-25T10:15:00Z"}) + '\n')
            f.write(json.dumps({"product_id": "P_INVALID", "stock_quantity": 5, "last_updated": "2025-07-25T10:20:00Z"}) + '\n') # Unmatched inventory
            f.write(json.dumps({"product_id": "P007", "stock_quantity": 30, "last_updated": "2025-07-25T11:00:00Z"}) + '\n') # New product inventory

    run_etl_pipeline(config_file_path)