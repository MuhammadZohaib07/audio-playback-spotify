import socket
import threading
import os


class BootstrapNode:
    def __init__(self):
        # Initialize a list to store function nodes
        self.function_nodes = []
        # Define the server address
        self.server_address = ("127.0.0.1", 5000)
        self.bootstrap_ip = "127.0.0.1"
        self.bootstrap_port = 5000

        # Create a socket to listen for incoming connections
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen()

        # Start a thread to handle incoming connections
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        # Function to accept incoming connections
        print("Bootstrap Node is listening for incoming connections...")
        try:
            while True:
                connection, address = self.server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(connection, address)).start()
        finally:
            self.server_socket.close()  # Close the server socket when done

    def handle_connection(self, connection, address):
        # Function to handle incoming connections
        try:
            data = connection.recv(1024).decode()
            print("Received data from client:", data)

            data_split = data.split('/')

            if len(data_split) > 0:
                if data_split[0] == "REGISTER":
                    # If registration request received
                    entity_type = data_split[1]
                    name = data_split[2]
                    ip = data_split[3]
                    port = data_split[4]
                    self.register_function_node(entity_type, name, ip, port)
                    print(f"Function Node {name} registered. Available Function Nodes: {self.function_nodes}")
                    connection.send(f"Registration successful/{self.bootstrap_ip}/{self.bootstrap_port}".encode())
                elif data_split[0] == "GET_AUDIO_FILES":
                    # If request for audio files received
                    audio_files = self.get_audio_files()
                    audio_files_data = ",".join(audio_files)
                    connection.send(audio_files_data.encode())  # Send the list of audio files to the client
                elif data_split[0] == "GET_AUDIO_FILE" and len(data_split) == 2:
                    # If request for a specific audio file received
                    file_name = data_split[1]
                    self.send_audio_file(connection, file_name)
                elif data_split[0] == 'LOGIN':
                    # If login request received
                    print(data_split[1])
                    print(data_split[2])
                    self.handle_login(connection, data_split[1], data_split[2])
                elif data_split[0] == 'SIGNUP':
                    # If signup request received
                    self.handle_signup(connection, data_split[1], data_split[2])
                else:
                    print("Invalid data received.")
            else:
                print("Invalid data received.")
        finally:
            connection.close()  # Close the client connection

    def register_function_node(self, entity_type, name, ip, port):
        # Function to register a function node
        self.function_nodes.append({"type": entity_type, "name": name, "ip": ip, "port": port})
        return "Registration successful."

    def get_audio_files(self):
        # Retrieve the list of available audio files from the storage directory
        audio_files_directory = "audio_files"  # directory where I have audio files
        audio_files = []
        try:
            audio_files = [file for file in os.listdir(audio_files_directory) if file.endswith(".mp3")]
        except FileNotFoundError:
            print(f"Error: Audio files directory '{audio_files_directory}' not found.")
        return audio_files

    def send_audio_file(self, connection, file_name):
        # Function to send the requested audio file to the client
        audio_files_directory = "audio_files"  # directory where I have audio files
        file_path = os.path.join(audio_files_directory, file_name)
        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                connection.send(audio_data)
        except FileNotFoundError:
            print(f"Error: Audio file '{file_name}' not found.")

    def handle_login(self, connection, username, password):
        # Function to handle user login
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    stored_username, stored_password = line.strip().split(":")
                    if username == stored_username and password == stored_password:
                        connection.send("Login successful.".encode())  # Send login success message
                        return
            connection.send("Login failed.".encode())  # Send login failure message
        except Exception as e:
            print(f"Error checking credentials: {e}")
            connection.send("Error during login.".encode())

    def handle_signup(self, connection, username, password):
        # Function to handle user signup
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    stored_username, _ = line.strip().split(":")
                    if username == stored_username:
                        connection.send("Username already exists.".encode())
                        return
            with open("users.txt", "a") as file:
                file.write(f"{username}:{password}\n")
                connection.send("Signup successful.".encode())
        except Exception as e:
            print(f"Error registering user: {e}")
            connection.send("Error during signup.".encode())


if __name__ == "__main__":
    bootstrap_node = BootstrapNode()

    while True:
        pass  # Keep the Bootstrap Node running
