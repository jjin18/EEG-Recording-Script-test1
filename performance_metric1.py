from cortex import Cortex
import time
import numpy as np
from scipy.signal import butter, lfilter

class LiveEEGMetrics():
    """
    A class to show EEG metrics (alpha, beta bands) in real-time from the headset.
    """

    def __init__(self, app_client_id, app_client_secret, **kwargs):
        """Initialize the Cortex connection and bind to EEG data."""
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)  # Bind to EEG data stream
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, profile_name, headsetId=''):
        """Start the live EEG streaming process."""
        if profile_name == '':
            raise ValueError('Profile name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def subscribe_data(self, streams):
        """Subscribe to one or more data streams, in this case 'eeg' for EEG data."""
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
            streams = ['eeg']  # Stream 'eeg' data for brainwave activity
            self.subscribe_data(streams)
        else:
            print(f"Failed to load profile '{self.profile_name}'.")

    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        """Create a bandpass filter for extracting specific frequency bands."""
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        """Apply a bandpass filter to the EEG data."""
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def on_new_eeg_data(self, *args, **kwargs):
        """Handle real-time EEG data and extract alpha/beta band activity."""
        data = kwargs.get('data')
        if data and 'eeg' in data:
            eeg_signals = np.array(data['eeg'])

            # Assuming data is sampled at 128 Hz
            fs = 128  

            # Alpha band (8-13 Hz)
            alpha_band = self.bandpass_filter(eeg_signals, 8.0, 13.0, fs)

            # Beta band (13-30 Hz)
            beta_band = self.bandpass_filter(eeg_signals, 13.0, 30.0, fs)

            # Output the values (you can send this to the front end for visualization)
            print(f"Alpha Band Power: {np.mean(alpha_band**2)}")
            print(f"Beta Band Power: {np.mean(beta_band**2)}")

            # You can format this data for visualization
            self.send_data_to_frontend(alpha_band, beta_band)

    def send_data_to_frontend(self, alpha_band, beta_band):
        """Send alpha and beta band data to your front-end collaborator."""
        # This function can be used to format the data in JSON or another format
        # and send it to the front-end for visualization
        data = {
            'alpha_band': alpha_band.tolist(),
            'beta_band': beta_band.tolist(),
        }
        # You can implement this method to send data via sockets or an API, etc.
        print("Sending data to front-end...")

    def on_inform_error(self, *args, **kwargs):
        """Handle errors emitted from Cortex."""
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']
        print(f"Error {error_code}: {error_message}")

def run_live_eeg_metrics():
    """Run the live streaming of EEG data ('eeg') and extract alpha/beta bands."""
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'

    # Initialize live streaming for EEG data
    live_metrics = LiveEEGMetrics(your_app_client_id, your_app_client_secret)

    # Set the profile name of a trained profile
    trained_profile_name = 'trainingtest1'
    live_metrics.start(trained_profile_name)

    try:
        # Keep streaming data until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping the live EEG metrics stream.")
        live_metrics.c.close()  # Gracefully close the Cortex connection

if __name__ == '__main__':
    run_live_eeg_metrics()

