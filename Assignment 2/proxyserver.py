import socket
import proxyclient

PORTNR = 54321

# receive server request from (user) client

# print request

# (debug) return some value

# send request to (proxy) client

def proxyserverstart():
    """
    initiates proxy server, starts listening
    """
    server_sock = socket.socket()

    server_sock.bind(('127.0.0.1', PORTNR))
    server_sock.listen(5)
    print("server listening")

    while True: 
        client_sock, addr = server_sock.accept()
        request = client_sock.recv(4096)

        print("BROWSER REQ:")
        print(request)

        request_socket = proxyclient.proxyClientSendRequest(request)
        send_data(request_socket, client_sock)


        client_sock.close()
        print("closed connection")

def send_data(fro, to):
    

    chunk = proxyclient.get_server_chunk(fro)

    cont_type_pos = chunk.lower().find("content-type:")
    cont_type = chunk[cont_type_pos:].split()[1].split("/")[0]
    temp=""
    while len(chunk) != 0:
        if cont_type != "image":
            out, temp = proxyclient.proxyClientAlterCont(chunk, temp)
            to.send(out)
        else:
            to.send(chunk)
        chunk = proxyclient.get_server_chunk(fro)

    to.send(" " + temp)



proxyserverstart()