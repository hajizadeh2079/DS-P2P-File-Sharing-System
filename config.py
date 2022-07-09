import os


class Config:
    connection_type = None
    port = 12345
    upload_folder = 'files'
    addr = os.environ.get('MY_ADDR')
    channel = 1
    similarity_th = 70
    chunk_size = 1024
    health_delay = 60
