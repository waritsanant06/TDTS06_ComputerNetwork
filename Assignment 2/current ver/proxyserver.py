
import socket
import proxyclient
import threading

PORTNR = 54321
BUFFER_SIZE = 4096

def handle_client(client_sock):
    """
    Handles the client connection and forwards request to the server
    """
    try:
        request = client_sock.recv(BUFFER_SIZE)
        print("BROWSER REQ:")
        print(request)
        print("--------------------------------")

        request_socket = proxyclient.proxyClientSendRequest(request)
        if request_socket:
            response = proxyclient.get_server_chunk(request_socket)
            altered_response = proxyclient.proxyClientAlterCont(response)
            client_sock.sendall(altered_response.encode('utf-8'))
        else:
            print("Failed to forward request to server")
    except Exception as e:
        print(f"Error handling client request: {e}")
    finally:
        client_sock.close()
        print("Closed connection")

def proxyserverstart():
    """
    Initiates proxy server, starts listening and handles multiple clients
    """
    server_socket = socket.socket()
    server_socket.bind(('127.0.0.1', PORTNR))
    server_socket.listen(5)
    print(f"Server listening on port {PORTNR}")

    while True:
        client_sock, address = server_socket.accept()
        print(f"Accepted connection from {address}")
        
        # Create a new thread to handle the client request
        client_thread = threading.Thread(target=handle_client, args=(client_sock,))
        client_thread.start()


proxyserverstart()