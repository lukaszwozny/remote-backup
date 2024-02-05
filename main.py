import os
from dotenv import load_dotenv
from managers.mega import MegaManager
from datetime import datetime

load_dotenv()


def parse_bool(name, default=""):
    env_var = os.getenv(name, default)
    return env_var.lower() in ["true", "1", "t"]


def test_postgres_cmd():
    print("# Test prostgres cmd")
    #     cmd = """ssh postgres@db "pg_dump -U postgres -h localhost -C --column-inserts" \
    #  > backup_file_on_your_local_machine.sql"""
    # cmd = """ssh postgres@db "pg_dumpall -h localhost -U postgres -W -d postgrees" > /logs/dump.sql"""
    # os.system(cmd)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d_%H_%M_%S")

    domain = os.getenv("DOMAIN", "")
    backup_file = f"{domain}_{current_time}.sql.gz"

    backup_path = os.path.join("/backups", backup_file)
    print(backup_path)
    cmd = f"pg_dump -h db -U postgres postgres | gzip > {backup_path}"
    result = os.system(cmd)

    file_size = os.path.getsize(backup_path)
    print(f"f size: {file_size}")
    print(result)


def main():
    mega_enable = parse_bool("MEGA_ENABLE")

    os.chdir("/app")

    test_postgres_cmd()
    if mega_enable and False:
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
            mega_m.upload_media()

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
