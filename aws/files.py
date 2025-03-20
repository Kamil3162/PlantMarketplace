import os, fnmatch
import shutil
from pathlib import Path
import re as regex

from fastapi import File, UploadFile

PATH_ROOT = Path(__file__).parent.parent / "images"
path_existance = os.path.exists(PATH_ROOT)
path_files = os.listdir(PATH_ROOT)


class FilesOperations:
    EXTENSIONS = ["jpg", "jpeg", "png"]

    def __init__(self, path: str = None):
        self.path = path

    def generate_file_name(self, file_name, post_id, extension) -> str:
        """
            Generate a file name

            Arguments:
                file_name {str} -- file name
                post_id {str} -- post id
                extension {str} -- file extension

            Returns:
                New generated file name
        """
        print(file_name, post_id, extension)
        file_name_v1 = ".".join([f"{file_name}-p{post_id}", extension])
        return file_name_v1

    def save_file_and_update_record(self, file: UploadFile, post_id: str):
        """
        Saves a file to the uploads directory and updates the database record.

        Args:
            file: The uploaded file
            post_id: The ID of the post to associate with this file

        Returns:
            The filename that was saved
        """
        try:
            file_name, extension = file.filename.split(".", )
        except ValueError:
            raise ValueError("Invalid file name and extension")

        if not regex.match(r'^\d+$', str(post_id)):
            raise ValueError(f"Invalid post ID format: {post_id}")

        print(extension)

        if extension not in self.EXTENSIONS:
            raise ValueError("Invalid file extension")

        n_file_name = self.generate_file_name(
            file_name=file_name,
            post_id=post_id,
            extension=extension
        )
        file_path = PATH_ROOT / n_file_name

        with open(file_path, "wb") as file_object:
            shutil.copyfileobj(file.file, file_object)

        return n_file_name

    def get_file_by_id(self, post_id: str):
        matching_files = []
        for extension in self.EXTENSIONS:
            file = fnmatch.filter(os.listdir(PATH_ROOT),
                                  f"*-p{post_id}.{extension}")
            if file:
                matching_files.append(file[0])

        if not matching_files:
            raise FileNotFoundError(f"No files found for post {post_id}")

        file_path = PATH_ROOT / matching_files[0]
        return file_path, matching_files[0]

    def change_file(self, post_id: str, uploaded_file: UploadFile):
        """
            Changes an existing file with proper extension handling.
            First removes the old file, then saves the new one.
        """
        # Get the existing file information
        file_path, file = self.get_file_by_id(post_id)
        print(f"Found existing file: {file_path}")

        # Extract the extension from the uploaded file
        try:
            file_name, extension = uploaded_file.filename.rsplit(".", 1)
        except ValueError:
            raise ValueError(
                "Invalid filename format - must include extension")

        # Validate the extension
        if extension.lower() not in self.EXTENSIONS:
            raise ValueError(
                f"Invalid extension. Allowed: {', '.join(self.EXTENSIONS)}")

        # Remove the old file
        os.remove(file_path)

        # Generate the new filename with the correct extension
        generate_file_path = self.generate_file_name(
            file_name=file_name,
            post_id=post_id,
            extension=extension
            # Now passing a single string instead of a list
        )

        file_path = PATH_ROOT / generate_file_path
        # Save the new file
        with open(file_path, "wb") as file_object:
            shutil.copyfileobj(uploaded_file.file, file_object)

        return generate_file_path

file_service = FilesOperations(PATH_ROOT)
