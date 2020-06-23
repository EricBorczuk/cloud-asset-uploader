# Cloud Asset Uploader

A server that allows a client to:
1) Generate a signed URL for uploading an asset securely to Amazon S3.
2) Allow marking an upload's status (i.e. mark an asset as COMPLETE)
3) Generate a signed URL for getting a COMPLETE asset from S3.

# Getting Started

The service runs with python 3.7. All of the instructions below assume that you have python 3.7 installed, and that running `python` in your shell refers to that install.

1) To get started, be sure to install pip (for python 3) by executing in a shell:
`curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
`python get-pip.py`

2) Create a virtual environment in a directory of your choosing:
`python -m venv /someplace/of/your/choice`

3) Activate the virtualenv by running
`source /someplace/of/your/choice/bin/activate`

4) Clone this git repository and `cd` in.

5) Run `pip install -r requirements.txt`

6) The server relies on env variables for your AWS credentials. Set your credentials:
`export AWS_ACCESS_KEY_ID=???`
`export AWS_SECRET_ACCESS_KEY=???`

7) Run the server.

