import socket
import threading
import re

# main function
class Proxy:
    def __init__(self, host: str, port: int): #setup
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates a socket for TCP communication
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allows the reuse of local addresses
        self.socket.bind((host, port))  # Binds the socket to the specified host and port
        self.socket.listen(0)  # Listens for incoming connections
        self.start_proxy_server()  # Starts the proxy server

    def start_proxy_server(self): #main loop
       
        while True:
            (client_socket, addr) = self.socket.accept()  # Accepts a new client connection
            print(f"Connected to {addr}")
            client_thread = threading.Thread(target=self.client, args=(client_socket, addr))  # Starts a new thread to handle the client
            client_thread.start()

    def client(self, client_socket, addr): #act as a client
        
        print("Started new thread for browser, connection is active")
    
        request: bytes = client_socket.recv(4096)  # Receives the client's request (up to 4096 bytes)

        header: bytes = get_header(request)  # Extracts the HTTP header from the client's request
        str_header = header.decode()  # Decodes the header into a string
        print("Header: \n" + str_header)

        # Extract the destination server's hostname from the header and resolve its IP address
        server_hostname = getDestination(str_header)
        server_addr = socket.gethostbyname(server_hostname)
        print(f"IP-address of the server(website) is {server_addr}")

        # Connect to the destination server (website)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_addr, 80))

        # Send the client's request to the server and receive the server's response
        response = self.server(server_socket, request)
        
        # Send the server's response back to the client
        client_socket.sendall(response)
        client_socket.close()  # Close the connection with the client
        print("--------------------connection closed-------------------")

    def server(self, web_socket, message) -> bytes: #forward message to the server + altering data if needed
       
        header = get_header(message)
        if "smiley.jpg" in getreqmessage(header.decode()):  # Checks if the request is for "smiley.jpg"
            print("trolley is coming!!!")
            header = changegetmessage(header.decode(), "smiley.jpg", "trolly.jpg").encode()  # Changes the requested image
            message = header

        web_socket.sendall(message)  # Sends the modified request to the server
        
        response = b''  
        data = web_socket.recv(4096)
        header = get_header(data)  # Extract the header from the response
        header_as_string = header.decode()
        print(header_as_string)
        content_size = contentsize(header_as_string)  # Get the content length from the header

        received_content_size = len(data) - len(header)  # Calculate the initial size of the received content
        response += data  # Append the received data to the response

        # Continue receiving data until the entire content is received
        while received_content_size < content_size:
            data = web_socket.recv(4096)
            received_content_size += len(data)
            response += data

        # If the content is text, modify specific parts of the response
        if contenttype(header_as_string) == "text":
            content = response[len(header)-1:-1].decode()
            print("--------------------------altering content----------------------------")
            content, count = alterdata(content, " Stockholm", " Linköping")
            content, count = alterdata(content, " smiley", " trolly")
            content, count = alterdata(content, " Smiley", " Trolly")

            header_as_string = changecontentsize(header_as_string, count)  # Adjust content-length header
            response = (header_as_string + content).encode()

        web_socket.close()  # Close the connection with the server
        return response

# support funtion(tools for code above)
def get_header(chunk: bytes) -> bytes: # get the header from the chunk data
    
    pattern = re.compile(b"\r\n\r\n")
    header_and_content: list = re.split(pattern, chunk, 1)
    header = header_and_content[0]
    header += "\r\n\r\n".encode("utf-8")
    return header

def getDestination(request: str) -> str: #get destination server
    
    lines = request.split("\r\n")
    for line in lines:
        if "host: " in line.lower():
            return line.split(": ")[1]
    return ""

def contentsize(content: str): #get content size
   
    lines = content.split("\r\n")
    for line in lines:
        if "content-length: " in line.lower():
            return int(line.split(": ")[1])
    return 0

def changecontentsize(content: str, size_change) -> str: #change content size due to the ö
   
    lines = content.split("\r\n")
    for line in lines:
        if "content-length: " in line.lower():
            curr = int(line.split(": ")[1])
            new_line = "Content-Length: " + str(size_change + curr)
            content = content.replace(line, new_line)
            return content
    return content

def getreqmessage(content: str) -> str: # get request message
    
    lines = content.split("\r\n")
    for line in lines:
        if "GET" in line:
            return line.split(" ")[1]
    return ""

def contenttype(content: str) -> str: #get content type for further altering content
    
    lines = content.split("\r\n")
    for line in lines:
        if "content-type: " in line.lower():
            return line.split(": ")[1].split("/")[0]
    return ""

def alterdata(response: str, old_name: str, new_name: str) -> tuple[str, int]:#replace data
    
    appearances = response.count(old_name)
    return response.replace(old_name, new_name), appearances

def changegetmessage(response: str, old_name, new_name): #replace data in GET message
   
    lines = response.split("\r\n")
    for line in lines:
        if "GET " in line:
            new_line = line.replace(old_name, new_name)
            response = response.replace(line, new_line)
            return response
    return response

#-------------------------------------------------------------------------------------------

if __name__ == '__main__':
    proxy = Proxy('localhost', 54321)  # Starts the proxy on localhost and port 54321
