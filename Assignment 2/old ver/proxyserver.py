import socket
import proxyclient

PORTNR = 54321


def proxyserverstart():
    """
    initiates proxy server, starts listening
    """
    server_socket = socket.socket()

    server_socket.bind(('127.0.0.1', PORTNR))
    server_socket.listen(5)
    print(f"server listening on port {PORTNR}")

    while True: 

        client_sock, address = server_socket.accept()
        request = client_sock.recv(4096)

        print("BROWSER REQ:")
        print(request)
        print("--------------------------------")

        request_socket = proxyclient.proxyClientSendRequest(request)
        send_data(request_socket, client_sock)


        client_sock.close()
        print("closed connection")

def send_data(fro, to):
    

    chunk = proxyclient.get_server_chunk(fro)
    print(f'chunk = \n\n <{chunk}>\n\n')
    cont_type_pos = chunk.lower().find("content-type:") 
    print(f"content type pos = {cont_type_pos}")   
    cont_type = chunk[cont_type_pos:].split()[1].split("/")[0]
    print(f'content type = {cont_type}')

    temp=""
    
    while True:
        if len(chunk) == 0:
            print("chunk is empty")
            break
        if cont_type != "image":
            out, temp = proxyclient.proxyClientAlterCont(chunk, temp)
            
            to.send(out.encode('utf-8'))
        else:
            to.send(chunk.encode('utf-8'))
        chunk = proxyclient.get_server_chunk(fro)

    to.send((" " + temp).encode('utf-8'))



proxyserverstart()