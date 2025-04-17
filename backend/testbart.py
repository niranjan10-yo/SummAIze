import requests

# Define API URL
url = "http://127.0.0.1:8000/summary"

# Replace with a valid `pdf_id` from your database
data = {"pdf_id": 1, "model": "bart-large"}

# Send POST request
response = requests.post(url, data=data)

# Debugging: Print raw response before parsing JSON
print("Raw Response:", response.text)
print("Status Code:", response.status_code)

# Attempt to parse JSON only if the response is valid
if response.status_code == 200:
    print("Response JSON:", response.json())
else:
    print("Error: API did not return a valid response.")
