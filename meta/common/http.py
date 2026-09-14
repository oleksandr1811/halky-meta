import time
import requests

def download_binary_file(sess, path, url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(path, "wb") as f:
                r = sess.get(url, stream=True)
                r.raise_for_status()
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
            return
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Error downloading {url} (attempt {attempt + 1}/{max_retries}): {e}")
            time.sleep(2 ** attempt)
