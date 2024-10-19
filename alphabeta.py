import asyncio
import websockets
import json
from cortex import Cortex
import time
import numpy as np
from scipy.signal import butter, lfilter

class LiveEEGMetrics():
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)
        self.c.bind(inform_error=self.on_inform_error)
        self.ws_connection = None  # WebSocket connection

    def start(self, profile_name, headsetId=''):
        if profile_name == '':
            raise ValueError('Profile name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def subscribe_data(self, streams):
        self.c.sub_request(streams)

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
            streams = ['eeg']
            self.subscribe_data(streams)
        else:
            print(f"Failed to load profile '{self.profile_name}'.")

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    async def send_data(self, alpha, beta):
        if self.ws_connection:
            data = json.dumps({
                "alpha": alpha,
                "beta": beta
            })
            await self.ws_connection.send(data)

    def on_new_eeg_data(self, *args, **kwargs):
        data = kwargs.get('data')
        if data and 'eeg' in data:
            eeg_signals = np.array(data['eeg'])

            # Assuming data is sampled at 128 Hz
            fs = 128

            # Alpha band (8-13 Hz)
            alpha_band = self.bandpass_filter(eeg_signals, 8.0, 13.0, fs)

            # Beta band (13-30 Hz)
            beta_band = self.bandpass_filter(eeg_signals, 13.0, 30.0, fs)

            # Compute band powers
            alpha_power = np.mean(alpha_band ** 2)
            beta_power = np.mean(beta_band ** 2)

            # Print to console for debugging
            print(f"Alpha Band Power: {alpha_power}")
            print(f"Beta Band Power: {beta_power}")

            # Send data to front end via WebSocket
            asyncio.run(self.send_data(alpha_power, beta_power))

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']
        print(f"Error {error_code}: {error_message}")

async def websocket_handler(websocket, path):
    live_metrics.ws_connection = websocket  # Assign WebSocket connection
    await websocket.recv()  # Keep connection alive

def run_live_eeg_metrics():
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'

    # Initialize live streaming for EEG data
    global live_metrics
    live_metrics = LiveEEGMetrics(your_app_client_id, your_app_client_secret)

    # Start the Cortex EEG streaming
    trained_profile_name = 'trainingtest1'
    live_metrics.start(trained_profile_name)

    # Start WebSocket server
    start_server = websockets.serve(websocket_handler, "localhost", 8765)

    # Run WebSocket server and Cortex connection in parallel
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    run_live_eeg_metrics()
