import os
import json
from dotenv import load_dotenv
from managers.mega import MegaManager
from datetime import datetime

load_dotenv()


def parse_bool(name, default=""):
    env_var = os.getenv(name, default)
    return env_var.lower() in ["true", "1", "t"]


def main():
    mega_enable = parse_bool("MEGA_ENABLE")

    if os.path.exists("/app"):
        os.chdir("/app")

    if mega_enable and True:
        mega_m = MegaManager(
            username=os.getenv("MEGA_USERNAME"),
            password=os.getenv("MEGA_PASSWORD"),
            media_weight=330,
        )

        # Upload
        mega_m.upload_database()
        mega_m.upload_media()


if __name__ == "__main__":
    main()
