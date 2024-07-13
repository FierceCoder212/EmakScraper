import json
import math
from concurrent.futures import ThreadPoolExecutor

import requests


def create_chunks(data, chunk_size):
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


index = 0


def download_images(images: list[dict]):
    global index
    for image in images:
        print(f'At index : {index} out of {len(images_data)}')
        index += 1
        image_url = image['Url']
        image_filename = image['FileName']
        print(f'Downloading file at url : {image_url}')
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(f'Images/{image_filename}', 'wb') as file:
                file.write(response.content)
        else:
            print(json.dumps({
                'Error when downloading img': {
                    'StatusCode': response.status_code,
                    'Response': response.text
                }
            }, indent=4))


with open('imagesData.json', 'r') as images_data_file:
    images_data = json.loads(images_data_file.read())

n_threads = 20

chunk_size = math.ceil(len(images_data) / n_threads)

chunks = list(create_chunks(images_data, chunk_size))

with ThreadPoolExecutor(max_workers=n_threads) as pool:
    # Submit chunks to the pool
    futures = [pool.submit(download_images, chunk) for chunk in chunks]

    # Optionally, wait for all tasks to complete
    for future in futures:
        future.result()
