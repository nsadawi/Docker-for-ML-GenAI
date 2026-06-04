# Building and using a Docker Image/Container

### This example helps you create a Docker image that:
* Is based on the Docker image python:3.11-slim.
* We will the sklearn and pandas packages.
* A Python script that receives a CSV file, perform some calculations on it and write the results into a results file.
* This results file should be saved into our host machine (permanent using a Docker volume).



* Let’s build our image (you can choose your own tag):
`docker build -t ml-regressor .`


* and now we run the container passing it our dataset file and specifying the folder we want to the result to be stored in (using volumes):
`$ docker run --rm -v "$(pwd)":/work ml-regressor dataset.csv`

* `-v "$(pwd)":/work` Mounts your current folder (`$(pwd)`) to the container's `/work` directory.

* This `/work/` is the directory inside the container (the script will write the results there)

* `dataset.csv` This is passed directly into your script as `sys.argv[1]`.
* `--rm` Automatically cleans up and deletes the container instance after it finishes running to save disk space.