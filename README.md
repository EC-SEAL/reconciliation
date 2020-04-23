# SEAL Automated Identity Reconciliation Module

To run the container `faragom/seal-reconciliation:latest`, you need to set up a folder with the contents of the `data/` folder in the repository, but adapted to your own needs. Also see the properties file for additional files that might be needed.

```[shell script]
docker run -p HOST_PORT:8080 -v "LOCAL_PATH_data:/app/data" \
  --env PROPERTIES_FILE=/app/data/server.properties \
  --env ENCRYPTION_KEY=ENC_KEY \
  --name seal-reconciliation faragom/seal-reconciliation:latest
```

* `-p HOST_PORT:8080`  Substitute **HOST_PORT** for the port you want to expose the microservice on
* `-v "LOCAL_PATH_data:/app/data"`  Substitute **LOCAL_PATH_data** for the path to your volume folder
* `--env PROPERTIES_FILE=/app/data/server.properties`  Leave this environment variable as is
* `--env ENCRYPTION_KEY=ENC_KEY`  Substitute **ENC_KEY** for a string password that will be used to encrypt the 
sensitive cells on the requests volatile database (resets on every run and after some timeout)
* `--name seal-reconciliation`  The name of the container. Use this or change at will.