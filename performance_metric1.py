from cortex import Cortex
import time
import random
from pythonosc import osc_message_builder
from pythonosc import udp_client
import openai
import ast
from dotenv import load_dotenv
import os


openai.api_key = "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"

# Read the text file
with open('music_generation_prompt.txt', 'r') as file:
    prompt = file.read()

# Create an OSC client to send messages to Sonic Pi
ip = "127.0.0.1"  # Change to the IP address of your Sonic Pi server if needed
port = 4560  # Default Sonic Pi OSC port
client = udp_client.SimpleUDPClient(ip, port)

class LivePerformanceMetrics():
    """
    A class to show performance metrics (eng, exc, str, etc.) in real-time from the headset.
    """

    def __init__(self, app_client_id, app_client_secret, **kwargs):
        """Initialize the Cortex connection and bind to performance metrics data."""
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(new_met_data=self.on_new_met_data)  # Bind to performance metrics stream
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, profile_name, headsetId=''):
        """
        Start the live performance metrics streaming process.

        Parameters
        ----------
        profile_name : string, required
            name of the profile
        headsetId: string, optional
            ID of the headset you want to work with. If empty, the first available headset will be used
        """
        if profile_name == '':
            raise ValueError('Profile name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def subscribe_data(self, streams):
        """
        Subscribe to one or more data streams, in this case, 'met' for performance metrics.

        Parameters
        ----------
        streams : list, required
            List of streams to subscribe to, for example ['met'] for performance metrics.
        """
        self.c.sub_request(streams)

    # Callbacks
    def on_create_session_done(self, *args, **kwargs):
        print('Session created successfully.')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        profile_lists = kwargs.get('data')
        if self.profile_name in profile_lists:
            print(f"Profile '{self.profile_name}' exists. Loading profile.")
            self.c.get_current_profile()
        else:
            print(f"Profile '{self.profile_name}' does not exist. Creating profile.")
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        if is_loaded:
            print(f"Profile '{self.profile_name}' loaded successfully.")
            streams = ['met']  # Only stream 'met' (performance metrics) data
            self.subscribe_data(streams)
        else:
            print(f"Failed to load profile '{self.profile_name}'.")

    def on_new_met_data(self, *args, **kwargs):
        """
        Handle real-time performance metrics data emitted from Cortex.

        Parameters
        ----------
        kwargs : dict
            Contains the performance metrics data
        """
        data = kwargs.get('data')
        if data and 'met' in data:
            metrics = data['met']
            print(f"\nPerformance Metrics at {time.strftime('%H:%M:%S')}")

            # Output the values for different metrics
            try:
                print(f"Engagement: {metrics[1]}")
                print(f"Excitement: {metrics[3]}")
                print(f"Long-term Excitement (lex): {metrics[5]}")
                print(f"Stress: {metrics[7]}")
                print(f"Relaxation: {metrics[9]}")
                print(f"Interest: {metrics[11]}")
                print(f"Focus: {metrics[13]}\n")
            except IndexError:
                print("Insufficient metrics data received.")

    def on_inform_error(self, *args, **kwargs):
        """Handle errors emitted from Cortex."""
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']
        print(f"Error {error_code}: {error_message}")


def run_live_performance_metrics():
    """
    Run the live streaming of performance metrics data ('met') and output it in real-time.
    """
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'

    # Initialize live streaming for performance metrics
    # live_metrics = LivePerformanceMetrics(your_app_client_id, your_app_client_secret)

    # Set the profile name of a trained profile
    # trained_profile_name = 'trainingtest1'
    # live_metrics.start(trained_profile_name)

    try:
        # Keep streaming data until interrupted
        # while True:
        #     time.sleep(1)  # Sleep to avoid busy waiting
        

        time_elapsed = 0;
        eeg_interval = 0.5
        regenerate_time = 2  # Regenerate music every 2 seconds

        eeg_data = []
        notes = []

        # Simulate sending live EEG data
        while True:

            # Get EEG data from the headset (for now, get an array of random [excitement, relaxation, stress, focus] values)
            eeg_data.append([random.randint(0, 100) for _ in range(4)])

            # If you're at regenerate_time seconds, request from Gemini
                # Send a list of a bunch of chronological snapshops of EEG data 
                # Send previous the list of notes
            if (time_elapsed == regenerate_time):

                response = openai.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": prompt,
                    }],
                    model="gpt-4o",
                )

                # Once you get the notes, you can send it to Sonic Pi to generate music
                # Format: List of [instrument, delay, duration, note, volume] e.g. ['piano', 0.1, 1, 'C', 1]
                # notes = ast.literal_eval(response.choices[0].message.content)
                
                notes = [['piano', 0.1, 1, 'C', 1], ['pluck', 0.1, 1, 'D', 1], ['piano', 0.1, 1, 'E', 1], ['pluck', 0.1, 1, 'F', 1], ['piano', 0.1, 1, 'G', 1], ['pluck', 0.1, 1, 'A', 1], ['piano', 0.1, 1, 'B', 1], ['pluck', 0.1, 1, 'C', 1]]
                
                # Flatten the array by adding "START" marker to denote sub-arrays
                flattened_data = []
                for sub_array in notes:
                    flattened_data.append("START")  # Marker for start of each sub-array
                    flattened_data.extend(sub_array)  # Add the sub-array elements

                print(flattened_data)
                # flattened_data = ['START', 'piano', 0, 0.5, 'C4', 0.4, 'START', 'pluck', 0, 0.4, 'E5', 0.35, 'START', 'saw', 0, 0.6, 'C3', 0.3, 'START', 'fm', 0.5, 0.5, 'G4', 0.4, 'START', 'pluck', 0.5, 0.3, 'B5', 0.35, 'START', 'saw', 0.5, 0.4, 'G3', 0.3, 'START', 'piano', 0.5, 0.4, 'A4', 0.4, 'START', 'pluck', 0.5, 0.3, 'C6', 0.35, 'START', 'saw', 0.5, 0.4, 'A3', 0.3, 'START', 'fm', 0.5, 0.5, 'F4', 0.4, 'START', 'pluck', 0.5, 0.3, 'A5', 0.35, 'START', 'saw', 0.5, 0.5, 'F3', 0.3, 'START', 'dark_ambience', 0, 0.5, 'C3', 0.2, 'START', 'dark_ambience', 1, 0.5, 'G2', 0.2, 'START', 'dark_ambience', 1, 0.5, 'A2', 0.2, 'START', 'dark_ambience', 1, 0.5, 'F2', 0.2, 'START', 'noise', 1, 0.3, 'C2', 0.3]
                
                # Send EEG value as an OSC message
                client.send_message("/synth", flattened_data)

                time_elapsed = 0
                eeg_data = []
            
            # Send data at intervals (adjust as needed)
            time.sleep(eeg_interval)  # Adjust the sleep time for your needs
            time_elapsed += eeg_interval


    except KeyboardInterrupt:
        print("Stopping the live performance metrics stream.")
        # live_metrics.c.close()  # Gracefully close the Cortex connection

if __name__ == '__main__':
    run_live_performance_metrics()
