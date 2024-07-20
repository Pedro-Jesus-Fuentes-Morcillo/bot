# constants.py

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, 'data')

CACHE_FILE_PATH = os.path.join(BASE_DIR, 'data', 'file_id_cache.json')

MEDIA_DIR = os.path.join(BASE_DIR, DATA_DIR, "media")

GIF_DIR = os.path.join(MEDIA_DIR, 'gif')
IMAGE_DIR = os.path.join(MEDIA_DIR, 'img')
VIDEO_DIR = os.path.join(MEDIA_DIR, 'video')
VOICE_DIR = os.path.join(MEDIA_DIR, 'voice')

EDITS_DIR = os.path.join(IMAGE_DIR, 'edits')
