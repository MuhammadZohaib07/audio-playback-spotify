import socket
import pygame
import os
import sys
import atexit
import time


class Client:
    def __init__(self, client_id, client_port, bootstrap_address):
        self.client_id = client_id
        self.client_port = client_port
        self.bootstrap_address = bootstrap_address
        self.function_nodes = []
        self.current_function_node_index = 0
        self.client_ip = self.get_client_ip()
        self.available_audio_files = []
        self.bootstrap_ip = None
        self.bootstrap_port = None

    def get_client_ip(self):
        # Get the IP address of the client
        return socket.gethostbyname(socket.gethostname())

    def connect_to_bootstrap_node(self):
        # Connect to the bootstrap node and register the client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(self.bootstrap_address)
            message = f"REGISTER/Client/{self.client_id}/{self.client_ip}/{self.client_port}"
            s.send(message.encode())
            registration_result = s.recv(1024).decode()
            print("Received Function Nodes Info:", registration_result)
            received = registration_result.split("/")
            self.bootstrap_ip = received[1]
            self.bootstrap_port = received[2]
            return received[0]

    def start_menu(self):
        # Display the start menu
        print()
        print("start menu")
        print("enter 1 to login and 2 to sign up")
        choice = input("Enter option: ")
        if choice == "1":
            self.login()
        elif choice == "2":
            self.signup()
        else:
            print("Invalid input try again")
            self.start_menu()

    def login(self):
        # Handle user login
        print()
        print("Login")
        username = input("Username: ")
        password = input("Password: ")
        if username == "" or password == "":
            print("Try again enter values")
            self.login()
        else:
            loginDetails = f"LOGIN/{username}/{password}"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(self.bootstrap_address)
                client_socket.send(loginDetails.encode())

                while True:
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    if response == "Login successful.":
                        self.main_menu()
                    else:
                        print("Invalid login details try again")
                        print()
                        self.start_menu()
                        break

    def signup(self):
        # Handle user signup
        print()
        print("Signup")
        username = input("Username: ")
        password = input("Password: ")
        if username == "" or password == "":
            print("Try again and enter values")
            self.signup()
        else:
            loginDetails = f"SIGNUP/{username}/{password}"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(self.bootstrap_address)
                client_socket.send(loginDetails.encode())

                while True:
                    response = client_socket.recv(1024).decode('utf-8')
                    print(response)
                    if response == "Signup successful.":
                        self.main_menu()
                    else:
                        print("Username already exists try again!!")
                        print()
                        self.start_menu()
                        break

    def main_menu(self):
        # Display the main menu
        print("Main Menu")
        print("Select an option: 1. Get Audio Files. 2. Download Audio File. 3. Play Audio File. 4.Retrieve Info. 5. Logout")
        user_choice = input("Enter choice: ")
        if user_choice == "1":
            self.get_audio_files()
        elif user_choice == "2":
            self.download_audio_file()
        elif user_choice == "3":
            self.play_song()
        elif user_choice == "4":
            self.retrieve_info()
        elif user_choice == "5":
            self.logout()
        else:
            print("input is invalid try again")
            self.main_menu()

    def retrieve_info(self):
        print()
        print(f"Bootstrap connected to information:")
        print(f"Bootstrap IP: {self.bootstrap_ip}")
        print(f"Bootstrap Port: {self.bootstrap_port}")
        print("Press any key to go back to the main menu...")
        input()
        self.main_menu()

    def download_audio_file(self):
        # Download an audio file
        print("Download an audio file")
        print("Available audio files:")
        self.get_downloadable_files()

        try:
            selected_file_index = int(input(
                f"Enter the number corresponding to the audio file you wish to download (1 - {len(self.audio_List)}): ")) - 1
            if 0 <= selected_file_index < len(self.audio_List):
                selected_file = self.audio_List[selected_file_index]

                # Request the selected audio file from the bootstrap server
                request_audio_file = f"GET_AUDIO_FILE/{selected_file}"
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                    client_socket.connect(self.bootstrap_address)
                    client_socket.send(request_audio_file.encode())

                    # Receive the audio file data
                    audio_data = b''
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        audio_data += chunk

                    # Save the received audio file to the directory
                    received_audio_files_directory = "received_audio_files"
                    os.makedirs(received_audio_files_directory, exist_ok=True)  # Create directory if it doesn't exist
                    file_path = os.path.join(received_audio_files_directory, selected_file)
                    with open(file_path, "wb") as audio_file:
                        audio_file.write(audio_data)

                    print(f"Audio file '{selected_file}' downloaded and saved to '{file_path}'")
                    self.download_again_function()
            else:
                print("Invalid audio number.")
                self.download_audio_file()
        except ValueError:
            print("Invalid input  Please enter a valid number.")
            self.download_audio_file()

    def download_again_function(self):
        # Ask user if they want to download another song
        print("Would you like to download another song y for yes or n for no")
        download_again = input("Enter Choice: ")
        if download_again == 'y':
            self.download_audio_file()
        elif download_again == 'n':
            print()
            self.main_menu()
        else:
            print("Invalid input try again...")
            print()
            self.download_audio_file()

    def get_audio_files(self):
        # Get the list of available audio files from the server
        request_files = "GET_AUDIO_FILES/"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(self.bootstrap_address)
            client_socket.send(request_files.encode())
            self.audio_files_data = client_socket.recv(1024).decode('utf-8')
            audioList = self.audio_files_data.split(',')
            print()
            print("Music Received: ")
            for i, file in enumerate(audioList, start=1):
                print(f"{i}. {file}")
            print("press enter to go back to the main menu")
            input()
            time.sleep(1)
            print()
            self.main_menu()

    def get_downloadable_files(self):
        # Get the list of downloadable audio files from the server
        request_files = "GET_AUDIO_FILES/"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(self.bootstrap_address)
            client_socket.send(request_files.encode())

            self.audio_files_data = client_socket.recv(1024).decode('utf-8')
            self.audio_List = self.audio_files_data.split(',')
            for i, file in enumerate(self.audio_List, start=1):
                print(f"{i}. {file}")

    def play_song(self):
        # Play a selected audio file
        self.display_existing_audio_files()

        if not self.audio_files_1:
            print("There are no songs available so taking you back to the main menu.")
            self.main_menu()
            return

        while True:
            try:
                song_index_input = input("Enter the number of the song you would like to play: ")
                if not song_index_input:
                    print("Please enter a number.")
                    continue
                song_index = int(song_index_input) - 1
                if 0 <= song_index < len(self.audio_files_1):
                    song = self.audio_files_1[song_index]
                    self.playSong(song)
                    break  # Exit the loop after successful input
                else:
                    print("Invalid song number. Please enter a number from the available songs list.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")

    def check_audio_files(self, song):
        # Check for available audio files
        audio_files_directory = "audio_files"  # this is my audio file directory
        try:
            # Use os.path.join to properly construct the file path
            audio_files_directory = os.path.join(os.getcwd(), audio_files_directory)
            # Use glob.glob to find files matching the pattern
            self.audio_files = [file for file in os.listdir(audio_files_directory) if file.endswith(song)]
        except FileNotFoundError:
            print(f"Error: Audio files directory '{audio_files_directory}' not found.")

    def display_existing_audio_files(self):
        # Display existing audio files available for playing
        audio_files_directory = "received_audio_files"
        try:
            audio_files_directory = os.path.join(os.getcwd(), audio_files_directory)
            self.audio_files_1 = [file for file in os.listdir(audio_files_directory) if file.endswith(".mp3")]
            if self.audio_files_1:
                print("Available songs:")
                for i, file in enumerate(self.audio_files_1, start=1):
                    print(f"{i}. {file}")
            else:
                print("No audio files found.")
        except FileNotFoundError:
            print(f"Error: Audio files directory '{audio_files_directory}' not found.")

    def playSong(self, song):
        # Play the selected song
        self.check_audio_files(song)
        pygame.mixer.init()
        # Load the first file in the list
        pygame.mixer.music.load(os.path.join("received_audio_files", self.audio_files[0]))
        pygame.mixer.music.play()

        while True:
            user_input = input("Enter p to pause, r to resume and q to quit: ")
            if user_input == 'p':
                self.pause()
                print("paused")
            elif user_input == 'r':
                self.resume()
                print("resumed")
            elif user_input == 'q':
                self.quit()
                print("quited")
                break
            else:
                "input is invalid try again with only p, r, q"
        self.play_again()

    def play_again(self):
        # Ask user if they want to play another song
        print("Would you like to play another song y for yes or n for no?")
        user_entered = input("Enter choice: ")
        if user_entered == 'y':
            self.play_song()
        elif user_entered == 'n':
            self.main_menu()
        else:
            print("Invalid input try again")
            self.play_again()

    def pause(self):
        # Pause the currently playing song
        pygame.mixer.music.pause()

    def resume(self):
        # Resume the currently paused song
        pygame.mixer.music.unpause()

    def quit(self):
        # Quit the currently playing song
        pygame.mixer.music.stop()

    def logout(self):
        # logout the user
        sys.exit()


def cleanup_on_exit():
    # Cleanup resources on exit
    pygame.quit()


if __name__ == "__main__":
    pygame.init()  # Initialize pygame here
    atexit.register(cleanup_on_exit)

    client_id = "Client1"
    client_port = 5000
    bootstrap_address = ("127.0.0.1", 5000)
    client = Client(client_id, client_port, bootstrap_address)

    registration_result = client.connect_to_bootstrap_node()
    print(registration_result)

    if registration_result == "Registration successful":
        client.start_menu()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
