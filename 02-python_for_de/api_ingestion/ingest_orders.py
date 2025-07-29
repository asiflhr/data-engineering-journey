import requests
import json
import os
import logging
import configparser
import time
import functools
import pendulum

# configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuring Loading
def load_config(config_file):
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file not found: {config_file}")
    config.read(config_file)
    return config

# --- Retry Decorator ----
def retry(max_attempts=3, delay_seconds=1, backoff_factor=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                    logging.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}")
                    if attempt < max_attempts - 1:
                        sleep_time = delay_seconds * (backoff_factor ** attempt)
                        logging.info(f"Retrying in {sleep_time:0.2f} seconds...")
                        time.sleep(sleep_time)
                    else:
                        logging.error(f"Max retries reached for {func.__name__}. Giving up.")
                        raise
        return wrapper
    return decorator

# --- API Client ---
class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url

    @retry(max_attempts=5, delay_seconds=0.5)
    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        logging.debug(f"Making request to: {url} with params: {params}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    
    def get_users(self):
        """Fetches all users (simulated orders)."""
        logging.info("Fetching users (simulated orders)...")
        return self._make_request(f"/users")
    
    def get_user_todos(self, user_id):
        """Fetches todos for a specific user (simulated order items)."""
        logging.info(f"Fetching todos for user_id: {user_id} (simulated order items)...")
        return self._make_request(f"/users/{user_id}/todos")

# --- State Management for Deduplication ---
def get_processed_ids(state_file):
    if not os.path.exists(state_file):
        return set()
    with open(state_file, 'r') as f:
        return set(line.strip() for line in f if line.strip())
    
def add_processed_id(state_file, item_id):
    with open(state_file, 'a') as f:
        f.write(f"{item_id}\n")

# --- Main Ingestion Logic ---
def ingest_api_data(config_file):
    try:
        config = load_config(config_file)
        api_config = config['api']
        paths = config['paths']

        base_api_url = api_config['base_url']
        output_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), paths['output_data_dir'])
        processed_ids_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), paths['processed_ids_file'])

        api_client = ApiClient(base_api_url)
        processed_user_ids = get_processed_ids(processed_ids_file)

        logging.info(f"Already processed user IDs: {len(processed_user_ids)}")

        all_users = api_client.get_users()
        if not all_users:
            logging.info("No users fetched from API. Exiting.")
            return
        
        # Prepare ouput directory with partitioning (e.g: /YYYY/MM/DD)
        current_datetime = pendulum.now()
        partition_path = os.path.join(
            output_data_dir,
            'orders', # Or a more generic name like 'ingested_data'
            current_datetime.format('YYYY'),
            current_datetime.format('MM'),
            current_datetime.format('DD')
        )
        os.makedirs(partition_path, exist_ok=True)

        output_filepath = os.path.join(
            partition_path,
            f"Orders_{current_datetime.format('YYYYMMDD_HHmmss')}.jsonl"
        )

        logging.info(f"Saving enriched data to: {output_filepath}")

        successful_ingestion = 0
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            for user in all_users:
                user_id = str(user.get('id'))
                if not user_id:
                    logging.warning(f"User record without ID found: {user}. Skipping.")
                    continue

                if user_id in processed_user_ids:
                    logging.info(f"User ID {user_id} already processed. Skipping")
                    continue

                try:
                    user_todos = api_client.get_user_todos(user_id)

                    # Deduplicate todos (simple example: convert to set of dicts via tuple)
                    # Note: For complex dicts, you might need a custom hashable representation
                    seen_todos = set()
                    unique_todos = []
                    for todo in user_todos:
                        todo_tuple = tuple(sorted(todo.items())) # make it hashable
                        if todo_tuple not in seen_todos:
                            seen_todos.add(todo_tuple)
                            unique_todos.append(todo)

                    enriched_user_data = user.copy()
                    enriched_user_data['todos'] = unique_todos

                    outfile.write(json.dumps(enriched_user_data) + '\n')
                    add_processed_id(processed_ids_file, user_id)
                    successful_ingestion += 1

                except requests.exceptions.RequestException as e:
                    logging.error(f"Failed to fetch todos for user ID {user_id}: {e}. Skipping this user.")
                except json.JSONDecodeError:
                    logging.error(f"Failed to decode JSON for user ID {user_id} or their todos. Skipping this user.")
                except Exception as e:
                    logging.error(f"An unexpected error occured for user ID {user_id}: {e}. Skipping this user.")

        logging.info(f"API ingestion completed. Successfully ingested {successful_ingestion} new users.")

    except FileNotFoundError as e:
        logging.error(f"Configuration file error: {e}")
    except Exception as e:
        logging.critical(f"An unhandled error occurred during API ingestion: {e}", exc_info=True)

    
if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_script_dir, 'config.ini')
    
    # Create dummy config if it doesn't exist
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as f:
            f.write("[api]\n")
            f.write("base_url: = https://jsonplaceholder.typicode.com\n")
            f.write("\n[paths]\n")
            f.write("output_data_dir = data\n")
            f.write("processed_ids_file = processed_user_ids.txt\n")
        logging.info(f"Created dummy config.ini at {config_file_path}. Base URL is JSONPlaceholder.")

    ingest_api_data(config_file_path)

    # To demonstrate deduplication, run the script again.
    logging.info("\n--- Running API ingestion again to demonstrate deduplication ---")
    ingest_api_data(config_file_path)
    