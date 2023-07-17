# Robot Mission and Fault Logging
This project was used to test out some of the capabilities of the streamlit library and to streamline robot mission and fault logging, which I normally did through a large spreadsheet and accompanying on-board video.

## Description
This is a simple CRUD-type web app and accomplishes the following:
* Create or use an existing mission and log faults to a mission
* Create and view video clips of faults

## Getting Started
1. Fork the repository and install dependencies
    1. cd into repository and run command: `pip install -r requirements.txt` in terminal
1. [Download and setup a MongoDB server](https://www.mongodb.com/docs/manual/installation/)
2. Add a single database into your server named project. Then add 2 collections within the project database named: 'missions' and 'faults'
    1. This can be done through mongosh shell, MongoDBCompass, etc. See MongoDB documentation for more info.
4. Create a /.streamlit folder into the project repository and add a file called 'secrets.toml'
    1. The secrets file should have the following (replace with your server's login info):
    1. `[mongo]`\
`host = "localhost"`\
`port = 27017`\
`username = ""`\
`password = ""`
5. Adjust the config.py file to match your chosen options.
    1. There are 2 tuples within config.py: FAULT_OPTIONS and UNIT_OPTIONS
    2. Change the string literals to match your configuration.
6. Run the app by typing this command into the terminal: `streamlit run Add_logs.py`

## How to Use


## Extras
### Deploying
You'll probably want to deploy the app to the web. Here are several options available to you. Depending on your deployment choice, securely connecting to the database may require extra steps.
* [Deploy via streamlit community cloud](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
* [Deploy with Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
* [Deploy with Docker & Kubernetes](https://docs.streamlit.io/knowledge-base/tutorials/deploy/kubernetes)
