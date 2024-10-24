import pathlib

from flask_ml.flask_ml_client import MLClient

url = "http://127.0.0.1:5000/gen_hash_random"  # The URL of the server
client = MLClient(url)  # Create an instance of the MLClient object
root = pathlib.Path(__file__).parent.resolve()

# The inputs to be sent to the server
inputs = {
    "known_content_directory": {"path": f'{root.joinpath("examples", "known_content_directory")}'},
    "output_sql_path": {"path": f'{root.joinpath("examples", "out", "known_content_hashes.sqlite")}'},
    "target_directory": {"path": f'{root.joinpath("examples", "target_directory")}'},
}

# Parameters of the model
parameters = {"block_size": 4, "target_probability": 0.90}

response = client.request(inputs, parameters)  # Send a request to the server

print("INFO: Received a response")
print(response)  # Print the response
