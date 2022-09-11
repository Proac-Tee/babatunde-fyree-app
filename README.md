## Fyyur

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

## Overview

This is a a fully functioning site that is capable of doing the following, using a PostgreSQL database:

- creating new venues, artists, and creating new shows.
- searching for venues and artists.
- learning more about a specific artist or venue.

## Tech Stack (Dependencies)

### 1. Backend Dependencies

The backend tech stacks includes the following:

- **virtualenv** as a tool to create isolated Python environments
- **SQLAlchemy ORM** to be our ORM library of choice
- **PostgreSQL** as our database of choice
- **Python3** and **Flask** as our server language and server framework
- **Flask-Migrate** for creating and running schema migrations
  You can download and install the dependencies mentioned above using `pip` as:

```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```

> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed.

### 2. Frontend Dependencies

You must have the **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend. Bootstrap can only be installed by Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). Windows users must run the executable as an Administrator, and restart the computer after installation. After successfully installing the Node, verify the installation as shown below.

```
node -v
npm -v
```

Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:

```
npm init -y
npm install bootstrap@3
```

## Main Files: Project Structure

```sh
├── README.md
├── app.py *** the main driver of the app. Includes your SQLAlchemy models.
                  "python app.py" to run after installing dependencies
├── config.py *** Database URLs, CSRF generation, etc
├── error.log
├── forms.py *** Your forms
├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
├── static
│   ├── css
│   ├── font
│   ├── ico
│   ├── img
│   └── js
└── templates
    ├── errors
    ├── forms
    ├── layouts
    └── pages
```

Overall:

- Models are located in the `MODELS` section of `app.py`.
- Controllers are also located in `app.py`.
- The web frontend is located in `templates/`, which builds static assets deployed to the web server at `static/`.
- Web forms for creating data are located in `form.py`

## Development Setup

1. **Install the dependencies:**

```
pip install -r requirements.txt
```

2. **Run the development server:**

### MAC, LINUX and Git-Bash

```
export FLASK_APP=myapp
export FLASK_ENV=development
export FLASK_DEBUG=true
python3 app.py
```

### In CMD

```
set FLASK_APP=myapp
set FLASK_ENV=development
set FLASK_DEBUG=true
python3 app.py
```

3. **Verify on the Browser**<br>
   Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000)
