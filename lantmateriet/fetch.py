import os
import requests
import json
import base64
import argparse

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


def download_and_save_tif(url, filepath, headers: dict|None=None, force_dl=False):
    try:
        if headers and "username" in headers.keys() and "password" in headers.keys():
            credentials = f"{headers["username"]}:{headers["password"]}".encode("utf-8")
            encoded_credentials = base64.b64encode(credentials).decode("utf-8")
            headers.update({
                "Authorization": f"Basic {encoded_credentials}"
            })
            headers.pop("username")
            headers.pop("password")


        if force_dl or not os.path.exists(filepath):
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"TIFF file downloaded and saved successfully to {filepath}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading TIFF file: {e}")
    except IOError as e:
        print(f"Error writing TIFF file: {e}")
    except Exception as e:
        print(f"An unexpected error occured: {e}")


def check_if_next_link_exists(search_data):
    next_exists = False
    out_links = []
    for l in search_data["links"]:
        if l["rel"] == "next":
            next_exists = True
            out_links.append(l["href"])

    return next_exists, out_links


def main(search_url, out_dir, bbox):
    params = {
        "bbox": bbox,
        "limit": 50
    }
    links = []
    next_links = [search_url]

    while next_links:
        next = next_links.pop(0)
        search_data = make_request(next, params=params, type="json")

        for feat in search_data["features"]:
            links.append(feat["assets"]["data"]["href"])

        exists, new_nexts = check_if_next_link_exists(search_data)
        if exists:
            params = None
            next_links.extend(new_nexts)

    for link in links:
        output_file_path = os.path.join(out_dir, link.split("data/")[1])
        download_and_save_tif(link, output_file_path, headers=creds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", help="Out directory")
    parser.add_argument("--bbox", help="Bounding box in LONG,LAT,LONG,LAT coord.")
    parser.add_argument("--type", help="bild / höjd", required=True)

    args = parser.parse_args()

    if args.type == "bild":
        search_url = URL_BILD+"/search"
    elif args.type == "höjd":
        search_url = URL_HOJD+"/search"
    else:
        print(f"Bad type. Expecting bild or höjd, got {args.type}")
        exit()

    main(search_url, args.o, args.bbox)
