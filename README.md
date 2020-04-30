# SEAL Automated Identity Reconciliation Module

##Run the container

To run the container `faragom/seal-reconciliation:latest`, you need to set up a folder with the contents of the `data/` folder in the repository, but adapted to your own needs. Also see the properties file for additional files that might be needed.

```[shell script]
docker run -p HOST_PORT:8050 -v "LOCAL_PATH_data:/app/data" \
  --env PROPERTIES_FILE=/app/data/server.properties \
  --env ENCRYPTION_KEY=ENC_KEY \
  --name seal-reconciliation faragom/seal-reconciliation:latest
```

* `-p HOST_PORT:8050`  Substitute **HOST_PORT** for the port you want to expose the microservice on
* `-v "LOCAL_PATH_data:/app/data"`  Substitute **LOCAL_PATH_data** for the path to your volume folder
* `--env PROPERTIES_FILE=/app/data/server.properties`  Leave this environment variable as is
* `--env ENCRYPTION_KEY=ENC_KEY`  Substitute **ENC_KEY** for a string password that will be used to encrypt the 
sensitive cells on the requests volatile database (resets on every run and after some timeout)
* `--env MSPORT=8050` The port where the internal web server must listen 
* `--env WTHREADS=4` The number of worker threads the 

* `--name seal-reconciliation`  The name of the container. Use this or change at will.


## Expected volume contents
Your volume needs to contain a number of configuration files for the microservice to be operational.
You can find an example of those files in the `data/` directory in the repository

* `server.properties` (*name is fixed*) this file contains most of the configuration parameters of the application. **You will need to change some parameters there**
* `attributeMaps.json` (*name is fixed*) this is the file that holds all the running information of the matching engine. If not planning to twitch the behaviour, just leave the file from the repo as is
* *RSA key file*, In PEM, the RSA private key your microservice will use to do HTTPSig requests. The name depends on a field in the properties file.
* `msMetadataList.json` (*optional*) this file containes the metadata of the other microservices. If you set a CM url, the microservice will periodically try to refresh the contents of this file. It is recommended to provide an initial version to avoid depending on the CM.
* `testLinkRequest.json` (*optional*) if you want to use the test client included on the microservice, specify here the demo link request to be sent.
* `testAuthRequest.json` (*optional*) if you want to use the demo SP module client included on the microservice, specify here the demo auth/query request to be sent.
* `testSPMetadata.json` (*optional*) if you want to use the demo SP module client included on the microservice, specify here the SP metadata object to be sent