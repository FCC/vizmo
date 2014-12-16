#!./env/bin/python -u
"""
   ___  ___   ___         _
  / __\/ __\ / __\ /\   /(_)____ /\/\   ___
 / _\ / /   / /    \ \ / / |_  //    \ / _ \
/ /  / /___/ /___   \ V /| |/ // /\/\ \ (_) |
\/   \____/\____/    \_/ |_/___\/    \/\___/

"""


if __name__ in ('__main__',):
    import log
    log.init_new_log()


import sys
import time
import os
import subprocess
import datetime
from multiprocessing import Manager, Process

import database
import vizmo_map
from log import config_decorator
import update_meta_public

@config_decorator
def _idle(_config=None, db=None, log=None):
    """
    Idle for the configured amount of time.
    """

    time.sleep(int(_config['vizmo_tilemill']['sleep_time']))


def _sleep_hour():
    """
    Idle for one hour.
    """

    time.sleep(3600)


def _sleep_morning():
    """
    Idle until 3am.
    """

    today = datetime.datetime.today()
    if today.hour > 3:
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 0, 0, 0)
        sleep_time = (tomorrow - today).seconds
    else:
        tomorrow = datetime.date.today()
        tomorrow = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 3, 0, 0, 0)
        sleep_time = (tomorrow - today).seconds

    time.sleep(sleep_time)


def _render_maps_process_wrapper(map_queue):
    """
    Windows compatible entry point for the render map process.
    """

    _render_maps_process(map_queue)


@config_decorator
def _render_maps_process(map_queue, _config=None, db=None, log=None):
    """
    Worker process which renders each map on the map_queue by dispatching a Tilemill instance.
    """

    while True:
        project = map_queue.get()

        if project is None:
            map_queue.task_done()
            break
        else:
            try:
                project_file = _config['vizmo_tilemill']['map_dir'] + project + '.mbtiles'
                os.remove(project_file)
            except IOError:
                pass

            project_file = _config['vizmo_tilemill']['map_dir'] + project + '.mbtiles'
            tilemill_api = './index.js' + ' export ' + project + ' ' + project_file
            tilemill_api += ' --format=mbtiles --bbox=' + _config['vizmo_tilemill']['bbox'] + ' --minzoom='
            tilemill_api += _config['vizmo_tilemill']['minzoom'] + ' --maxzoom='
            tilemill_api += _config['vizmo_tilemill']['maxzoom'] + ' --files=' + _config['vizmo_tilemill']['files']

            print(tilemill_api)
            log.info("** " + str(datetime.datetime.now()) + " ** Rendering " + str(project))

            subprocess.check_output(tilemill_api, shell=True)
            map_queue.task_done()


def _upload_maps_process_wrapper(map_queue):
    """
    Windows compatible entry point for the upload map process.
    """

    _upload_maps_process(map_queue)


@config_decorator
def _upload_maps_process(map_queue, _config=None, db=None, log=None):
    """
    Worker process which uploads each completed map to Mapbox from the map_queue.
    """

    while True:
        project = map_queue.get()

        if project is None:
            map_queue.task_done()
            break
        else:
            project_file = _config['vizmo_tilemill']['map_dir'] + project + '.mbtiles'
            tilemill_api = './index.js' + ' export ' + project + ' ' + project_file
            tilemill_api += ' --format=upload --bbox=' + _config['vizmo_tilemill']['bbox'] + ' --minzoom='
            tilemill_api += _config['vizmo_tilemill']['minzoom'] + ' --maxzoom=' + _config['vizmo_tilemill']['maxzoom']
            tilemill_api += ' --files=' + _config['vizmo_tilemill']['files']
            tilemill_api += ' --syncAccount=\"' + _config['vizmo_tilemill']['sync_account'] + '\" --syncAccessToken='
            tilemill_api += _config['vizmo_tilemill']['sync_access_token']

            print(tilemill_api)
            log.info("** " + str(datetime.datetime.now()) + " ** Uploading " + str(project))

            subprocess.check_output(tilemill_api, shell=True)
            map_queue.task_done()


@config_decorator
def _update_maps(_config=None, db=None, log=None):
    """
    Render and upload the new maps to Mapbox.
    """

    map_processes = []
    map_queue = Manager().JoinableQueue()

    log.info("** " + str(datetime.datetime.today()) + " ** Creating geojson layers!")
    vizmo_map.main([])

    log.info("** " + str(datetime.datetime.today()) + " ** Rendering new maps!")
    os.chdir(_config['vizmo_tilemill']['tilemill_dir'])

    for i in range(int(_config['vizmo_tilemill']['map_process_count'])):
        process = Process(target=_render_maps_process_wrapper, args=(map_queue,))
        map_processes.append(process)
        process.start()

    for project in _config['tilemill_projects']:
        map_queue.put(project)

    # Place poison pills at the end of the map_queue to stop the render processes.
    for process in map_processes:
        map_queue.put(None)

    for process in map_processes:
        process.join()

    _sleep_morning()

    log.info("** " + str(datetime.datetime.today()) + " ** Uploading maps to mapbox!")
    map_processes = []

    for i in range(1):
        process = Process(target=_upload_maps_process_wrapper, args=(map_queue,))
        map_processes.append(process)
        process.start()

    for project in _config['tilemill_projects']:
        map_queue.put(project)

    # Place poison pills at the end of the map_queue to stop the upload processes.
    for process in map_processes:
        map_queue.put(None)

    for process in map_processes:
        process.join()

    _sleep_hour()


@config_decorator
def _update_data(_config=None, db=None, log=None):
    """
    Switch the public data on Mongo once the new maps have been rendered, uploaded, and cached in Mapbox.
    """

    db_public = database.Connection('public')

    new_meta = db.meta.find_one({'type': 'dates'})
    db_public.meta.remove({'type': 'dates'})
    db_public.meta.insert(new_meta)

    # Replace the old aggregations collection with the new one.
    db_public[_config['vizmo_tilemill']['aggregations_mongo_to']].drop()
    db_public[_config['vizmo_tilemill']['aggregations_mongo_from']].rename(
        _config['vizmo_tilemill']['aggregations_mongo_to'])

    # Replace the old bin meta collection with the new one.
    db_public[_config['vizmo_tilemill']['bins_mongo_to']].drop()
    db_public[_config['vizmo_tilemill']['bins_mongo_from']].rename(_config['vizmo_tilemill']['bins_mongo_to'])

    # Update the latest_aggregated_date now that the process is complete.
    latest_binned_date = db.meta.find_one({'type': 'dates'})['latest_binned_date']
    db_public.meta.update({'type': 'dates'}, {'$set': {'latest_aggregated_date': latest_binned_date}}, upsert=False,
                          multi=True)
    db.meta.update({'type': 'dates'}, {'$set': {'latest_aggregated_date': latest_binned_date}}, upsert=False,
                   multi=True)

    # Toggle the map_complete flag to reactivate the aggregation process.
    db.meta.update({'type': 'flags'}, {'$set': {'map_complete': True}}, upsert=False, multi=True)

    #update meta.public
    update_meta_public.create_meta_public()

@config_decorator
def main(argv, _config=None, db=None, log=None):
    """
    Render and update the maps when the map_complete flag is False.
    """

    while True:
        map_complete = db.meta.find_one({'type': 'flags'})['map_complete']

        if not map_complete:
            log.info("** " + str(datetime.datetime.today()) + " ** Updating the maps!")
            _update_maps()

            log.info("** " + str(datetime.datetime.today()) + " ** Updating the database!")
            _update_data()

            log.info("** " + str(datetime.datetime.today()) + " ** Finished!")

        _idle()


if __name__ == "__main__":
    main(sys.argv[1:])
