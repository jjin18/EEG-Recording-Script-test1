from cortex import Cortex
import time

class Record():
    def __init__(self, app_client_id, app_client_secret, license_key=None, **kwargs):
        """
        Initializes the Cortex object with the provided app client ID, client secret, and optional license key.
        Binds callback functions to handle various Cortex events.

        Parameters
        ----------
        app_client_id : str
            Application client ID.
        app_client_secret : str
            Application client secret.
        license_key : str, optional
            License key, required for certain features.
        """
        if license_key:
            self.c = Cortex(app_client_id, app_client_secret, license=license_key, debug_mode=False, **kwargs)
        else:
            self.c = Cortex(app_client_id, app_client_secret, debug_mode=False, **kwargs)
        
        # Bind Cortex event handlers to class methods
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(create_record_done=self.on_create_record_done)
        self.c.bind(stop_record_done=self.on_stop_record_done)
        self.c.bind(warn_record_post_processing_done=self.on_warn_record_post_processing_done)
        self.c.bind(export_record_done=self.on_export_record_done)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, record_duration_s=20, headsetId=''):
        """
        Starts the process of data recording and exporting.

        Parameters
        ----------
        record_duration_s: int, optional
            Duration of the recording. Default is 20 seconds.
        headsetId: str, optional
            ID of the desired headset. If empty, the first available headset will be used.
        """
        self.record_duration_s = record_duration_s

        if headsetId:
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def create_record(self, record_title, **kwargs):
        """
        Creates a new recording session.

        Parameters
        ----------
        record_title : str
            Title of the recording.
        """
        self.c.create_record(record_title, **kwargs)

    def stop_record(self):
        """Stops the ongoing recording session."""
        self.c.stop_record()

    def export_record(self, folder, stream_types, format, record_ids, version, **kwargs):
        """
        Exports the recorded data.

        Parameters
        ----------
        folder : str
            Path where the exported file will be saved.
        stream_types : list
            List of data types to export, e.g., ['EEG', 'MOTION'].
        format : str
            File format to export (e.g., 'EDF', 'CSV').
        record_ids : list
            List of record IDs to export.
        version : str
            Version of the export format.
        """
        self.c.export_record(folder, stream_types, format, record_ids, version, **kwargs)

    def wait(self, record_duration_s):
        """Waits during the recording for the specified duration."""
        print('Start recording -------------------------')
        length = 0
        while length < record_duration_s:
            print(f'Recording at {length} seconds')
            time.sleep(1)
            length += 1
        print('End recording -------------------------')

    # Callback: Session creation done
    def on_create_session_done(self, *args, **kwargs):
        print('Session creation done')
        # Create a record
        self.create_record(self.record_title, description=self.record_description)

    # Callback: Record creation done
    def on_create_record_done(self, *args, **kwargs):
        data = kwargs.get('data')
        self.record_id = data['uuid']
        start_time = data['startDatetime']
        title = data['title']
        print(f'Record created: ID={self.record_id}, Title={title}, Start Time={start_time}')
        
        # Wait for the recording duration
        self.wait(self.record_duration_s)

        # Stop the recording
        self.stop_record()

    # Callback: Recording stopped
    def on_stop_record_done(self, *args, **kwargs):
        data = kwargs.get('data')
        record_id = data['uuid']
        start_time = data['startDatetime']
        end_time = data['endDatetime']
        title = data['title']
        print(f'Record stopped: ID={record_id}, Title={title}, Start Time={start_time}, End Time={end_time}')

    # Callback: Post-processing warning
    def on_warn_record_post_processing_done(self, *args, **kwargs):
        data = kwargs.get('data')
        record_id = data.get('recordId')
        print(f'Record {record_id} post-processed. Ready for export.')
        
        # Export the record
        self.export_record(
            self.record_export_folder, 
            self.record_export_data_types, 
            self.record_export_format, 
            [record_id], 
            self.record_export_version
        )

    # Callback: Record exported
    def on_export_record_done(self, *args, **kwargs):
        print('Record export successful:')
        data = kwargs.get('data')
        print(data)
        self.c.close()

    # Callback: Error handler
    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(f'Error: {error_data}')

# Main script
def main():
    # Application client details (fill in your credentials)
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'
    license_key = '2607e309-03bf-4520-b687-4215420be1d3'  # Insert your license key here
    
    # Create Record object and pass the license key
    r = Record(your_app_client_id, your_app_client_secret, license_key=license_key)

    # Record settings
    r.record_title = 'EEG_Record_1'  # Required parameter, cannot be empty
    r.record_description = ''  # Optional parameter

    # Export settings
    r.record_export_folder = 'r.record_export_folder = C:/Users/jiahu/Desktop/'
 # Ensure correct path with write permission
    r.record_export_data_types = ['EEG', 'MOTION', 'PM', 'BP']  # Data types to export
    r.record_export_format = 'EDF'  # Export format (e.g., 'EDF')
    r.record_export_version = 'V2'  # Export version

    # Start recording process (adjust duration if needed)
    record_duration_s = 10  # 10 seconds recording
    r.start(record_duration_s)

if __name__ == '__main__':
    main()

# -----------------------------------------------------------
