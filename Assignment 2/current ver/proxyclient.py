import socket
import re

PORT = 80
BUFFER_SIZE = 8192  

def proxyClientSendRequest(request): #Forwards HTTP request to the internet and alters the request URL and content if necessary
    
    request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    request_socket.settimeout(10)  # Set a timeout to prevent hanging

    request_str = request.decode()

    print(f"request = {request_str}")

    host_pos = request_str.lower().find("host:")
    host = request_str[host_pos:].split()[1].split(":")[0]

    try:
        # Forward the modified request to the original host
        request_socket.connect((host, PORT))
        request_socket.sendall(request_str.encode())
        return request_socket
    except Exception as e:
        print(f"Error forwarding request: {e}")
        request_socket.close()
        return None


def get_server_chunk(socket): # Receives a response from the server and handles chunked transfer encoding and encoding issues

    response_data = b""
    try:
        while True:
            chunk = socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            response_data += chunk

        # Detect if the response is chunked (Transfer-Encoding: chunked)
        if b"transfer-encoding: chunked" in response_data.lower():
            return decode_chunked_response(response_data)
        else:
            return response_data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error receiving data from server: {e}")
        return ""

def decode_chunked_response(response_data): # Decodes chunked response data and assembles the full response

    response_str = response_data.decode('utf-8', errors='ignore')  # Decode the full response ignoring errors for now
    headers, body = response_str.split("\r\n\r\n", 1)  # Split headers and body
    decoded_body = ""

    chunk_size = -1
    while chunk_size != 0:
        chunk_size_hex, rest = body.split("\r\n", 1)
        chunk_size = int(chunk_size_hex, 16)
        chunk_data = rest[:chunk_size]
        decoded_body += chunk_data
        body = rest[chunk_size+2:]  # Skip the chunk data and the following \r\n

    return headers + "\r\n\r\n" + decoded_body


def proxyClientAlterCont(response): # make fake news

    print("Altering content...")

    # Split the HTTP response into headers and body
    header_end_pos = response.find("\r\n\r\n")
    if header_end_pos == -1:
        print("Malformed response")
        return response

    headers = response[:header_end_pos]
    body = response[header_end_pos + 4:]  # +4 to skip the \r\n\r\n separator

    def replace_outside_img_tags(match):
        text = match.group(0)
        text = text.replace("Stockholm", "Linköping")
        return text

    altered_body = re.sub(r'>([^<]+)<', replace_outside_img_tags, body) # change the Stockholm -> Linkoping only not in the image tag
    altered_body = altered_body.replace("smiley", "trolly").replace("Smiley", "Trolly") # change smiley-> trolly every where

    # Update Content-Length in the headers if present
    headers = update_content_length(headers, altered_body)

    # Combine the headers and altered body
    new_response = headers + "\r\n\r\n" + altered_body

    return new_response


def update_content_length(headers, altered_body): # Updates the Content-Length header based on the new altered body length


    content_length_pos = headers.lower().find("content-length:")
    if content_length_pos != -1:
        # Extract the original Content-Length
        original_length_start = content_length_pos + len("content-length:")
        original_length_end = headers.find("\r\n", original_length_start)
        original_length = headers[original_length_start:original_length_end].strip()

        # Calculate the new length based on the altered body (in bytes)
        new_length = len(altered_body.encode('utf-8'))

        # Replace the original Content-Length with the new length
        headers = headers[:original_length_start] + f" {new_length}" + headers[original_length_end:]

        print(f"Updated Content-Length from {original_length} to {new_length}")

    return headers
