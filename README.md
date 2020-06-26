# Cloud Asset Uploader

A server that allows a client to:
1) Generate a signed URL for uploading an asset securely to Amazon S3. (POST `/api/upload`)
2) Allow marking an upload's status (i.e. mark an asset as `complete`) (PUT `/api/status`)
3) Generate a signed URL for getting a `complete` asset from S3. (GET `/api/access`)

# Prerequisites

The server runs with python 3.7. All of the instructions below assume that you have python 3.7 installed, and that running `python` in your shell refers to that install.

The server also requires that you have AWS credentials configured. On a local (i.e. not EC2) machine,
this will mean that you need the AWS CLI installed, and that you have called `aws configure` to save your
credentials. To install the CLI, please see https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html.

In addition, the server requires that you have a bucket in S3 that has read/write access configured for your configured user.

Lastly, the server also requires that you have PostgreSQL 10 installed, and `psql`. A simple way to get this install for Mac is to follow the steps at https://postgresapp.com/ (Choose the download option that reads `Postgres.app with PostgreSQL 10, 11 and 12`).

# Getting Started

1) To get started, be sure to install pip (for python 3) by executing in a shell:
```
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

2) Create a virtual environment in a directory of your choosing:
`python -m venv /someplace/of/your/choice`

3) Activate the virtualenv by running
`source /someplace/of/your/choice/bin/activate`

4) Clone the git repository and `cd` in.

5) Run `pip install -r requirements.txt`

6) Connect to your local PostgreSQL instance and create a database (a one-liner, if your PostgreSQL instance lives at port 5432: `psql postgresql://localhost:5432 -c 'create database db'`). The rest of these instructions operate under the assumption that the database you created was called `db`, and was created at `localhost:5432`, but really you can call it whatever you'd like.

7) The server uses yoyo to migrate the PostgreSQL database schema. To bootstrap the database schema, simply obtain the connection string (such as `postgresql://bob:@localhost:5432/db`) and run `yoyo apply --database <YOUR_CONNECTION_STRING_HERE> ./migrations` from the root directory of the repo. Then, follow the prompts that yoyo gives (type `y` a few times).

8) The server relies on an env variable called `POSTGRESQL_LIBPQ_CONN_STR` for the connection string to your PostgreSQL instance. A sample connection string is below, replace the following command with the connection details to your PostgreSQL server:
`export POSTGRESQL_LIBPQ_CONN_STR='host=localhost port=5432 dbname=db user=bob password=security'`

9) The server needs to know what the name of your s3 bucket is.
`export S3_BUCKET_NAME=<your_s3_bucket_name>`

10) Finally, to run the server, simply run:
`python cloud_asset_server.py`

# View API Docs

To view API documentation, simply open `docs/api_docs.html` in a browser.

# Testing Instructions

Assuming you are in an active virtual environment (See setup above):

1) pip install -r test_requirements.txt

2) Make sure you have a PostgreSQL server running on localhost:5432 (to check just type `psql` in your shell). This PostgreSQL instance will be used for integration tests.

Tests can be run in four ways:

3a) To run only unit tests (starting from the root directory of the repo):
```
cd test/unit
PYTHONPATH=../.. pytest
```

3b) To run only integration tests (starting from the root directory of the repo):
```
cd test/integration
PYTHONPATH=../.. pytest
```

3c) To run ALL tests (starting from the root directory of the repo):
```
PYTHONPATH=. pytest
```

3d) Run a particular test file (starting from the root directory of the repo):
```
PYTHONPATH=. pytest <path/to/testfile.py>
```

Enjoy!

# Reasons why this shouldn't really be used in production/a "real" setting

1) There are no users, and no permissions. This means that anyone who is a good guesser (or wants to brute-force) can mark any asset with the status of `complete` whenever they'd like. In addition, anyone can access anyone's uploaded files by this same guessing game. Ideally we would want users who "own" the asset and can only upload and get their own assets.

2) Because bucket and object_key have a compound unique constraint, no two people can name their file with exactly the same key.  This is a pretty frustrating restriction, so once there are users in the system it would be preferable to make separate paths in s3 within the bucket, where the files would get stored (for instance - for user ID 1, the object could get stored in `uploads/1/<object_key>`)

3) Python is single-threaded by default, so I'd want to make it into a WSGI application with something like gunicorn in order to have parallel worker processes in a production environment. At a glance I don't think there would be any real pitfalls with doing that related to database connection handling, but I could be wrong.

4) While on the topic of databases - I chose to use psycopg2 and raw SQL to make my queries. This was a super simple and not-extensible solution for the purposes of this small server, but I would use something else that provides some degree of safety when changing the schema if this were a long-standing project. Grepping through raw SQL usages every time you change the schema for a table is just not preferable, there's a high chance you'll miss at least one usage and break production.

5) Integration tests were set up in a very naïve fashion (I drop the whole database and recreate it, then run migrations for every test case) - this will scale really poorly with just a few more database migrations, so I'd call it not fit for production. A better solution would involve migrating the database from empty only one time. In addition, having to set up the whole database over and over could be avoided by using PostgreSQL's SAVEPOINTs in a clever fashion, which is something I've always pondered but never really implement because it takes a fair amount of time to get right.

6) I thought about any particular name for no more than 10 seconds before writing something down. In production (well, in a "real" setting with teammates and other engineers), naming is way more important and I would rename a lot of the stuff I named in haste.

The two issues below are a non-issue if you have unlimited money/resources.

7) More of a UX concern with the contract of the service, but it is technically possible to upload a file to S3 and never mark it as completed, which would mean that a file could exist orphaned in S3 (which costs $$$). Would be cool if there were a UI that couples the file upload to talking with the server and marking it complete; or for even better consistency, a single endpoint on this server that handles the file upload transactionally and marks the asset complete.

8) A totally rude user could upload an enormous number of small files, or one enormous file to my S3 and end up charging me a lot of $$$ :'( Since there's really so restrictions on getting signed URL's in this server, it's just ripe for abuse. Compound it with the fact that 7) allows orphaned files, and I could really end up paying a lot of money for files that are never even being accessed by clients, and that would be suboptimal. If we added users/permissions, we could also rate limit user uploads somewhat to keep malicious spammers from doing misdeeds.

I'm sure there are more, and would love to discuss!
