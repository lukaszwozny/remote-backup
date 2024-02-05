import os
import json
from dotenv import load_dotenv
from managers.mega import MegaManager
from datetime import datetime

load_dotenv()


def parse_bool(name, default=""):
    env_var = os.getenv(name, default)
    return env_var.lower() in ["true", "1", "t"]


def test_media():
    media_folder_path = "volumes/media"

    current_modified_time = os.stat(media_folder_path).st_mtime

    # Load settings
    settings_path = "backups/settings.json"

    settings = {
        "mediaModifiedTime": current_modified_time,
    }
    if not os.path.exists(settings_path):
        with open(settings_path, "w+") as f:
            json.dump(settings, f, indent=2)
    else:
        with open(settings_path) as f:
            settings = json.load(f)

    prev_modified_time = settings["mediaModifiedTime"]

    if current_modified_time == prev_modified_time:
        print("NO CHANGEWS")
        return

    print("NEW MODIFICATION")
    # Create media archive
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H_%M_%S")
    domain = os.getenv("DOMAIN", "")
    media_output_path = f"backups/{domain}_{current_time}.tar.gz"

    cmd = f"tar -zcf {media_output_path} -C {media_folder_path} ."
    os.system(cmd)

    settings = {
        "mediaModifiedTime": current_modified_time,
    }
    with open(settings_path, "w+") as f:
        json.dump(settings, f, indent=2)


def main():
    mega_enable = parse_bool("MEGA_ENABLE")

    if os.path.exists("/app"):
        os.chdir("/app")

    test_media()

    return
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
