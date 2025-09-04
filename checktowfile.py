import json

CONFIG_PATH = "/root/V2IpLimit/config.json"  # Contains SPECIAL_LIMIT inside
DB_PATH = "/root/V2IpLimit/SPECIAL_LIMIT_DB.json"  # Main database file

def load_json_file(path):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {path}: {e}")
        return {}

def compare_special_limits():
    config_data = load_json_file(CONFIG_PATH)
    db_data = load_json_file(DB_PATH)

    config_special = config_data.get("SPECIAL_LIMIT", {})

    # Entries present in DB but missing from config
    only_in_db = {k: v for k, v in db_data.items() if k not in config_special}

    # Entries present in config but missing from DB
    only_in_config = {k: v for k, v in config_special.items() if k not in db_data}

    # Common usernames with different values
    different_values = {
        k: (config_special[k], db_data[k])
        for k in config_special.keys() & db_data.keys()
        if config_special[k] != db_data[k]
    }

    print("?? Present in DB but missing in config:")
    print(json.dumps(only_in_db, indent=4))

    print("\n?? Present in config but missing in DB:")
    print(json.dumps(only_in_config, indent=4))

    print("\n?? Common usernames with different values:")
    for k, v in different_values.items():
        print(f"{k}: config = {v[0]}, db = {v[1]}")

if __name__ == "__main__":
    compare_special_limits()
