# currency-converter
Simple HTTP API currency converter USD -> RUB

Dependency: `python 3.7`

## How to start
Clone repository:
```
$ git clone https://github.com/ESm1th/currency-converter.git
```
Change direcotry to project folder:
```
$ cd currency-converter/
```

#### Run with docker
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


#### Run with python
Create virtual environment and activate it:
```
$ mkvirtualenv converter --python=python3.7
```
Then change directory to `converter` folder and run:
```
$ python server.py
```

#### Sending requests
Valid `method` is `POST` and valid `url` format for requests:
```
http://{host}:{port}/convert/
```
Valid request must include parameter `amount`.

Examples with `httpie` python app (you can install it with `pip install httpie`):
Valid request:
```
$ http POST http://localhost:8080/convert amount=10
```
Response to this request:
```python
HTTP/1.0 200 OK
Content-Type: application/json
Date: Thu, 20 Feb 2020 17:38:29 GMT
Server: BaseHTTP/0.6 Python/3.7.6

{
    "amount": 10.0,
    "from": "USD",
    "result": 636.9679699999999,
    "to": "RUB"
}
```

Invalid request with non existing path `/non-existing/` but with valid `method`:
```
$ http POST http://localhost:8080/non-existing/
```
Response to this request:
```python
HTTP/1.0 404 Not Found
Content-Type: application/json
Date: Thu, 20 Feb 2020 17:41:05 GMT
Server: BaseHTTP/0.6 Python/3.7.6

{
    "error": "Path /non-existing/ does not exist."
}
```
The same request but with invalid `method`:
```
$ http http://localhost:8080/non-existing/
```
Response to this request:
```python
HTTP/1.0 405 Method Not Allowed
Content-Type: application/json
Date: Thu, 20 Feb 2020 17:43:14 GMT
Server: BaseHTTP/0.6 Python/3.7.6

{
    "error": "Request method not allowed."
}
```
### Run tests
From `currency-converter/converter` folder:
```
python -m unittest -v tests
```
