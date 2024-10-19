from cortex import Cortex

class LiveAdvance():
    """
    A class to show performance metrics (met) data at live mode.
    """

    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(save_profile_done=self.on_save_profile_done)
        self.c.bind(new_met_data=self.on_new_met_data)  # Subscribing to performance metrics
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, profile_name, headsetId=''):
        """
        To start live process as below workflow:
        (1) check access right -> authorize -> connect headset->create session
        (2) query profile -> get current profile -> load/create profile
        (3) subscribe to 'met' data for live performance metrics
        """
        if profile_name == '':
            raise ValueError('Empty profile_name. The profile_name cannot be empty.')

        self.profile_name = profile_name
        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def load_profile(self, profile_name):
        """
        To load a profile.

        Parameters
        ----------
        profile_name : str, required
            profile name

        Returns
        -------
        None
        """
        self.c.setup_profile(profile_name, 'load')

    def unload_profile(self, profile_name):
        """
        To unload a profile.

        Parameters
        ----------
        profile_name : str, required
            profile name

        Returns
        -------
        None
        """
        self.c.setup_profile(profile_name, 'unload')

    def save_profile(self, profile_name):
        """
        To save a profile.

        Parameters
        ----------
        profile_name : str, required
            profile name

        Returns
        -------
        None
        """
        self.c.setup_profile(profile_name, 'save')

    def subscribe_data(self, streams):
        """
        To subscribe to one or more data streams.

        Parameters
        ----------
        streams : list, required
            list of streams. For example, ['met'] to subscribe to performance metrics.

        Returns
        -------
        None
        """
        self.c.sub_request(streams)

    # Callbacks
    def on_create_session_done(self, *args, **kwargs):
        print('on_create_session_done')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        print('on_query_profile_done')
        self.profile_lists = kwargs.get('data')
        if self.profile_name in self.profile_lists:
            self.c.get_current_profile()
        else:
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        print("on_load_unload_profile_done: " + str(is_loaded))
        
        if is_loaded == True:
            # Subscribe to performance metrics (met) data
            streams = ['met']
            self.subscribe_data(streams)
        else:
            print('The profile ' + self.profile_name + ' is unloaded')

    def on_save_profile_done(self, *args, **kwargs):
        print('Save profile ' + self.profile_name + " successfully")
        streams = ['met']
        self.subscribe_data(streams)

    def on_new_met_data(self, *args, **kwargs):
        """
        To handle performance metrics (met) data emitted from Cortex.

        Returns
        -------
        data: dictionary
             the format could be {'met': [...], 'time': ...}
        """
        data = kwargs.get('data')
        print('Performance metrics data: {}'.format(data))

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        error_code = error_data['code']
        error_message = error_data['message']
        print(f'Error {error_code}: {error_message}')


def run_performance_metrics_live():
    """
    Run the live streaming of performance metrics data ('met').
    """

    # Fill in your application clientId and clientSecret before running script
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'

    # Init live streaming for performance metrics
    l = LiveAdvance(your_app_client_id, your_app_client_secret)

    trained_profile_name = 'trainingtest1'  # Please set a trained profile name here
    l.start(trained_profile_name)

if __name__ == '__main__':
    run_performance_metrics_live()
