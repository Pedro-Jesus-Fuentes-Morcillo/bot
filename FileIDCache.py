import os
import json
from constants import (
    BASE_DIR, DATA_DIR,
    MEDIA_DIR, CACHE_FILE_PATH
)

class FileIDCache:
    def __init__(self, cache_file=CACHE_FILE_PATH):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f)

    def get_file_id(self, file_key):
        return self.cache.get(file_key)

    def set_file_id(self, file_key, file_id):
        self.cache[file_key] = file_id
        self.save_cache()
        
    def clear_cache(self):
        os.remove(CACHE_FILE_PATH)
