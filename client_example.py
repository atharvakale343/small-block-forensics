import pathlib

from flask_ml.flask_ml_client import MLClient
from flask_ml.flask_ml_server.constants import DataTypes

url = "http://127.0.0.1:5000/execute"  # The URL of the server
client = MLClient(url)  # Create an instance of the MLClient object
root = pathlib.Path(__file__).parent.resolve()

# The inputs to be sent to the server
inputs = [
    {
        "input": {
            "input_type": "TARGET_FOLDER",
            "file_path": f'{root.joinpath("examples", "target_folder")}',
        },
    },
    {
        "input": {
            "input_type": "KNOWN_DATASET",
            "file_path": f'{root.joinpath("examples", "known_dataset")}',
        },
    },
    {
        "input": {
            "input_type": "OUTPUT_SQL_PATH",
            "file_path": f'{root.joinpath("examples", "out", "known_content_hashes.sqlite")}',
        },
    },
]

data_type = DataTypes.CUSTOM  # The type of the input data

# Parameters of the model
parameters = {"block_size": 4, "target_probability": 0.99}

response = client.request(inputs, data_type, parameters)  # Send a request to the server

print("INFO: Received a response")
print(response)  # Print the response
