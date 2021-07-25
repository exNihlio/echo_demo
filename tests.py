import sys
import logging as log
import time
from os import environ as env
from json import dumps 
try:
    import httpx
except ImportError:
    log.warning("Module: httpx not imported, please run pip3 install httpx")
    sys.exit(1)

## Config settings
def main():
    try:
        env['HOST_IP'] 
    except KeyError:
        host_ip = '127.0.0.1'
    try:
        env['HOST_PORT']
    except KeyError:
        host_port = 8080
    ## For when HTTPS is added
    try:
        env['HOST_PROTOCOL']
    except KeyError:
        host_protocol = "http"
    ## Sample data to echo
    sample_data = {"kitten_status": "adorable",
                   "puppy_status": "precious"}
    headers = {"Content-Type": "application/json"}
    api_host = f"{host_protocol}://{host_ip}:{host_port}"
    api_path = "/api/echo"
    colors = TextColors()

    print(f"{colors.HEADER}Starting testing{colors.ENDC}")
    ## General connectivity
    print(f"{colors.OKBLUE}Checking endpoint connectivity to: {api_host}{colors.ENDC}")
    ########################
    ## Connection Testing ##
    ########################
    conn_status = check_endpoint_conn(api_host, colors)
    ## What's our status code?
    if conn_status != 200:
            status = "FAIL"
            print(f"{colors.FAIL}Invalid status code form {api_host}. Status code: {conn_status}. Status: [{status}]{colors.ENDC}")
            sys.exit(1)
    elif conn_status == 200:
        status = "PASS"
        print(f"{colors.OKGREEN}Connection to {api_host} success. Status: [{status}]{colors.ENDC}")

    #################
    ## API testing ##
    #################
    print(f"{colors.OKBLUE}Starting API tests{colors.ENDC}")

    ## Content-Type Validation
    content_status = check_content_type(api_host, api_path, colors, sample_data)
    if content_status != 415:
        status = "FAIL"
        print(f"{colors.FAIL}Incorrect status code for non application/json Content-Type header. Status code: {content_status}. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}Correct status code for non application/json Content-Type header. Status code: {content_status} Status: [{status}]{colors.ENDC}")

    ## Method validation POST
    post_status = check_api_method_post(api_host, api_path, colors, sample_data, headers)
    if post_status != 200:
        status = "FAIL"
        print(f"{colors.FAIL}POST method to {api_host}{api_path} failure. Status code: {post_status}. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}POST method to {api_host}{api_path} success. Status: [{status}]{colors.ENDC}")

    ## Method validation PUT
    put_status = check_api_method_put(api_host, api_path, colors, sample_data, headers)
    if put_status != 200:
        status = "FAIL"
        print(f"{colors.FAIL}PUT method to {api_host}{api_path} failure. Status code: {put_status}. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}PUT method to {api_host}{api_path} success. Status: [{status}]{colors.ENDC}")

    ## Method validation GET. Verify that GET is not allowed.
    get_status = check_api_method_get(api_host, api_path, colors, sample_data, headers)
    if get_status != 405:
        status = "FAIL"
        print(f"{colors.FAIL}GET method to {api_host}{api_path} failure. Status code: {get_status}. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}GET method to {api_host}{api_path} disallowed. Status: [{status}]{colors.ENDC}")

    ## Verify that the API echoes correctly
    echo_status = check_echo(api_host, api_path, colors, sample_data, headers)
    if echo_status != True:
        status = "FAIL"
        print(f"{colors.FAIL}Server did not echo test data correctly. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}Server echoed data correctly. Status: [{status}]")

    ## Verify that the API returns a 400 when '"echoed": true"' key is present
    echo_true_status = check_echo_true_status(api_host, api_path, colors, sample_data, headers)
    if echo_true_status != 400:
        status = "FAIL"
        print(f"{colors.FAIL}Server did not return correct error code for previously echoed data. Status code: {echo_true_status} Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}Server returned correct error code for previously echoed data. Status code: {echo_true_status} Status: [{status}]{colors.ENDC}")

    ## Verify that the API does NOT echo the data back when '"echoed": true"' key is present
    echo_true_disallow = check_echo_true_disallow(api_host, api_path, colors, sample_data, headers)
    if echo_true_disallow != True:
        status = "FAIL"
        print(f"{colors.FAIL}Server echoed back previously echoed data. Status: [{status}]{colors.ENDC}")
        sys.exit(1)
    else:
        status = "PASS"
        print(f"{colors.OKGREEN}Server did not echo back previously echoed data. Status: [{status}]{colors.ENDC}")
    ## Check that things are echoed correctly
    #echo_status = check_echo(api_host, api_path, colors, sample_data, headers)
## Here we're just testing that we can connect the server
## and that it is running. We'll terminate if that fails.
def check_endpoint_conn(api_host, colors):
    sleep_time = 0.1
    attempt = 0
    status = ""
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.get(api_host)
            break
        ## It's probably not super clean to terminate the operation from directly
        ## within the function, but here we are.
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Attempt: {attempt} Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    if status == "UNSUCCESSFUL":
        print(f"Terminating after {attempt} connection attempts")
        sys.exit(1)

    return connection.status_code

## We're checking that the framework only accepts GET/PUT methods.
## If anything other than GET/PUT is supported for /api/echo then it's a failure.
def check_api_method_post(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    if status == "UNSUCCESSFUL":
        print(f"Terminating after {attempt} connection attempts")
        sys.exit(1)

    return connection.status_code
## Acceptance criteria, that we can successfully PUT
## Expected status: 200
def check_api_method_put(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.put(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    if status == "UNSUCCESSFUL":
        print(f"Terminating after {attempt} connection attempts")
        sys.exit(1)

    return connection.status_code

## Acceptance criteria, that we CANNOT GET.
## Expected status code: 405
def check_api_method_get(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.get(endpoint)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    if status == "UNSUCCESSFUL":
        print(f"Terminating after {attempt} connection attempts")
        sys.exit(1)

    return connection.status_code
## Verify that our text is echoed correctly
def check_echo(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1
    ## Both conditions must be met
    connection_json = connection.json()
    ## A few more nested 'if's and this will be AI/ML
    try:
        if connection_json['echoed'] == True:
            pass
        else:
            return False
        if connection_json['puppy_status'] == "precious":
            pass
        else:
            return False       
        if connection_json['kitten_status'] == "adorable":
            return True
        else:
            return False
    except:
        return False
        
## Make sure we get the correct HTTP Code when previously echoed data is sent
def check_echo_true_status(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    ## Get our data echoed
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    echoed_data = connection.json()
    ## Send our echoed data back
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=echoed_data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    return connection.status_code

## Make sure that previously echoed data is NOT returned
def check_echo_true_disallow(api_host, api_path, colors, data, headers):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    ## Get our data echoed
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1
    attempt = 0
    sleep_time = 0.1
    echoed_data = connection.json()
    ## Send our echoed data back
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=echoed_data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1
    
    ## If the server works correctly, this should be an HTTP 400
    if connection.status_code == 400 and connection.json() != echoed_data:
        return True
    else:
        return False
## Verify that incorrect Content-Type header is rejected
def check_content_type(api_host, api_path, colors, data):
    endpoint = f"{api_host}{api_path}"
    sleep_time = 0.1
    attempt = 0
    status = ""
    ## Send an incorrect header
    headers = {"Content-Type": "text/html"}
    while attempt < 3:
        try:
            time.sleep(sleep_time)
            connection = httpx.post(endpoint, json=data, headers=headers)
            break
        except:
            status = "UNSUCCESSFUL"
            print(f"{colors.FAIL}Uncuccessful connection. Status: [{status}]")
            sleep_time = sleep_time * 4
            attempt += 1

    return connection.status_code
## Get us some pretty colors!
class TextColors():
    def __init__(self):
        self.HEADER = '\033[95m'
        self.OKBLUE = '\033[94m'
        self.OKGREEN = '\033[92m'
        self.WARN = '\033[93m'
        self.FAIL = '\033[91m'
        self.ENDC = '\033[0m'
        self.BOLD = '\033[1m'
        self.UNDERLINE = '\033[4m'

if __name__ == '__main__':
    main()