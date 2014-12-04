---
layout: default
title: API Basics
nav: basics
---

### API Basics

Visualizing Mobile Broadband is a RESTful GET API that is located at: ```http://vizmo.fcc.gov/api/```

##### File Formats
The API returns the data in the following formats:

- json
- jsonp?callback=myCallback
- geojson
- xml

##### Endpoints
The endpoint for querying all data begins with ```/api/```.

| Endpoint | What it does |
| ------------- | -------------|
| /api/carrier.{file} | Returns data for all carriers separately: combined, att, sprint, tmobile, verizon, and other.
| /api/carrier/{provider}.{file} | Returns the information for a specific provider.
| /api/meta.{file} | Returns metadata information including the last updated date.

##### Spatial Queries
The API calls will return data for a specific location if ```?lat={lat}&lon={lon}``` are provided in the query string of the API call.

When Latitude/Longitude is not provided, the API will return Nationwide data.

| Endpoint | What it does |
| ------------- | -------------|
| /api/carrier.json?lat={lat}&lon={lon} | Returns the information for all carriers separately in the particular location.
| /api/carrier/{provider}.json?lat={lat}&lon={lon} | Returns the information for specified provider in the particular location.

<a href="console/" class="action-arrow">Try It Out <i class="icon-right"> </i></a>

<body id="basics"></body>