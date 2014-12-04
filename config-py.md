Vizmo Config Guide
==================

The config file for this project is located one directory back from the source code in order to keep it separate from the code on Git. By default the name is 'vizmocfg.ini'. The file is divided into sections surrounded by square brackets, which, with a few exceptions, are named for the source code file they configure. 

**Note** - All paths in the config are fully qualified and not relative to the location of the project.

**Also note** - Some settings are used only by the Python script or the TileMill script. Sections specifically for the Python script are labeled green, while sections only for TileMill are red. Sections in red can be ignored when configuring for the Python server and vice versa.

#[lists]
This section is used to specify which sections should be placed into a list by the config parser (part of log.py). Each entry corresponds to the name of a different section. This section should not be modified by anyone other than the dev team.

#[vizmo_import]

```
TEST_DIR		Path to store the incoming tests from SamKnows. 
TEST_URL		URL of the SamKnows server.
TEST_USERNAME	SamKnows account username.
TEST_PASSWORD	SamKnows account password.
FIRST_DATE		First date to import from. This is stored in ordinal format.
```

#[vizmo_aggregate]
List of geometries to bin. For example, adding  hex50k = True to the list will cause the code to look for a collection named `geo.hex50k` with geometries to bin to.

#[vizmo_python]
```
AGGREGATIONS_MONGO_TO		Destination collection name for aggregations during transfer from private to public.
AGGREGATIONS_MONGO_FROM		Source collection name for aggregations during transfer from private to public.
BINS_MONGO_TO				Destination collection name for bin meta during transfer from private to public.
BINS_MONGO_FROM				Source collection name for bin meta during transfer from private to public.
SLEEP_TIME					Amount of time in seconds the script should idle if there is no new data to calculate.
```

#[vizmo_tilemill]
```
AGGREGATIONS_MONGO_TO		Destination collection name for aggregations during transfer from private to public.
AGGREGATIONS_MONGO_FROM		Source collection name for aggregations during transfer from private to public.
BINS_MONGO_TO				Destination collection name for bin meta during transfer from private to public.
BINS_MONGO_FROM				Source collection name for bin meta during transfer from private to public.
MAP_DIR						Directory to store local maps while rendering in TileMill.
TILEMILL_DIR				Location of the TileMill binary. This is not applicable to the Python server and can be safely ignored there.
BBOX						Bounding box definition for TileMill. 
MINZOOM						Minimum zoom level to render.
MAXZOOM						Maximum zoom level to render.
FILES						Location of the TileMill project files.
SYNC_ACCOUNT				Mapbox account name to upload to.
SYNC_ACCESS_TOKEN			Token for Mapbox account authentication.
SLEEP_TIME					Amount of time in seconds the script should idle if there are no new maps to render.
MAP_PROCESS_COUNT			Number of map rendering jobs to run in parallel. 
```


#[tilemill_projects]
List of TileMill projects to render and upload each day. Each entry corresponds to one project of the same name.

#[database]

```
PUBLIC_MONGO_URL	Location of the public Mongo DB in Mongo URL format. 
PUBLIC_MONGO_DB		Name of the public Mongo Database.
PRIVATE_MONGO_URL	Location of the private Mongo DB in Mongo URL format. 
PRIVATE_MONGO_DB	Name of the private Mongo Database.
```

#[mapreduce]

```
GEO_TYPE					Geometry type to use for national aggregations. 
MAP_PROCESS_COUNT			Number of processes to use for the map phase of map reduce.
REDUCE_PROCESS_COUNT		Number of processes to use for the reduce phase of map reduce.
AGGREGATION_PROCESS_COUNT	Number of processes to use for the national aggregation process.
```
