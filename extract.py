import tarfile


class TarBallExtractor():
    """
    Extracts tarball files from Samknows using the tarfile module.
    """

    def __init__(self, input_dir, file_name, output_dir):
        self.input_dir = input_dir
        self.file_name = file_name
        self.output_dir = output_dir
        self.tar_file = self.open_file()

    def open_file(self):
        """
        Open this tarball.
        """

        return tarfile.open(self.input_dir + "/" + self.file_name, "r:gz")

    def get_file_names(self):
        """
        Retrieve the filenames from this tarball.
        """

        return self.tar_file.getnames()

    def close(self):
        """
        Close this tarball.
        """

        self.tar_file.close()