import mega
import json
import os
from datetime import datetime
from time import sleep
import enum
import locale

locale.setlocale(locale.LC_ALL, "pl_PL.utf8")

# formatted_number = locale.format("%d", n, grouping=True)

EMAIL = ""
PASS = ""
MODIFIED_FILE = "modified.json"


def locale_print(name, number, kilo=True, tabs=0):
    prefix = "B"
    if kilo:
        number /= 1000
        prefix = "KB"

    tabs_s = ""
    for t in range(tabs):
        tabs_s += "  "
    name = tabs_s + name

    formatted_number = locale.format("%d", number, grouping=True)
    print(f"{name:20}{formatted_number:>16} {prefix}")


class RemoteFolder(enum.Enum):
    DB = "DB"
    MEDIA = "MEDIA"


class MegaManager:
    def __init__(self, username, password, db_weight=1, media_weight=1):
        if username is None or password is None:
            raise ValueError("Set MEGA_USERNAME and MEGA_PASSWORD env variables")
        self.username = username
        self.password = password

        self.weights = {
            RemoteFolder.DB: db_weight,
            RemoteFolder.MEDIA: media_weight,
        }

        self._remote_files = None

        self.mega = mega.Mega()

        self.logged = self._login()

    def _login(self):
        # Login to MEGA
        print(f"Loging... ", end="")
        try:
            self.mega = self.mega.login(self.username, self.password)
            print("Done!")
            return True
        except mega.errors.RequestError as e:
            print()
            print(e)

    def get_remote_total_size(self):
        storage = self.mega.get_storage_space()
        # self.storage_total = storage["total"]
        # self.storage_used = storage["used"]
        return storage["total"]

    def get_remote_folder_max_size(self, folder: RemoteFolder):
        weights_sum = sum(self.weights.values())
        folder_size_ratio = self.weights[folder] / weights_sum
        return self.get_remote_total_size() * folder_size_ratio

    def update_storage(self):
        # TODO
        print(f"Updating storage... ", end="")
        storage = self.mega.get_storage_space(kilo=True)
        print("Done!")
        self.storage_total = storage["total"]
        self.storage_used = storage["used"]
        self.db_ratio = 0.3
        print(f"total: {self.storage_total}")
        print(f"used: {self.storage_used}")
        print(f"db_ratio: {self.db_ratio}")

        # db_storage = self.TOTAL * self.DB_RATIO
        # self.server_folders[FolderKey.DB][FolderKey.STORAGE] = db_storage
        # self.server_folders[FolderKey.MEDIA][FolderKey.STORAGE] = (
        #     self.TOTAL - db_storage
        # )
        print("Done!")

    def remote_files(self, update=False):
        if self._remote_files is None or update:
            self._remote_files = self.mega.get_files()
        return self._remote_files

    def get_remote_folder_files(self, folder: RemoteFolder):
        files = {}
        for k, v in self.remote_files().items():
            if v["a"]["n"] == folder.value:
                folder_id = k
                break

        if folder_id is None:
            return None, []

        folder_size = 0
        for k, v in self.remote_files().items():
            if v["p"] != folder_id:
                continue

            files[k] = v

        files = {k: v for k, v in sorted(files.items(), key=lambda x: x[1]["ts"])}

        return folder_id, files

    def get_remote_folder_size(self, folder: RemoteFolder) -> float:
        folder_id, files = self.get_remote_folder_files(folder)
        if files is None:
            return 0

        folder_size = 0
        for k, v in files.items():
            if v["p"] != folder_id:
                continue

            folder_size += v["s"]

        return folder_size

    def remote_folder_make_space(self, folder: RemoteFolder, space_needed):
        freed = 0
        _, files = self.get_remote_folder_files(folder)
        if files is None:
            return 0

        print("Removing...")
        for k, v in files.items():
            freed += v["s"]
            self.mega.delete(k)
            locale_print(f"  {v['a']['n']}", v["s"])
            if freed > space_needed:
                break

        # print(f"Freed {locale.format('%d', freed, grouping=True)} KB")
        locale_print("Freed", freed)

    def create_postgres_dump_file(self) -> str:
        print("# Create Postgres dump file.")

        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d_%H_%M_%S")
        domain = os.getenv("DOMAIN", "")
        backup_file = f"{domain}_{current_time}.sql.gz"

        backup_path = os.path.join("/backups", backup_file)

        db_user = os.getenv("POSTGRES_USER", "postgres")
        db_name = os.getenv("POSTGRES_NAME", "postgres")
        cmd = f"pg_dump -h db -U {db_user} {db_name} | gzip > {backup_path}"

        result = os.system(cmd)
        if result != 0:
            print("  pg_dump error!")
            return None

        return backup_path

    def upload_database(self):
        print("# Upload DATABASE")

        # TODO Create file to upload
        # local_file = os.listdir("test_data")[0]
        # split = local_file.split(".")[0].split("-")
        # split_name = split[0]
        # split_nr = int(split[1])
        # final_path = os.path.join("test_data", local_file)

        path = self.create_postgres_dump_file()
        if path is None:
            return
        # End create file to upload

        self.upload_file_making_space(
            file_path=path,
            rf=RemoteFolder.DB,
        )

        os.remove(path)

    def upload_media(self):
        print("# Upload MEDIA")

        # TODO Create file to upload
        media_folder_path = "volumes/media"

        # Load settings
        settings_path = "backups/settings.json"
        settings = {
            "mediaModifiedTime": 0,
        }
        if not os.path.exists(settings_path):
            with open(settings_path, "w+") as f:
                json.dump(settings, f, indent=2)
        else:
            with open(settings_path) as f:
                settings = json.load(f)

        prev_modified_time = settings["mediaModifiedTime"]

        current_modified_time = os.stat(media_folder_path).st_mtime
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

        # Upload media to cloud
        self.upload_file_making_space(
            file_path=media_output_path,
            rf=RemoteFolder.MEDIA,
        )

        # Save mediaModifiedTime
        settings = {
            "mediaModifiedTime": current_modified_time,
        }
        with open(settings_path, "w+") as f:
            json.dump(settings, f, indent=2)

        # Remove archive
        os.remove(media_output_path)

    def upload_file_making_space(self, file_path, rf: RemoteFolder, tabs=1):
        file_size = os.path.getsize(file_path)
        locale_print(f"L file size", file_size, tabs=tabs)

        rf_max_size = self.get_remote_folder_max_size(rf)
        locale_print(f"RF max size", rf_max_size, tabs=tabs)

        rf_size = self.get_remote_folder_size(rf)
        locale_print(f"RF size", rf_size, tabs=tabs)

        rf_free_space = rf_max_size - rf_size
        locale_print(f"RF free space", rf_free_space, tabs=tabs)

        if rf_free_space < file_size:
            self.remote_folder_make_space(rf, space_needed=file_size - rf_free_space)

        self.upload_file(
            filename=file_path,
            rf=rf,
        )

    def upload_file(self, filename, rf: RemoteFolder):
        folder_name = rf.value
        print(f"Uploading {filename} to {rf.value}/... ", end="")
        if rf and folder_name != "":
            folder = self.mega.find(folder_name, exclude_deleted=True)
            if folder is None:
                folder = self.mega.create_folder(folder_name)
                folder_id = folder[folder_name]
            else:
                folder_id = folder[0]

            self.mega.upload(filename, folder_id)
        else:
            self.mega.upload(filename)
        print("Done!")
