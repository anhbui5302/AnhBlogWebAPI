AnhBlogWebAPI
=============

A basic blog app API built using the Flask micro web framework.

Written using python 3.10.5, thus, it is recommended that you use the same python version. Using other python versions may or may not work.

Install
-------

Clone the repository::


	$ git clone https://github.com/anhbui5302/AnhBlogWebAPI
	$ cd AnhBlogWebAPI

Create a virtualenv and activate it::

	$ python3 -m venv venv
	$ . venv/bin/activate

Or on Windows cmd::

	$ python -m venv venv
	$ venv\Scripts\activate.bat

Install dependencies::

	$ pip install -r requirements.txt

You will also need a config.py file from one of the contributors. It contains the secret key as well as client ids and secrets needed for authentication using Google and Facebook. You will not be able to run without it.

When you have the config.py file, create a new folder called "instance" and put the file inside it. The path should look like "../AnhBlogWebAPI/instance/config.py"

Run
---

To run the server, in the terminal run the following::

    $ export FLASK_APP=app
    $ export FLASK_ENV=development
    $ flask run --cert=adhoc

Or on Windows cmd::

    > set FLASK_APP=app
    > set FLASK_ENV=development
    > flask run --cert=adhoc

Afterwards, open a separate terminal and run the following in the same directory::

	> flask init-db

This will initialize the database file in the instance folder which the app will use. It will also overwrite an existing database with a new, clean one.

Open https://127.0.0.1:5000/google or https://127.0.0.1:5000/facebook in a browser to login using either Google or Facebook. NOTE: Only google authentication is possible at this moment at /login.

Ignore the warning by your browser. This happens because the security certificate is self-signed since the server is running on localhost.

Usage
-----

For now, open the app.py file and browse through the various functions to see which endpoints are available as well as what kind of request you can send to those endpoints.

For the time being, it only possible to send HTTP requests using Chrome's Web Developer Tool. To access it, while Chrome is open, press f12 or Ctrl+Shift+I and then click on the Console tab.

HTTP requests can be sent using the following format::

	fetch(URL, {
	  method: METHOD,
	  body: JSON.stringify({
		variable1: 'variable_value1',
		variable2: 'variable_value2',
		variable3: 'variable_value2',
	  }),
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

URL is the URL of the endpoint you want to send the HTTP request to (e.g. https://127.0.0.1:5000/).
METHOD is the request method (e.g. GET and POST).
Inside the body of the request, you may have to provide additional parameters if required.