import pefile, requests, os, time, threading, logging, shelve
from datetime import datetime
from flask import Flask
from waitress import serve
import schedule

DOWNLOADURL = "https://download.voipit.nl/HIPIN/HIPIN.exe"
FILENAME = "HIPIN.exe"
CACHEFILE = "cache"
CACHEKEY = "cached_api"
EXPIRATION_TIME = 86400 #24 hours cache

app = Flask(__name__)

@app.route("/hipin")
def api_handler():
    return get_product_version(FILENAME)

def string_time():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

## caching
def get_cached_json():
    with shelve.open(CACHEFILE) as cache:
        if CACHEKEY in cache:
            cached_data = cache[CACHEKEY]
            timestamp, data = cached_data['timestamp'], cached_data['data']
            current_time = time.time()
            if current_time - timestamp <= EXPIRATION_TIME:
                return data
    return None

def cache_json(data):
    with shelve.open(CACHEFILE) as cache:
        cache[CACHEKEY] = {'timestamp': time.time(), 'data': data}

## get product version, use cache when possible
def get_product_version(file_path):
    cached_data = get_cached_json()
    if cached_data:
        return cached_data
    else:
        try:
            pe = pefile.PE(file_path)
            string_version_info = {}
            for fileinfo in pe.FileInfo[0]:
                if fileinfo.Key.decode() == "StringFileInfo":
                    for st in fileinfo.StringTable:
                        for entry in st.entries.items():
                            string_version_info[entry[0].decode()] = entry[1].decode()
            cache_json(string_version_info)
            return string_version_info
        except pefile.PEFormatError as e:
            print(string_time() + f" | Error retrieving product version: {e}")
    return None

## file handler, clean and (re)download
def handle_file(path):
    print(string_time() + " | Cleaning files...")
    if os.path.exists(path):
        os.remove(path)
    url = "https://download.voipit.nl/HIPIN/HIPIN.exe"
    print(string_time() + " | Downloading files...")
    response = requests.get(url)
    with open(path, "wb") as file:
        file.write(response.content)
    print(string_time() + " | Downloaded!")

schedule.every(12).hours.do(handle_file, path=FILENAME)

def server_handler():
    serve(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    # download / cleanup files
    handle_file(FILENAME)

    # set logging
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)

    # start webserver as a thread
    threading_job = threading.Thread(target=server_handler)
    threading_job.start()

    # run scheduled task
    while True:
        schedule.run_pending()
        time.sleep(60)