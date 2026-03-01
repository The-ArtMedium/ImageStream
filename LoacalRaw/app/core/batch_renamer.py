import os
from datetime import datetime


class BatchRenamer:
    """
    Renames a list of image files using a pattern.

    Pattern tokens:
        {name}      — original filename without extension
        {n}         — sequence number (001, 002...)
        {date}      — today's date (YYYYMMDD)
        {ext}       — original extension
        {prefix}    — custom prefix provided by user

    Example pattern: "wedding_{date}_{n}"
    Result:          "wedding_20260228_001.jpg"
    """

    def preview(self, files: list, pattern: str, prefix: str = "") -> list:
        """
        Returns list of (old_path, new_name) tuples — no changes made to disk.
        Use this to show the user what will happen before confirming.
        """
        results = []
        today = datetime.now().strftime("%Y%m%d")

        for i, file_path in enumerate(files, start=1):
            original_name = os.path.splitext(os.path.basename(file_path))[0]
            ext = os.path.splitext(file_path)[1]

            new_name = pattern.format(
                name=original_name,
                n=str(i).zfill(3),
                date=today,
                ext=ext.lstrip("."),
                prefix=prefix
            ) + ext

            results.append((file_path, new_name))

        return results

    def execute(self, files: list, pattern: str, prefix: str = "") -> list:
        """
        Renames files on disk.
        Returns list of (old_path, new_path, success, error_message).
        """
        preview = self.preview(files, pattern, prefix)
        results = []

        for old_path, new_name in preview:
            folder = os.path.dirname(old_path)
            new_path = os.path.join(folder, new_name)

            try:
                if os.path.exists(new_path) and new_path != old_path:
                    raise FileExistsError(f"{new_name} already exists")

                os.rename(old_path, new_path)
                results.append((old_path, new_path, True, ""))

            except Exception as e:
                results.append((old_path, new_path, False, str(e)))

        return results
