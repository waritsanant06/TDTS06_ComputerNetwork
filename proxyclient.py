import socket

TEST_SERVER = "http://zebroid.ida.liu.se/fakenews/test1.txt"

PORT = 80

def proxyClientSendRequest(request):
    """
    forwards http request to internet
    """
    request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    request_str = request.decode()
    host_pos = request_str.lower().find("host:")
    host = request_str[host_pos:].split()[1].split(":")[0]


    ip = socket.gethostbyname(host)


    #connect socket to requested url
    request_socket.connect((ip, PORT))
    
    request_socket.send(request)
    return request_socket


def get_server_chunk(socket):

    chunk = socket.recv(2048)

    print("SERVER RESPONSE:")
    print(chunk)

    return chunk


def proxyClientAlterCont(response, trailing_chars=""):
    """
    insert fake news
    """
    
    new_response = trailing_chars + response
    new_response = new_response.replace("Stockholm", "Linkoping")

    new_response = new_response.replace("smiley", "trolly")
    new_response = new_response.replace("Smiley", "Trolly")

    new_response = new_response.split(" ")
    new_trailing_chars = new_response[-1]

    del new_response[-1]
    new_response = b' '.join(new_response)

    return new_response, new_trailing_chars
