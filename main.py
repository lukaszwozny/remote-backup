import os
import json
from dotenv import load_dotenv
from managers.mega import MegaManager
from datetime import datetime

load_dotenv()


def parse_bool(name, default=""):
    env_var = os.getenv(name, default)
    return env_var.lower() in ["true", "1", "t"]


def update_cronjobs():
    cron_schedule = os.getenv("CRON_SCHEDULE", "0 3 * * *")

    cronjobs_path = "/etc/crontabs/root"
    with open(cronjobs_path) as f:
        content = f.read()
        split = content.split(" ")
        current_cron_schedule = " ".join(split[:5])

        if cron_schedule != current_cron_schedule:
            new_cron_schedule = cron_schedule + " " + " ".join(split[5:])
            with open(cronjobs_path, "w") as fw:
                fw.write(new_cron_schedule)


def main():
    update_cronjobs()

    if os.path.exists("/app"):
        os.chdir("/app")

    mega_enable = parse_bool("MEGA_ENABLE")
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
