# An emotion-based recommender system

This project implements an emotion-based recommender system, built within the scope of my bachelor's thesis **Emotion-based Recommender System for City Visitors Built on Analyzing Egocentric Images**. It recommends places to visit on a map, based on the emotion of pictures which were taken there, the location and the emotion of the user. It uses, amongst others, the [Flickr API](https://www.flickr.com/services/api/), the [Clarifai API](https://clarifai.com/developer/quick-start/), an [emotion dictionary](https://www.god-helmet.com/wp/whissel-dictionary-of-affect/index.htm), [Leaflet](http://leafletjs.com/), a [sidebar for Leaflet](https://github.com/Turbo87/sidebar-v2), and [Flask](http://flask.pocoo.org/). The frontend (`index.html`) is based on HTML and JavaScript, the backend (`app.py`) is based on Python. The communicate between them is realized via Ajax.

## How to get started

The project requires a **web browser** (successfully tested on Chrome and Firefox) and **Python 3.x** to be installed.

To begin, run `pip install -r requirements.txt --upgrade` once before the first run to install the newest versions of all required Python packages.

**Note:** The `clarifai` package installs an older version of the `requests` package, if installed manually, and not via the `requirements.txt` file; however, this version is working as well. If you are on Windows and installing the package returns an error, you might also need to install the [Microsoft Visual C++ Build Tools](https://go.microsoft.com/fwlink/?LinkId=691126), including Windows 8/8.1 SDK.

## How to run the project

(1) Run `python app.py`
(2) Open `index.html`

All used files can be found in the folder `static`.

**Note:** The calculation of the first set of recommendations might take a few seconds, all following recommendations should be ready immediately.

## Picture databases

- `flickr.csv` contains information about pictures from Flickr taken in and around Helsinki.
- `local.csv` contains information about pictures from Flickr taken in and around Munich.

Both databases can be found in the folder `static`.

**Note:** The database `local.csv` is meant to contain information about pictures which are all downloaded and stored locally in the folder `img`. For copyright reasons, the `img` folder does not contain any pictures. Instead, the pictures can be manually downloaded via the links in the file `links.txt`, e.g. by using a download manager.

## Creating an own picture database

If you want to create your own picture database via the recommender system ("create your own by clicking **here**"), you need to set API keys for Flickr and Clarifai in `app.py`. They are specified in the variables `FLICKR_API_KEY` and `CLARIFAI_API_KEY`. The keys can be obtained for free from the services' websites. The database creation takes a few minutes, because 100 (default number) pictures need to be uploaded via the Clarifai API for the image content analysis. A message is shown on the commend line for each successfully analyzed picture, and the browser sends a notification when the database has been successfully stored in the file `flickr-own.csv`. You can rename it to `flickr.csv` and overwrite the old database to use the new one from now on.

## Additional files

`xmlParser.py` and `RecSys.py` have the same capabilities as the respective functions called in `app.py`. They can be used with command line options, as shown within the files.

`csvParser.py` can analyze locally saved pictures and add the collected information to an existing picture database. An example can be found in the folder `example`.

`plots.py` can create plots to visualize the data contained in the picture databases.