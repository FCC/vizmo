import subprocess
import requests


CHUNKSIZE = 256


class CurlDownloader():
    """
    Samknows downloader implemented using curl.
    """

    def __init__(self, base_url, username, password, output_dir, date):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.date = date

    def download_tests(self):
        """
        Use the settings supplied on object creation to download a tarball from the SamKnows server.
        """

        filename = "{:%Y%m%d}".format(self.date)
        filename += "-fcc-android.tar.gz"

        download_api = "/usr/bin/curl -X POST " + self.base_url + filename + " --user "
        download_api = download_api + self.username + ":" + self.password + " -o " + self.output_dir + "/" + filename

        response = subprocess.check_output(download_api, shell=True)

        return response


class RequestsDownloader():
    """
    Samknows downloader implemented using the requests module.
    """

    def __init__(self, base_url, username, password, output_dir, date):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.output_dir = output_dir
        self.date = date

    def download_tests(self):
        """
        Use the settings supplied on object creation to download a tarball from the SamKnows server.
        """

        filename = "{:%Y%m%d}".format(self.date)
        filename += "-fcc-android.tar.gz"

        url = self.base_url + filename
        request = requests.get(url, stream=True, auth=(self.username, self.password))

        filename = self.output_dir + '/' + filename

        with open(filename, 'wb') as file:
            for chunk in request.iter_content(CHUNKSIZE):
                file.write(chunk)