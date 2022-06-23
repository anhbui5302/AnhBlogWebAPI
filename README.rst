AnhBlogWebAPI
=============

A basic blog app API built using the Flask micro web framework.

Written using python 3.10.5, thus, it is recommended that you use 
the same python version. Using other python versions may or may 
not work.

Install
-------

Clone the repository::


	$ git clone https://github.com/anhbui5302/AnhBlogWebAPI
	$ cd AnhBlogWebAPI

Create a virtualenv and activate it::

	$ python3 -m venv venv
	$ . venv/bin/activate

Or on Windows cmd::

	> python -m venv venv
	> venv\Scripts\activate

Install dependencies::

	$ pip install -r requirements.txt

You will need a config.py file from one of the contributors. It 
contains the secret key as well as client ids and secrets needed 
for authentication using Google and Facebook. You will not be able 
to run without it. When you have the config.py file, create a new 
folder called "instance" and put the file inside it. The path should 
look like "../AnhBlogWebAPI/instance/config.py"

You will also need to create a .env file in the root folder of the 
project. The path should look like "../AnhBlogWebAPI/.env".

Put the following into the .env file::

	FLASK_APP="app"
	FLASK_ENV="development"

Run
---

To run the server, in the terminal run the following::

    $ flask run --cert=adhoc

Or on Windows cmd::

    > flask run --cert=adhoc

Afterwards, open a separate terminal and run the following in the same directory::

	> flask init-db

Make sure that venv is activated.

This will initialize the database file in the instance folder which 
the app will use. It will also overwrite an existing database with a 
new, clean one.

Open https://127.0.0.1:5000/google or https://127.0.0.1:5000/facebook 
in a browser to log in using either Google or Facebook.

Ignore the warning by your browser. This happens because the security 
certificate is self-signed since the server is running on localhost.

Test
----

To perform tests, in the terminal run the following::

    $ pytest
	
Or test with coverage::

	$ coverage run -m pytest
	$ coverage report
	$ coverage html

Open htmlcov/index.html in a browser to view the coverage report.

Currently tests cover almost 100% of all written code. Only the callback 
routes which are redirected to after the user authenticates themselves
through either Google or Facebook have not been covered by the tests. 
However, the creation of a user based on the email address as well as 
getting said user back from the database are tested separately.

Usage
-----

Once the server is running, you can use any program that can send 
HTTP requests to interact with it, such as: Chrome's Web Developer 
Tool, curl, Postman, etc.

The URLs returned by the /google and /facebook endpoints need to be 
accessed through a browser.

Ensure that for all blog API endpoints, include 'Authorization' with 
value 'Bearer TOKEN' in the header of your requests. 
TOKEN is the token provided by the server after the user has successfully 
authenticated themselves.

For requests that require additional data to be passed through the body, 
include 'Content-Type' with value 'application/json' in the header.

Data included in the request body also has to be in json form, like so::

	{
		"var1":"value1",
		"var2":"value2",
		"var3":"value3"
	}

If you're using Chrome's Web Developer Tool, HTTP requests can be sent 
through the console after pressing f12, using the following format::

	fetch(URL, {
	  method: METHOD,
	  body: JSON.stringify({
		variable1: 'variable_value1',
		variable2: 'variable_value2',
		variable3: 'variable_value2'
	  }),
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
		'Authorization': 'Bearer TOKEN'
	  }
	})
	.then(res => res.json())
	.then(console.log)

URL is the URL of the endpoint you want to send the HTTP request to 
(e.g. https://127.0.0.1:5000/). Query parameters are attached to the 
end of the URL (e.g. https://127.0.0.1:5000/?page=2). METHOD is the 
request method (e.g. GET or POST). Inside the body of the request, 
you may have to provide additional data if required.

Requests with GET/HEAD method cannot have a body so make sure to 
remove them like so::

	fetch(URL, {
	  method: METHOD,
	  headers: {
		'Content-type': 'application/json; charset=UTF-8',
		'Authorization': 'Bearer TOKEN'
	  }
	})
	.then(res => res.json())
	.then(console.log)

Endpoints
---------

User Authorization and Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

/google
"""""""

*- Description*

The first step in the Google OAuth 2 login flow. It will figure out
where Google's OAuth 2 Authorization endpoint is and then construct 
the request for Google login.

*- URL Structure*

https://127.0.0.1:5000/google

*- Method*

GET

*- Required Headers*

None

*- Required Body Data*

None

*- Sample Request*

Get request for Google login::

	fetch('https://localhost:5000/google', {
	  method: 'GET',
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

None

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``URL`` (*String*) The URL the user access in the browser to log in 
  into their google account.
- ``message`` (*String*) A message telling the user what to do 
  with the URL.

*- Sample Response*::

	{
	  "URI": "https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=<client_id>&redirect_uri=https%3A%2F%2Flocalhost%3A5000%2Fgoogle%2Fcallback&scope=openid+email", 
	  "message": "Access the URI below through a browser to log in."
	}

*- Response Codes*

| Success: 200
| Error: 404
|

/google/callback
""""""""""""""""

*- Description*

| Once the user has accessed the URL provided by /google on a browser, 
  they will be authenticated and authorized on Google's end. Once the 
  user has logged in with Google and agreed to share their email with 
  the API, Google then redirects to this endpoint and pass in arguments 
  which contain the authorization code.
| The client then use the authorization code provided to exchange for 
  access tokens which can be used to obtain the email the client needs.
  A Google user with the email obtained will be created in the database 
  if it has not existed already. Lastly, the user's ID is stored in the
  session to authenticate the user in other endpoints. 

| 

*- URL Structure*

https://127.0.0.1:5000/google/callback

*- Method*

GET

*- Required Headers*

None

*- Required Body Data*

None

*- Sample Request*

Redirected from Google login and request access::

	fetch('https://127.0.0.1:5000/google/callback?code=4%2F0AX4XfWjk5Kgcak3aiSmx5TfDe0-j_bxVLv2jc3FZZBs5jTeE-5qJ5whhoVKOazaTmJoETw&scope=email+openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email&authuser=0&prompt=none', {
	  method: 'GET',
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

All parameters are returned by the Google Authorization endpoint.

- ``code`` (*String*) The authorization code.
- ``scope`` (*String*) A string that determines the endpoints to which 
  the client has access.
- ``authuser`` (*String*) A string that is determined by the n-th user 
  already logged into Google being used by the authorization endpoint.
- ``prompt`` (*String*) A string that is determined by whether the 
  user were shown the re-consent prompt or not.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``message`` (*String*) A message telling the user that they 
  have logged in successfully.
- ``token`` (*String*) A token the user can use to authenticate 
  themselves.

|

Sample Response::

	{
	  "message": "Login successful. Send the provided token as a bearer token in the header of your HTTP request to the API to authenticate yourself.", 
	  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNjU2MDA1MjEwfQ.6bM0AQg2p9FkyAimUxFoplmWidSzkpOP1eWBBLgH2U8"
	}

*- Response Codes*

| Success: 200
| Error: 400, 401, 404
|

/facebook
"""""""""

*- Description*

The first step in the Facebook OAuth 2 login flow. It will figure out
where Facebook's OAuth 2 Authorization endpoint is and then construct 
the request for Facebook login.

*- URL Structure*

https://127.0.0.1:5000/facebook

*- Method*

GET

*- Required Headers*

None

*- Required Body Data*

None

*- Sample Request*

Get request for Facebook login::

	fetch('https://127.0.0.1:5000/facebook', {
	  method: 'GET',
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

None

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``URL`` (*String*) The URL the user access in the browser to 
  log in into their google account.
- ``message`` (*String*) A message telling the user what to 
  do with the URL.

*- Sample Response*::

	{
	  "URI": "https://facebook.com/dialog/oauth/?response_type=code&client_id=<client_id>&redirect_uri=https%3A%2F%2Flocalhost%3A5000%2Ffacebook%2Fcallback&scope=email", 
	  "message": "Access the URI below through a browser to log in."
	}

*- Response Codes*

| Success: 200
| Error: 404
|

/facebook/callback
""""""""""""""""""

*- Description*

| Once the user has accessed the URL provided by /facebook on a browser, 
  they will be authenticated and authorized on Facebook's end. Once the 
  user has logged in with Facebook and agreed to share their email with 
  the API, Facebook then redirects to this endpoint and pass in arguments 
  which contain the authorization code.
| The client then use the authorization code provided to exchange for 
  access tokens which can be used to obtain the email the client needs.
  A Facebook user with the email obtained will be created in the database 
  if it has not existed already. Lastly, the user's ID is stored in the
  session to authenticate the user in other endpoints. 

*- URL Structure*

https://127.0.0.1:5000/facebook/callback

*- Method*

GET

*- Required Headers*

None

*- Required Body Data*

None

*- Sample Request*

Redirected from Facebook login and request access::

	fetch('https://127.0.0.1:5000/facebook/callback?code=AQBOBF97uu798i1VLp3p291w0PyVciEgVrI45Mqbn5UIaVjjyT7SnDsBQLxiMGDKOsf-ubkp7pgV-HfUE2obwHgkS9uJrWsCb3TVHeYgNoXDG4qlAQz5djXV7PKrgAWqJ04zhpHrlPGgruCKO9HTvsFQp_1QCQxLUbWMRcF9lHRgUtC5Y5wcYsmvXhD3dAbfn4VYKBOp0v-sQoFgnhTYn5zS_qLVoJL7hLNkBHPSkX-pGlze1I3mrmJzL2EuDD63xZvJUw7PTwdKevcOTs5zsvUF2_mNVCXN46m5HFEB8Dpj7BvSB0onRFkA3PjfN49UVqpMF9zNZsGLegYylmg-FR1qQoiQv2xwB8KpzeAN5dIBr4aiVusgar1b0Tvib11gSzQ#_=_', {
	  method: 'GET',
	  headers: {
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

All parameters are returned by the Facebook Authorization endpoint.

- ``code`` (*String*) The authorization code.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``message`` (*String*) A message telling the user that they 
  have logged in successfully.
- ``token`` (*String*) A token the user can use to authenticate 
  themselves.

|

Sample Response::

	{
	  "message": "Login successful. Send the provided token as a bearer token in the header of your HTTP request to the API to authenticate yourself.", 
	  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss"
	}

*- Response Codes*

| Success: 200
| Error: 400, 401, 404
|

Blog Functionality
^^^^^^^^^^^^^^^^^^

/
"

*- Description*

Shows a list containing all posts made by all users. The list 
is paginated. By default, it shows 5 posts per page and starts 
at page 1.

*- URL Structure*

https://127.0.0.1:5000/

*- Method*

GET

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Shows page 2 of the list of all posts with 3 posts per page::

	fetch('https://127.0.0.1:5000/?page=2&perpage=3', {
	  method: 'GET',
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

- ``page`` (*String*) The page number to show.
- ``perpage`` (*String*) The number of posts shown per page.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``nextpage`` (*String*) The query needed to get to the next page.
- ``posts`` (*List of"(*post*)) A list of post objects
- ``post`` (*String*) A JSON-encoded dictionary containing: 
- ``author_id`` (*String*) The id of the author.
- ``author_name`` (*String*) The name of the author.
- ``body`` (*String*) The main text of the post.
- ``created`` (*String*) When the post was created.
- ``likes`` (*String*) Shows users who liked the post.
- ``title`` (*String*) The title of the post.
	
*- Sample Response*::

	{
	  "next_page": "/?page=3&perpage=3", 
	  "posts": [
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 4 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:55 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post4"
		}, 
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 3 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:48 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post3"
		}, 
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 2 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:32 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post2"
		}
	  ]
	}

*- Response Codes*

| Success: 200
| Error: 401, 403
|

/info
"""""

*- Description*

Shows the currently authenticated user's info.

*- URL Structure*

https://127.0.0.1:5000/info

*- Method*

GET

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Shows info of currently authenticated user::

	fetch('https://127.0.0.1:5000/info', {
	  method: 'GET',
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

None

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``email`` (*String*) The user's email.
- ``id`` (*String*) The user's id
- ``name`` (*String*) The user'sname.
- ``occupation`` (*String*) The user's occupation.
- ``phone`` (*String*) The user's phone number.
- ``type`` (*String*) The type of the user.
*- Sample Response*::

	{
	  "email": "luckyjam0503@gmail.com", 
	  "id": 3, 
	  "name": "testname123", 
	  "occupation": "asdfgh", 
	  "phone": ""
	  "type": "Google"
	}

*- Response Codes*

| Success: 200
| Error: 401, 403, 404
|

/updateinfo
"""""""""""

*- Description*

Updates the currently authenticated user's info with new values.

*- URL Structure*

https://127.0.0.1:5000/updateinfo

*- Method*

PATCH

*- Required Headers*

'Content-type': 'application/json'

*- Required Body Data*

| ``name`` The new name of the user.
| ``phone`` (for Facebook users) The new phone number of the user.
| ``occupation`` (for Google users) The new occupation of the user.

*- Sample Request*

Updates info of currently authenticated user::

	fetch('https://127.0.0.1:5000/updateinfo', {
	  method: 'PUT',
	  body: JSON.stringify({
		name: 'TyperMan',
		phone: '1234567890',
		occupation: 'Typist'
	  }),
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

*- Parameters*

None

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``message`` (*String*) A message telling the user that they 
  have updated their info successfully.
	
*- Sample Response*::

	{
	  message: "User info successfully updated!" 
	}

*- Response Codes*

| Success: 200
| Error: 400, 401
|

/create
"""""""

*- Description*

Creates a new post using the info provided.

*- URL Structure*

https://127.0.0.1:5000/create

*- Method*

POST

*- Required Headers*

| 'Authorization': 'Bearer TOKEN'
| 'Content-type': 'application/json'

*- Required Body Data*

| ``title`` The title of the new post.
| ``body`` The main text of the new post.

*- Sample Request*

Creates a new post::

	fetch('https://127.0.0.1:5000/create', {
	  method: 'POST',
	  body: JSON.stringify({
		title: 'NewPostTitle',
		body: 'NewPostBody'
	  }),
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

*- Parameters*

None

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``message`` (*String*) A message telling the user that they 
  have successfully created a new post.
	
*- Sample Response*::

	{
	  message: "New post created!"
	}

*- Response Codes*

| Success: 201
| Error: 400, 401, 403 
|

/<author_id>/posts
""""""""""""""""

*- Description*

Shows a list containing all posts made by a user.

*- URL Structure*

https://127.0.0.1:5000/<author_id>/posts

*- Method*

GET

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Shows all posts made by user with id of 7::

	fetch('https://127.0.0.1:5000/7/posts', {
	  method: 'GET',
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

- ``author_id`` (*String*) The id of the user whose posts are 
  requested.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:

- ``posts`` (*List of"(*post*)) A list of post objects
- ``post`` (*String*) A JSON-encoded dictionary containing: 
- ``author_id`` (*String*) The id of the author.
- ``author_name`` (*String*) The name of the author.
- ``body`` (*String*) The main text of the post.
- ``created`` (*String*) When the post was created.
- ``likes`` (*String*) Shows users who liked the post.
- ``title`` (*String*) The title of the post.
	
*- Sample Response*::

	{ 
	  "posts": [
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 4 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:55 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post4"
		}, 
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 3 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:48 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post3"
		}, 
		{
		  "author_id": 3, 
		  "author_name": "testname123", 
		  "body": "This is post no 2 for user id 3", 
		  "created": "Thu, 16 Jun 2022 20:58:32 GMT", 
		  "likes": "No one has liked this post yet.", 
		  "title": "post2"
		}
	  ]
	}

*- Response Codes*

| Success: 200
| Error: 401, 403, 404
|

/<author_id>/posts/<post_id>
""""""""""""""""""""""""""

*- Description*

Shows the details of a post.

*- URL Structure*

https://127.0.0.1:5000/<author_id>/posts/<post_id>

*- Method*

GET

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Shows the details of post with id 1 made 
by a user with id 1::

	fetch('https://127.0.0.1:5000/1/posts/1', {
	  method: 'GET',
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)	

*- Parameters*

- ``author_id`` (*String*) The id of the user whose posts are 
  requested.
- ``post_id`` (*String*) The id of the post.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``author_id`` (*String*) The id of the author.
- ``author_name`` (*String*) The name of the author.
- ``body`` (*String*) The main text of the post.
- ``created`` (*String*) When the post was created.
- ``likes`` (*String*) Shows users who liked the post.
- ``title`` (*String*) The title of the post.
	
*- Sample Response*::

	{
	  "author_id": 1, 
	  "author_name": "anhbui5302", 
	  "body": "This is post no 1 for user_id 1", 
	  "created": "Thu, 16 Jun 2022 20:51:58 GMT", 
	  "likes": "anhbui5302, fb acc and 3 other people liked this post.", 
	  "title": "Post1"
	}

*- Response Codes*

| Success: 200
| Error: 401, 403, 404
|

/<author_id>/posts/<post_id>/like
"""""""""""""""""""""""""""""""

*- Description*

Like or unlike a post given the author's id and the 
post's id.

*- URL Structure*

https://127.0.0.1:5000/<author_id>/posts/<post_id>/like

*- Method*

POST, DELETE

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Likes a post of id 1 and author of id 1::

	fetch('https://127.0.0.1:5000/1/posts/1/like', {
	  method: 'POST',
	  body: JSON.stringify({
	  }),
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

Unlikes a post of id 1 and author of id 1::

	fetch('https://127.0.0.1:5000/1/posts/1/like', {
	  method: 'DELETE',
	  body: JSON.stringify({
	  }),
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

*- Parameters*

- ``author_id`` (*String*) The id of the author.
- ``post_id`` (*String*) The id of the post.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:
  
- ``message`` (*String*) A message telling the user that they 
  have successfully liked or unliked the post.
	
*- Sample Response*

Liking a post::

	{
	  message: "Liked the post!"
	}

Unliking a post::

	{
	  message: "Removed like from post!"
	}

*- Response Codes*

| Success: 200, 201
| Error: 400, 401, 403, 404
|

/<author_id>/posts/<post_id>/likes
""""""""""""""""""""""""""""""""

*- Description*

Shows all users who like a post given the post's id
and the author's id.

*- URL Structure*

https://127.0.0.1:5000/<author_id>/posts/<post_id>/likes

*- Method*

GET

*- Required Headers*

'Authorization': 'Bearer TOKEN'

*- Required Body Data*

None

*- Sample Request*

Shows all users who liked post of id 3 and author of id 1::

	fetch('https://127.0.0.1:5000/1/posts/3/likes', {
	  method: 'GET',
	  headers: {
		'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6NywiZXhwIjoxNjU2MDA1Mjk3fQ.7wlaFhjpYJmU6p4ORrFi732LQCPHyl4qF_m_29zSrss',
		'Content-type': 'application/json; charset=UTF-8'
	  }
	})
	.then(res => res.json())
	.then(console.log)

*- Parameters*

- ``author_id`` (*String*) The id of the author.
- ``post_id`` (*String*) The id of the post.

*- Returns*

This endpoint returns a JSON-encoded dictionary including 
fields below:

- ``users`` (*List of"(*user*)) A list of user objects
- ``user`` (*String*) A JSON-encoded dictionary containing:  
- ``email`` (*String*) The user's email.
- ``id`` (*String*) The user's id
- ``name`` (*String*) The user'sname.
- ``occupation`` (*String*) The user's occupation.
- ``phone`` (*String*) The user's phone number.
- ``type`` (*String*) The type of the user.

*- Sample Response*::

	{
	  "users": [
		{
		  "email": "luckyjam53@gmail.com", 
		  "id": 4, 
		  "name": "me tired", 
		  "occupation": "asdfgh", 
		  "phone": 1234567890
		  "type": "Google"
		}, 
		{
		  "email": "testforwebapp1@gmail.com", 
		  "id": 2, 
		  "name": "testname", 
		  "occupation": "asd", 
		  "phone": ""
		  "type": "Google"
		}
	  ]
	}

*- Response Codes*

| Success: 200
| Error: 401, 403, 404