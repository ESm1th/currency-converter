# currency_converter
Simple HTTP API currency converter USD -> RUB

### How to start
Clone repository:
```
$ git clone https://github.com/ESm1th/currency_converter.git
```
Change direcotry to project folder:
```
$ cd currency_converter/
```

### Run with docker
If you prefer to use `docker` you can build image:
```
$ docker build --tag converter .
```
And then run container with default `port` 8000:
```
$ docker run --network host converter
```
or if default port is busy with another `port` by setting `environment` variable `PORT`:
```
$ docker run --network host --env PORT=8080 converter
```
Server is running in docker container now.

### Run with python
Create virtualenvironment and activate it:
```
$ mkvirtualenv converter --python=python3.7
```
Then change directory to `converter` folder and run:
```
$ python server.py
```

 Create virtual environment:
 ```
 $ mkvirtualenv converter --python=python3
 ```
