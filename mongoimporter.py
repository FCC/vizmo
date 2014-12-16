import json
import tarfile
from multiprocessing import Process, Manager
import pymongo
import datetime

from log import config_decorator


@config_decorator
def _import_test(import_queue, tar_file, _config=None, db=None, log=None):
    """
    Worker process which pulls file names from the import_queue and imports them to Mongo using json.loads.
    """

    tar = tarfile.open(tar_file, 'r:gz')
    while True:
        filename = import_queue.get()
        if filename is None:
            import_queue.task_done()
            tar.close()
            return
        else:
            try:
                data = tar.extractfile(filename).read().decode('utf-8')
                data_json = json.loads(data)
                db.test.buffer.insert(data_json)
            except ValueError:
                log.warning("** " + str(datetime.datetime.now()) + " ** Json parsing error for file " + str(filename))
            import_queue.task_done()


def _import_test_wrapper(import_queue, tar_file):
    """
    Windows compatible entry point for the import test process.
    """

    _import_test(import_queue, tar_file)


class MongoImporter():
    """
    Class that handles importing tests from SamKnows.

    Instances of the class are created with various fields which are used to build the necessary db queries to
    insert tests into the appropriate collections.
    """

    def __init__(self, date, tar_file, file_names):
        self.date = date
        self.tar_file = tar_file
        self.file_names = file_names

    @config_decorator
    def import_tests(self, _config=None, db=None, log=None):
        """
        Import the tests pointed to by this instance of MongoImporter.

        Walks the file names in file_names
            - If it is a directory, ignore the name
            - If it is a json file, insert it into the import queue
        """

        import_processes = []
        import_queue = Manager().JoinableQueue()

        # test_dir_suffix = "{:%Y%m%d}".format(self.date)
        # os.chdir(self.test_dir + "/" + test_dir_suffix)

        for i in range(8):
            process = Process(target=_import_test_wrapper, args=(import_queue, self.tar_file))
            import_processes.append(process)
            process.start()

        for name in self.file_names:
            if '.json' in name:
                import_queue.put(name)

        # Place poison pills at the end of the import_queue to end the import processes.
        for process in import_processes:
            import_queue.put(None)

        for process in import_processes:
            process.join()

        # Mark the buffer status flag as False so that if the program is interrupted during the transfer it knows to
        # finish clearing the buffer before importing more tests.
        db.meta.update({'type': 'flags'}, {'$set': {'buffer_transfer_complete': False}})
        uploaded_dates = db.meta.find_one({'type': 'dates'})['uploaded_dates']
        uploaded_dates.append("{:%Y%m%d}".format(self.date))
        db.meta.update({'type': 'dates'}, {'$set': {'uploaded_dates': uploaded_dates}})
        db.meta.update({'type': 'dates'}, {'$set': {'latest_imported_date': "{:%Y%m%d}".format(self.date)}})
        # When finished remove the tests from test.buffer and place them in test.raw.buffer
        for test in db.test.buffer.find():
            try:
                highest_test_id = db.meta.find_one({'type': 'highest_test_id'})['value']
                test.update({'test_id': highest_test_id})
                highest_test_id += 1

                db.test.buffer.remove({'_id': test['_id']})
                db.test.raw.buffer.insert(test)

                db.meta.update({'type': 'highest_test_id'}, {'$set': {'value': highest_test_id}})
            except pymongo.errors.DuplicateKeyError:
                pass

        db.meta.update({'type': 'flags'}, {'$set': {'buffer_transfer_complete': True}})