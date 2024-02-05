import mega
import json
import os
from datetime import datetime
from time import sleep
import enum

EMAIL = ""
PASS = ""
MODIFIED_FILE = "modified.json"


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
        storage = self.mega.get_storage_space(kilo=True)
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
            return None

        folder_size = 0
        for k, v in self.remote_files().items():
            if v["p"] != folder_id:
                continue

            files[k] = v

        files = {k: v for k, v in sorted(files.items(), key=lambda x: x[1]["ts"])}

        return files

    def get_remote_folder_size(self, folder: RemoteFolder) -> float:
        folder_id = None

        files = self.get_remote_folder_files(folder)
        if files is None:
            return 0

        folder_size = 0
        for k, v in files.items():
            if v["p"] != folder_id:
                continue

            folder_size += v["s"]

        return folder_size / 1000

    def remote_folder_make_space(self, folder: RemoteFolder, space_needed):
        freed = 0
        files = self.get_remote_folder_files(folder)
        if files is None:
            return 0

        print(type(files.items()))

        print("KEY")
        for k, v in files.items():
            # print(f"  {k}")
            print(f"  {v['ts']}")
            # print(json.dumps(v, indent=2))

    def upload_database(self):
        print("# Upload DATABASE")
        # media_path = self.settings["MEDIA_PATH"]
        # media_path = "test_data/clonezilla-1.iso"
        local_file = os.listdir("test_data")[0]
        split = local_file.split(".")[0].split("-")
        split_name = split[0]
        split_nr = int(split[1])

        final_path = os.path.join("test_data", local_file)
        file_size = os.path.getsize(final_path) / 1000
        print(f"size: {file_size}")

        rf = RemoteFolder.DB
        rf_max_size = self.get_remote_folder_max_size(rf)
        print(f"rf max size: {rf_max_size}")

        rf_size = self.get_remote_folder_size(rf)
        print(f"rf size: {rf_size}")

        rf_free_space = rf_max_size - rf_size
        rf_free_space = 0
        print(f"rf free size: {rf_free_space}")

        if rf_free_space < file_size:
            print("NOT ENOUGH SPACE")
            self.remote_folder_make_space(rf, space_needed=file_size - rf_free_space)
        else:
            print("JEST SPACE")
        return

        self.upload_file(
            filename=final_path,
            remote_folder="DB",
        )

        # was_mod = was_modified(media_path)
        # if not was_mod:
        #     print(f'No changes found in "{media_path}". Skipped!')
        #     return

        # folder_name = "MEDIA"
        # dir = os.path.join("temp", folder_name)

        # output_filename = f"{media_path}_.tar.gz"

    def upload_media(self):
        print("# Upload MEDIA")
        # media_path = self.settings["MEDIA_PATH"]
        # media_path = "test_data/clonezilla-1.iso"
        local_file = os.listdir("test_data")[0]
        split = local_file.split(".")[0].split("-")
        split_name = split[0]
        split_nr = int(split[1])

        final_path = os.path.join("test_data", local_file)

        self.upload_file(
            filename=final_path,
            remote_folder="MEDIA",
        )

        # was_mod = was_modified(media_path)
        # if not was_mod:
        #     print(f'No changes found in "{media_path}". Skipped!')
        #     return

        # folder_name = "MEDIA"
        # dir = os.path.join("temp", folder_name)

        # output_filename = f"{media_path}_.tar.gz"

    def upload_file(self, filename, remote_folder):
        print(f"Uploading {filename}... ", end="")
        if remote_folder and remote_folder != "":
            folder = self.mega.find(remote_folder, exclude_deleted=True)
            if folder is None:
                folder = self.mega.create_folder(remote_folder)
                folder_id = folder[remote_folder]
            else:
                folder_id = folder[0]

            self.mega.upload(filename, folder_id)
        else:
            self.mega.upload(filename)
        print("Done!")
