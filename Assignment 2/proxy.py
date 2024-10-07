
import socket
import threading
import re
class Proxy: 
    def __init__(self, host : str, port : int):
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(0)
        self.start_proxy_server()
        
    def start_proxy_server(self):
        while True:
            (client_socket, addr) = self.socket.accept()
            print(f"Connected to {addr}")
            client_thread = threading.Thread(target=self.client, args=(client_socket, addr))
            client_thread.start()

    def client(self, client_socket, addr): 
        print("Started new thread for browser, connection is active")
    
        request : bytes = client_socket.recv(4096)

        header : bytes = get_header(request)
        str_header = header.decode()
        print("Header: \n"+str_header)

        server_hostname = getDestination(str_header)
        server_addr = socket.gethostbyname(server_hostname)
        print(f"IP-address of the server(website) is {server_addr}")
        
        # Connect to the server (website), and start new thread for server.
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_addr, 80))
        
        response = self.server(server_socket, request)
        
        client_socket.sendall(response)
        
        client_socket.close()
        print("--------------------connection closed-------------------")

    def server(self, web_socket, message) -> bytes: 
        
        header = get_header(message)
        if "smiley.jpg" in getreqmessage(header.decode()):
            print("trolley is coming!!!")
            header = changegetmessage(header.decode(), "smiley.jpg", "trolly.jpg").encode()
            message = header

        web_socket.sendall(message)
        
        response = b''

        data = web_socket.recv(4096)

        header = get_header(data)
        header_as_string = header.decode()
        print(header_as_string)
        content_size = contentsize(header_as_string)

        received_content_size = len(data) - len(header)
        response += data
        while received_content_size < content_size:
            data = web_socket.recv(4096)
            received_content_size += len(data)
            response += data

        header_as_string = header.decode()
        if contenttype(header_as_string) == "text":
            content = response[len(header)-1:-1].decode()
            print("--------------------------altering content----------------------------")
            content, count = alterdata(content, " Stockholm", " Linköping")
            content, count = alterdata(content, " smiley", " trolly")
            content, count = alterdata(content, " Smiley", " Trolly")


            header_as_string = changecontentsize(header_as_string, count)
            response = (header_as_string+content).encode()
        
        web_socket.close()
        return response

def get_header(chunk : bytes) -> bytes:
    pattern = re.compile(b"\r\n\r\n")

    header_and_content : list = re.split(pattern, chunk, 1)
    header = header_and_content[0]
    header += "\r\n\r\n".encode("utf-8")
    return header

def getDestination(request : str) -> str:
    lines = request.split("\r\n")
    for line in lines:
        if "host: " in line.lower():
            return line.split(": ")[1]
    return ""

def getStatus(request : str) -> bool:
    lines = request.split("\r\n")
    for line in lines:
        if "proxy-connection: " in line.lower() or "connection: " in line.lower():
            return line.split(": ")[1].lower() == "keep-alive"
    return False

def contentsize(content : str):
    lines = content.split("\r\n")
    for line in lines:
        if "content-length: " in line.lower():
            return int(line.split(": ")[1])
    return 0
    
def changecontentsize(content : str, size_change) -> str:
    lines = content.split("\r\n")
    for line in lines:
        if "content-length: " in line.lower():
            curr = int(line.split(": ")[1])
            new_line = "Content-Length: "+str(size_change+curr)
            content = content.replace(line, new_line)
            return content
    return content

def getreqmessage(content : str) -> str:
    lines = content.split("\r\n")
    for line in lines:
        if "GET" in line:
            return line.split(" ")[1]
    return ""

def contenttype(content : str) -> str: 
    lines = content.split("\r\n")
    for line in lines:
        if "content-type: " in line.lower():
            return line.split(": ")[1].split("/")[0]
    return ""

def alterdata(response: str, old_name : str, new_name : str) -> tuple[str, int]:
    apperances = response.count(old_name)
    return response.replace(old_name, new_name), apperances

def changegetmessage(response : str, old_name, new_name):
    lines = response.split("\r\n")
    for line in lines:
        if "GET " in line:
            new_line = line.replace(old_name, new_name)
            response = response.replace(line, new_line)
            return response
    return response


if __name__ == '__main__':
    proxy = Proxy('localhost', 54321)