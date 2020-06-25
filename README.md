# Cloud Asset Uploader

A server that allows a client to:
1) Generate a signed URL for uploading an asset securely to Amazon S3.
2) Allow marking an upload's status (i.e. mark an asset as COMPLETE)
3) Generate a signed URL for getting a COMPLETE asset from S3.

# Prerequisites

The server runs with python 3.7. All of the instructions below assume that you have python 3.7 installed, and that running `python` in your shell refers to that install.

The server also requires that you have aws credentials configured. On a local (i.e. not EC2) machine,
this will mean that you need the AWS CLI installed, and that you have called `aws configure` to save your
credentials. To install the CLI, please see https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html.

Lastly, the server also requires that you have PostgreSQL 10 installed. A simple way to get this install for Mac is to follow the steps at https://postgresapp.com/ (Choose the download option that reads `Postgres.app with PostgreSQL 10, 11 and 12`).

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

7) The server uses yoyo to migrate the PostgreSQL database schema. To bootstrap the database schema, simply obtain the connection string (such as `postgresql://bob:@localhost:5432/db`) and run `yoyo apply --database <YOUR_CONNECTION_STRING_HERE> ./migrations` from the root directory of the repo.

8) The server relies on an env variable called `POSTGRESQL_LIBPQ_CONN_STR` for the connection string to your PostgreSQL instance. A sample connection string is below, replace the following command with the connection details to your PostgreSQL server:
`export POSTGRESQL_LIBPQ_CONN_STR='host=localhost port=5432 dbname=db user=bob password=security'`

9) Finally, to run the server, simply run:
`python cloud_asset_server.py`

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

Oh, boy, do I have a list.