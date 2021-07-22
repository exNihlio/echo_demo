## What is this?

A simple API server written in Python with Bottle.
It takes a JSON encoded body and echoes it back with the added
key/value of `"echoed": true"`. Additionally, if you return that
same body and it detects the `"echoed": true"` key/value, it returns
an error.