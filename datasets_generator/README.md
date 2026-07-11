To build the images:

```Shell
docker build -t generate:python .
```

To run the generator script.

```Shell
docker run -it -v raw_data:/app/data/raw --rm generate:python
```


# One-Project

# Script generator of data
to this script you can execute:

```shell
docker run -it generate:python 
docker run -it -v ebm_raw:/app/data/raw generate:python
docker run -it -v ebm_raw:/app/data/raw pipeline:python

docker run -it --network=database_postgresql_default -v ebm_raw:/app/data/raw pipeline:python
```

