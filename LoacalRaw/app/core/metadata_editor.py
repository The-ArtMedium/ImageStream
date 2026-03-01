from PIL import Image
from PIL.ExifTags import TAGS
import piexif
import os


class MetadataEditor:
    """
    Read and write image metadata (EXIF).
    Supports JPEG files. PNG support is read-only.

    Readable fields: camera, lens, ISO, shutter, aperture, date, GPS
    Writable fields: artist, copyright, description, keywords
    """

    # EXIF tag IDs for writing
    TAG_ARTIST      = 315
    TAG_COPYRIGHT   = 33432
    TAG_DESCRIPTION = 270
    TAG_SOFTWARE    = 305

    def read(self, file_path: str) -> dict:
        """
        Returns a dict of human-readable EXIF metadata.
        Returns empty dict if no EXIF found.
        """
        try:
            img = Image.open(file_path)
            exif_data = img._getexif()

            if not exif_data:
                return {}

            readable = {}
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, str(tag_id))

                # Skip binary/thumbnail data
                if isinstance(value, bytes) and len(value) > 64:
                    continue

                readable[tag_name] = value

            return readable

        except Exception:
            return {}

    def write(
        self,
        file_path: str,
        artist: str = "",
        copyright: str = "",
        description: str = "",
        software: str = "LocalRAW"
    ) -> bool:
        """
        Writes metadata to a JPEG file.
        Preserves existing EXIF data and merges new values.
        Returns True on success.
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext not in [".jpg", ".jpeg"]:
            raise ValueError("Metadata writing only supported for JPEG files.")

        try:
            # Load existing EXIF or start fresh
            try:
                exif_dict = piexif.load(file_path)
            except Exception:
                exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}

            def encode(val):
                return val.encode("utf-8") if val else b""

            if artist:
                exif_dict["0th"][self.TAG_ARTIST] = encode(artist)
            if copyright:
                exif_dict["0th"][self.TAG_COPYRIGHT] = encode(copyright)
            if description:
                exif_dict["0th"][self.TAG_DESCRIPTION] = encode(description)
            if software:
                exif_dict["0th"][self.TAG_SOFTWARE] = encode(software)

            exif_bytes = piexif.dump(exif_dict)

            img = Image.open(file_path)
            img.save(file_path, "jpeg", exif=exif_bytes, quality=95)

            return True

        except Exception as e:
            raise RuntimeError(f"Failed to write metadata: {e}")

    def summary(self, file_path: str) -> str:
        """
        Returns a formatted string summary of key EXIF fields.
        Useful for display in UI.
        """
        data = self.read(file_path)
        if not data:
            return "No EXIF data found."

        fields = [
            ("Camera",   data.get("Make", "") + " " + data.get("Model", "")),
            ("Date",     data.get("DateTimeOriginal", data.get("DateTime", ""))),
            ("ISO",      data.get("ISOSpeedRatings", "")),
            ("Shutter",  str(data.get("ExposureTime", ""))),
            ("Aperture", str(data.get("FNumber", ""))),
            ("Lens",     data.get("LensModel", "")),
            ("Artist",   data.get("Artist", "")),
            ("Copyright",data.get("Copyright", "")),
        ]

        lines = []
        for label, value in fields:
            if value and str(value).strip():
                lines.append(f"{label}: {value}")

        return "\n".join(lines) if lines else "No readable EXIF fields found."
