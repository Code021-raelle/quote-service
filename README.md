# CiTa Service
Cita is a quote service in inspiring and motivating lives. Cita was created through inspirations to motivate individuals in some certain moments, derived from the Spanish word for `quotes (cita)`.

Our mission is to curate and share quotes that resonate with people's experiences, challenges, and aspirations, offering a spark of inspiration when needed the most.

## Table of Content
* [Environment](#environment)
* [Installation](#installation)
* [File Descriptions](#file-descriptions)
* [Usage](#usage)
* [Examples of use](#examples-of-use)
* [Bugs](#bugs)
* [Database](#database)
* [Authors](#authors)
* [License](#license)
* [Deployment link](#deployed-site-link)

## Environment
This project is interpreted/tested on Ubuntu 22.04 LTS using python3 (version 3.11)

## Installation
* Clone this repository: `git clone "https://github.com/Code021-raelle/quote-service.git"`
* Access Cita directory: `cd quote-service`
* Install build command: `pip install -r requirements.txt`
* Run app(interactively): `python3 app.py` and enter command
* Run app(production server): `gunicorn app:app`

## File Descriptions
[app.py](app.py) - the application contains the main logic of the quote service.

## Examples of use
```
python3 app.py

* Serving Flask app 'app'
* Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a pro
duction WSGI server instead.
* Running on http://127.0.0.1:5000
Press CTRL+C to quit
* Restarting with stat
* Debugger is active!
* Debugger PIN: 101-200-274
```

## Bugs
No known bugs at this time. 

## Database
The database used for this project is postgresql. The database file is `hbnb_dev_db` and it contains tables for quotes, authors, user credentials and categories.
The database schema is defined in `app.py` file.

## Authors
Gabriel Akinshola - [Github](https://github.com/Code021-raelle) / [x](https://x.com/gabbyextra)
Dayo Oshinnaiye - [Github](https://github.com/oshybobo)

## License
Public Domain. Copy write protection.

## Deployed site link
`https://portfolio-project-vzu1.onrender.com`