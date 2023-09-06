def validate_environment_settings(CLIENT_PUBLIC_KEYS_DIRECTORY, SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY, REDIRECT_URL_TO_LOUIS_FRONTEND):
    """
    Validate the environment settings required for the application.
    
    Args:
    - CLIENT_PUBLIC_KEYS_DIRECTORY (Path): The directory containing the client public keys.
    - SERVER_PRIVATE_KEY (Path): The path to the server's private key.
    - SERVER_PUBLIC_KEY (Path): The path to the server's public key.
    - REDIRECT_URL_TO_LOUIS_FRONTEND (str): The redirect URL to the Louis frontend.

    Returns:
    - True if all validations pass.

    Raises:
    - ValueError: If any of the provided settings are invalid.
    """

    # Check the client public keys directory
    if not CLIENT_PUBLIC_KEYS_DIRECTORY.exists():
        raise ValueError(f"The directory {CLIENT_PUBLIC_KEYS_DIRECTORY} for public keys does not exist. Please specify a valid directory.")

    # Check the server private key
    if not SERVER_PRIVATE_KEY.exists() or SERVER_PRIVATE_KEY.is_dir():
        raise ValueError(f"The specified server private key file {SERVER_PRIVATE_KEY} does not exist or is a directory. Please provide a valid path.")

    # Check the server public key
    if not SERVER_PUBLIC_KEY.exists() or SERVER_PUBLIC_KEY.is_dir():
        raise ValueError(f"The specified server public key file {SERVER_PUBLIC_KEY} does not exist or is a directory. Please provide a valid path.")

    # Check the redirect URL to Louis Frontend
    if not REDIRECT_URL_TO_LOUIS_FRONTEND:
        raise ValueError("The redirect URL to Louis Frontend is not specified. Please provide a valid URL.")

    return True
