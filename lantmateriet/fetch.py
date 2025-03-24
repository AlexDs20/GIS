import requests
import json
import base64

from pprint import pprint

URL_BILD = "https://api.lantmateriet.se/stac-bild/v1"
URL_HOJD = "https://api.lantmateriet.se/stac-hojd/v1"

GET_SEARCH_PARAMS = {
    "collections": None,
    "ids": None,
    "bbox": None,
    "intersects": None,
    "datetime": None,
    "limit": None,
    "query": None,
    "sortby": None,
    "fields": None,
    "token": None,
    "filter": None,
    "filter-crs": None,
    "filter-lang": None,
}

CREDENTIALS = "/home/alexandre/credentials.json"

with open(CREDENTIALS) as fp:
    creds = json.load(fp)["geotorget"]


def make_request(url, params: dict=None, headers: dict=None, type: str="json"):
    if params:
        url_params = "&".join(f"{k}={v}" for k, v in params.items())
        url = url + "?" + url_params

    if headers and "username" in headers.keys() and "password" in headers.keys():
        credentials = f"{headers["username"]}:{headers["password"]}".encode("utf-8")
        encoded_credentials = base64.b64encode(credentials).decode("utf-8")
        headers.update({
            "Authorization": f"Basic {encoded_credentials}"
        })
        headers.pop("username")
        headers.pop("password")

    response = requests.get(url, params=params, headers=headers)
    if type == "json":
        return response.json()
    elif type == "raw":
        return response.content



def write_tif_data_to_file(data, filepath):
    """
    Writes raw TIFF data to a file.

    Args:
        data (bytes): The raw TIFF data (bytes object).
        filepath (str): The path to the file where the data should be written.
    """
    try:
        with open(filepath, 'wb') as f:  # 'wb' for write binary
            f.write(data)
        print(f"TIFF data written successfully to {filepath}")
    except Exception as e:
        print(f"Error writing TIFF data to file: {e}")

# Example usage (assuming you've already downloaded the data):

headers = creds

if headers and "username" in headers.keys() and "password" in headers.keys():
    credentials = f"{headers["username"]}:{headers["password"]}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("utf-8")
    headers.update({
        "Authorization": f"Basic {encoded_credentials}"
    })
    headers.pop("username")
    headers.pop("password")


def download_and_save_tif(url, filepath):
    """
    Downloads a TIFF file from a URL and saves it to a file.

    Args:
        url (str): The URL of the TIFF file.
        filepath (str): The path to save the downloaded TIFF file.
    """
    try:
        response = requests.get(url, headers=headers, stream=True) # stream=True is crucial for large files
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): # process the file in chunks
                f.write(chunk)

        print(f"TIFF file downloaded and saved successfully to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading TIFF file: {e}")
    except IOError as e:
        print(f"Error writing TIFF file: {e}")
    except Exception as e:
        print(f"An unexpected error occured: {e}")

# example usage.
# replace with your URL and output file path.
tif_url =  "https://dl1.lantmateriet.se/bild/data/orto/se0_5c_sweref/2009_J/o72900_5050_50_fi09.tif"
output_file_path = "/home/alexandre/Desktop/test_dl.tif"
download_and_save_tif(tif_url, output_file_path)



# def main():
#     params = {
#         "bbox": "15.122,65.7567,15.3297,65.9744",
#         "limit": 10000
#     }
#     links = make_request(URL_BILD+"/search", params=params, type="json")
#
#     links = "https://dl1.lantmateriet.se/bild/data/orto/se0_5c_sweref/2009_J/o72900_5050_50_fi09.tif"
#     headers = creds
#     data = make_request(links, headers=headers, type="raw")
#
#     with open("/home/alexandre/Desktop/test_dl.tif", "wb") as fp:
#         fp.write(data)
#
#
#
#
# if __name__ == "__main__":
#     main()
