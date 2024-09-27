import socket

PORT = 80

def proxyClientSendRequest(request):
    """
    Forwards HTTP request to the internet
    """
    request_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    request_str = request.decode()
    host_pos = request_str.lower().find("host:")
    host = request_str[host_pos:].split()[1].split(":")[0]

    ip = socket.gethostbyname(host)

    # Connect socket to the requested URL
    request_socket.connect((ip, PORT))
    request_socket.send(request)
    return request_socket


def get_server_chunk(socket):
    """
    Receives a chunk from the server and decodes it
    """
    chunk = socket.recv(2048).decode('utf-8')
    
    print("SERVER RESPONSE:")
    print(chunk)
    print("--------------------------------")
    
    return chunk


def proxyClientAlterCont(response, trailing_chars=""):
    """
    Alters the content of the response and updates Content-Length header
    """

    print("Altering content...")

    # Split the HTTP response into headers and body
    header_end_pos = response.find("\r\n\r\n")
    headers = response[:header_end_pos]
    body = response[header_end_pos + 4:]  # +4 to skip the \r\n\r\n separator

    # Perform content replacements in the body
    altered_body = body.replace("Stockholm", "Linköping").replace("smiley", "trolly").replace("Smiley", "Trolly")

    # Update Content-Length in the headers if present
    headers = update_content_length(headers, altered_body)

    # Combine the headers and altered body
    new_response = headers + "\r\n\r\n" + altered_body

    # Return the altered response and trailing characters (if any)
    return new_response, trailing_chars


def update_content_length(headers, altered_body):
    """
    Updates the Content-Length header based on the new altered body length
    """
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
