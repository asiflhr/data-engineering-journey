import requests
import json
import os
import logging
import time
import pendulum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_comment_schema(comment):
    """Basic schema validation for a comment object."""

    required_fields = {
        'postId': int,
        'id': int,
        'name': str,
        'email': str,
        'body': str
    }

    for field, expected_type in required_fields.items():
        if field not in comment:
            logging.warning(f"Comment (ID: {comment.get('id', 'N/A')}) missing required field: '{field}'")
            return False
        if not isinstance(comment[field], expected_type):
            logging.warning(f"Comment (ID: {comment.get('id', 'N/A')}) field '{field}' has unexpected type: {type(comment[field])}, expected {expected_type}")
            return False
    return True

def fetch_paginated_data(base_url, limit_per_page=10, max_items=50, sleep_time=0.1):
    """
    Simulates fetching paginated data from an API.
    For JSONPlaceholder, it just fetches all and yields in batches.
    """

    all_data = []

    try:
        logging.info(f"Fetching all data from {base_url} for simulated pagination...")
        response = requests.get(base_url, timeout=15)
        response.raise_for_status()
        all_data = response.json()
        logging.info(f"Successfully fetched {len(all_data)} items in total.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching initial data from {base_url}: {e}")
        return
    
    fetched_count = 0
    while fetched_count < min(len(all_data), max_items):
        page_data = all_data[fetched_count : fetched_count + limit_per_page]
        yield page_data
        fetched_count += len(page_data)
        logging.info(f"Simulated page fetched. Total fetched: {fetched_count}/{min(len(all_data), max_items)}")
        time.sleep(sleep_time) # Simulate delay between pages/requests

def fetch_and_enrich_comments(output_dir):
    """
    Fetches comments, dynamically fetches post details, validates,
    and saves enriched data to JSON file.
    """

    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"enriched_comments_{pendulum.now().format('YYYYMMDD')}.jsonl"
    output_filepath = os.path.join(output_dir, output_filename)

    comment_api_url = "https://jsonplaceholder.typicode.com/comments"
    post_api_url_template = "https://jsonplaceholder.typicode.com/posts/{post_id}"

    processed_count = 0 # Initialize the variable
    skipped_count = 0   # Initialize the variable
    
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
        # Simulate fetching comments in batches
        for comments_batch in fetch_paginated_data(comment_api_url, limit_per_page=20, max_items=100): # Process up to 100 comments for demonstration
            if not comments_batch:
                continue

            for comment in comments_batch:
                if not validate_comment_schema(comment):
                    skipped_count += 1
                    continue # Skip to the next comment if validation fails

                post_id = comment.get('postId')
                if not post_id:
                    logging.warning(f"Comment (ID: {comment.get('id', 'N/A')}) has no postId. Skipping post detail fetch.")
                    comment['postTitle'] = 'N/A' # Add a placeholder
                    enriched_comment = comment
                else:
                    # Fetch post details for the current comment
                    post_detail_url = post_api_url_template.format(post_id=post_id)
                    try:
                        post_response = requests.get(post_detail_url, timeout=5)
                        post_response.raise_for_status()
                        post_data = post_response.json()
                        comment['postTitle'] = post_data.get('title', 'No Title Found')
                        enriched_comment = comment
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error fetching post {post_id} for comment {comment.get('id', 'N/A')}: {e}. Skipping post details.")
                        comment['postTitle'] = 'Error Fetching Post Title'
                        enriched_comment = comment
                    time.sleep(0.05) # Small delay to be polite to the API

                # Write enriched comment to JSONL
                outfile.write(json.dumps(enriched_comment) + '\n')
                processed_count += 1

    logging.info(f"Finished processing. Total processed comments: {processed_count}. Skipped comments due to validation: {skipped_count}.")
    logging.info(f"Enriched comments saved to {output_filepath}")


if __name__ == "__main__":
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    output_data_directory = os.path.join(current_script_dir, 'data')

    fetch_and_enrich_comments(output_data_directory)