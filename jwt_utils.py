"""
JWT Utility functions
"""
from pathlib import Path
import logging
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver
from jwt import get_unverified_header, decode, exceptions as jwt_exceptions

def extract_jwt_token(request):
    """
    Extract JWT token from the provided request object.
    """
    return request.args.get('token')

def decode_jwt_token(jwt_token, KEYS):
    """
    Decode the given JWT token using the provided set of public keys.
    """
    decoded_header = get_unverified_header(jwt_token)
    app_id = decoded_header.get('appId')

    logging.debug(f"Attempting to decode JWT for appId: {app_id}")
    logging.debug(f"Available keys: {KEYS.keys()}")

    if app_id not in KEYS:
        return None, {'error': 'Invalid appId or app not supported.'}

    try:
        decoded_token = decode(jwt_token, KEYS[app_id], algorithms=['RS256'])
        if 'redirect_url' not in decoded_token:
            return None, {'error': 'Token does not contain a redirect URL'}
        return decoded_token, None
    except jwt_exceptions.ExpiredSignatureError:
        return None, {'error': 'Token has expired'}
    except jwt_exceptions.InvalidTokenError as error:
        return None, {'error': f'Invalid token. Reason: {str(error)}'}

def get_jwt_redirect_url(session):
    """
    Retrieve the JWT redirect URL from the provided session.
    """
    return session.get('redirect_url')

def load_keys_from_directory(directory_path: Path) -> dict:
    """
    Dynamically load keys based on files in a directory.
    Assumes files are named as 'testN_public_key.pem' where N is app ID.
    """
    keys = {}
    for key_file in directory_path.iterdir():
        if key_file.name.endswith("_public_key.pem"):
            try:
                app_id = key_file.stem.split("_")[0]
                keys[app_id] = key_file.read_bytes()
                logging.info(f"Loaded key for appId: {app_id}")
            except Exception as error:
                logging.error(f"Failed to load key {key_file.name}: {str(error)}")

    return keys

class KeyDirectoryHandler(FileSystemEventHandler):
    """
    Handle filesystem events, specifically for key directory modifications.
    """
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith("_public_key.pem"):
            print("Detected key file change!")
            self.callback()


    def on_created(self, event):
        print(f"File {event.src_path} has been created")
        self.callback()

    def on_any_event(self, event):
        print(f"Detected event: {event}")
        self.callback()

def watch_keys_directory(directory_path: Path, callback):
    """
    Watch the given directory for changes using a polling mechanism.
    """
    observer = PollingObserver(timeout=5)  # Check every 5 seconds
    handler = KeyDirectoryHandler(callback)
    observer.schedule(handler, directory_path, recursive=False)
    observer.start()
    return observer
