import os


class Config:
    connection_type = None
    port = 12345
    upload_folder = 'files'
    addr = os.environ.get('MY_ADDR')
