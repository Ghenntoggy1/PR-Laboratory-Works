import json
if __name__ == '__main__':
    # serialize string
    data = "alpha"
    print(f"Data: {data}")
    serialized_data = json.dumps(data)
    print(f"Serialized Data: {serialized_data}")