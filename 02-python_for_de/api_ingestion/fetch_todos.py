import requests
import json

def fetch_todos(num_todos = 5):
    """
    Fetches a list of todos from JSONPlaceholder API and prints their ID and title
    """

    url = "https://jsonplaceholder.typicode.com/todos"
    print(f"--- Fetching {num_todos} todos from {url} ---")

    try:
        response = requests.get(url, timeout=10) # Add a timeout for robustness
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        todos = response.json()

        print(f"Successfully fetched {len(todos)} todos. Displaying first {num_todos}: ")
        for i, todo in enumerate(todos):
            if i >= num_todos:
                break
            print(f"ID: {todo.get('id', 'N/A')}, Title: {todo.get('title', "No Title")}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timed out: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response.")
    print(f"--- Finished fetching todos ---")

if __name__ == "__main__":
    fetch_todos(num_todos=10)
    