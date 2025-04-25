import json
from datetime import datetime

def load_json_with_datetime(file_path):
    """
    Load a JSON file and convert timestamp strings to datetime objects.

    Args:
        file_path (str): Path to the JSON file

    Returns:
        list: List of dictionaries with timestamp fields converted to datetime objects
    """
    # Load JSON data from file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process each item to convert timestamp fields to datetime objects
    for item in data:
        # Convert the creation date
        if 'date_created' in item:
            item['date_created'] = datetime.fromisoformat(item['date_created'])



    return data

# Example usage
if __name__ == "__main__":
    file_path = "data/simplified_posts.json"  # Replace with your actual file path
    data = load_json_with_datetime(file_path)

    print(data[0].keys())  # Print the first item to verify the conversion
