import requests
import json

def fetch_and_filter_users(city_filter, output_filepath):
    """
    Fetches users data from JSONPlaceholder API, filters by city,
    and writes the filtered data to a JSON file.
    """

    url = "https://jsonplaceholder.typicode.com/users"
    print(f"--- Fetching users from {url} and filtering by city: {city_filter} ---")
    filtered_users = []


    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses

        users = response.json()

        for user in users:
            # Safely access nested dictionary elements
            # Filter users by city
            if user.get('address') and user['address'].get('city') == city_filter:
                filtered_users.append(user)

            # save all the users
            # filtered_users.append(user)

        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            json.dump(filtered_users, outfile, indent=4) #indent for pretty printing

        print(f"Successfully filtered {len(filtered_users)} users and saved to {output_filepath}")

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
    print(f"--- Finished user fetching and filtering ---")


if __name__ == "__main__":
    city_to_filter = "Gwenborough"
    output_file = 'gwenborough_users.json'
    fetch_and_filter_users(city_to_filter, output_file)