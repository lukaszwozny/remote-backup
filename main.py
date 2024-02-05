import os
from dotenv import load_dotenv
from managers.mega import MegaManager
from datetime import datetime

load_dotenv()


def parse_bool(name, default=""):
    env_var = os.getenv(name, default)
    return env_var.lower() in ["true", "1", "t"]


def main():
    mega_enable = parse_bool("MEGA_ENABLE")

    os.chdir("/app")

    # test_postgres_cmd()
    if mega_enable and True:
        mega_m = MegaManager(
            username=os.getenv("MEGA_USERNAME"),
            password=os.getenv("MEGA_PASSWORD"),
            media_weight=330,
        )

        for i in range(1):
            media_file = os.listdir("test_data")[0]
            print(f"mediafile: {media_file}")

            # Upload
            mega_m.upload_database()
            # mega_m.upload_media()

            # Rename
            split = media_file.split(".")[0].split("-")
            split_name = split[0]
            split_nr = int(split[1])

            split_nr += 1
            os.rename(
                os.path.join("test_data", media_file),
                os.path.join("test_data", f"{split_name}-{split_nr}.iso"),
            )


if __name__ == "__main__":
    main()
