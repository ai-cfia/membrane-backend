def validate_environment_settings(
    CLIENT_PUBLIC_KEYS_DIRECTORY, SERVER_PRIVATE_KEY, SERVER_PUBLIC_KEY, FRONTEND_URL
):
    """
    Validate the environment settings required for the application.


    Args:
    - CLIENT_PUBLIC_KEYS_DIRECTORY (Path): The directory containing the client public
    keys.
    - SERVER_PRIVATE_KEY (Path): The path to the server's private key.
    - SERVER_PUBLIC_KEY (Path): The path to the server's public key.
    - FRONTEND_URL (str): The redirect URL to the membrane frontend.

    Returns:
    - True if all validations pass.

    Raises:
    - ValueError: If any of the provided settings are invalid.
    """

    # Check the client public keys directory
    if not CLIENT_PUBLIC_KEYS_DIRECTORY.exists():
        raise ValueError(
            f"The directory {CLIENT_PUBLIC_KEYS_DIRECTORY} for public keys does not "
            "exist. Please specify a valid directory."
        )

    # Check the server private key
    if not SERVER_PRIVATE_KEY.exists() :
        raise ValueError(f"The specified server private key file {SERVER_PRIVATE_KEY} does not exist.")
    elif SERVER_PRIVATE_KEY.is_dir():
        raise ValueError(f"The specified server private key file {SERVER_PRIVATE_KEY} is a directory.")

    # Check the server public key

    if not SERVER_PUBLIC_KEY.exists() :
        raise ValueError(f"The specified server public key file {SERVER_PUBLIC_KEY} does not exist.")
    elif SERVER_PUBLIC_KEY.is_dir():
        raise ValueError(f"The specified server public key file {SERVER_PUBLIC_KEY} is a directory.")

    # Check the redirect URL to Membrane Frontend
    if not FRONTEND_URL:
        raise ValueError(
            "The redirect URL to Membrane Frontend is not specified. Please provide a "
            "valid URL."
        )

    return True
