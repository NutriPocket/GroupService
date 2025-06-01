import os
from os import getenv
import dotenv


def pytest_configure(config):
    """
    Runs before test collection starts.
    This is a good place for setup that should happen before any tests run.
    """
    env_path: str = getenv("ENV_PATH", "../.env.test")
    env_path = os.path.abspath(env_path)

    print(f"Loading environment variables from {env_path}")
    dotenv.load_dotenv(dotenv_path=env_path, override=True, verbose=True)
    print("Environment variables loaded successfully.")

    # Additional setup code here
    print("Running before all tests setup...")
