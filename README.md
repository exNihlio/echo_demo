## What is this?

A simple API server written in Python with Bottle.
It takes a JSON encoded body and echoes it back with the added
key/value of `"echoed": true"`. Additionally, if you return that
same body and it detects the `"echoed": true"` key/value, it returns
an error.

## Usage

### Build the Docker image
`docker build -t demo_echo:1 .`

### Run the Docker container
`docker run --rm -d -p 8080:8080 demo_echo:1`

### Validate that the server is running correctly

`curl -v --header "Content-Type: application/json" --data '{"foo": "bar"}' -XPOST  http://127.0.0.1:8080/api/echo`

If everything is working correctly you should see this:

`{"foo": "bar", "echoed": true}`