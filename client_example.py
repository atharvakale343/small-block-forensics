import pathlib

from flask_ml.flask_ml_client import MLClient  # type: ignore
from flask_ml.flask_ml_server.constants import DataTypes  # type: ignore

url = "http://127.0.0.1:5000/execute"  # The URL of the server
client = MLClient(url)  # Create an instance of the MLClient object

root = pathlib.Path(__file__).parent.resolve()

# The inputs to be sent to the server
inputs = [
    {"input_type": "TARGET_FOLDER", "file_path": f"{root.joinpath("target_folder")}"},
    {"input_type": "KNOWN_DATASET", "file_path": f"{root.joinpath("known_dataset")}"},
    {"input_type": "OUTPUT_FOLDER", "file_path": f"{root.joinpath("out")}"},
]

data_type = DataTypes.TEXT  # The type of the input data

# Parameters of the model
parameters = {"block_size": 4194304, "target_probability": 0.99}

response = client.request(inputs, data_type, parameters)  # Send a request to the server
print(response)  # Print the response
