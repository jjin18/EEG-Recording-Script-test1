from cortex import Cortex

class Train():
    """
    A class to use BCI API to control the training of mental command detections.
    """

    def __init__(self, app_client_id, app_client_secret, **kwargs):
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(query_profile_done=self.on_query_profile_done)
        self.c.bind(load_unload_profile_done=self.on_load_unload_profile_done)
        self.c.bind(save_profile_done=self.on_save_profile_done)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_sys_data=self.on_new_sys_data)
        self.c.bind(inform_error=self.on_inform_error)

    def start(self, profile_name, actions, headsetId=''):
        """
        To start the training process.
        """
        if profile_name == '':
            raise ValueError('Empty profile_name. The profile_name cannot be empty.')

        self.profile_name = profile_name
        self.actions = actions
        self.action_idx = 0

        self.c.set_wanted_profile(profile_name)

        if headsetId != '':
            self.c.set_wanted_headset(headsetId)

        self.c.open()

    def subscribe_data(self, streams):
        """
        To subscribe to one or more data streams
        """
        self.c.sub_request(streams)

    def load_profile(self, profile_name):
        """
        To load an existing profile or create a new profile for training.
        """
        status = 'load'
        self.c.setup_profile(profile_name, status)

    def unload_profile(self, profile_name):
        """
        To unload an existing profile.
        """
        self.c.setup_profile(profile_name, 'unload')

    def save_profile(self, profile_name):
        """
        To save a profile.
        """
        self.c.setup_profile(profile_name, 'save')

    def train_mc_action(self, status):
        """
        To control the training of the mental command action.
        """
        if self.action_idx < len(self.actions):
            action = self.actions[self.action_idx]
            print(f'train_mc_action: {action}:{status}')
            self.c.train_request(detection='mentalCommand',
                                 action=action,
                                 status=status)
        else:
            print('Training Complete')
            self.c.setup_profile(self.profile_name, 'save')
            self.action_idx = 0  # Reset action index

    # Callbacks
    def on_create_session_done(self, *args, **kwargs):
        print('Session created.')
        self.c.query_profile()

    def on_query_profile_done(self, *args, **kwargs):
        self.profile_lists = kwargs.get('data')
        if self.profile_name in self.profile_lists:
            self.c.get_current_profile()
        else:
            self.c.setup_profile(self.profile_name, 'create')

    def on_load_unload_profile_done(self, *args, **kwargs):
        is_loaded = kwargs.get('isLoaded')
        if is_loaded:
            self.subscribe_data(['sys'])
        else:
            print(f'Profile {self.profile_name} unloaded')
            self.c.close()

    def on_save_profile_done(self, *args, **kwargs):
        print(f'Profile {self.profile_name} saved successfully.')
        self.unload_profile(self.profile_name)

    def on_new_sys_data(self, *args, **kwargs):
        data = kwargs.get('data')
        train_event = data[1]
        action = self.actions[self.action_idx]
        print(f'on_new_sys_data: {action}: {train_event}')
        if train_event == 'MC_Succeeded':
            self.train_mc_action('accept')
        elif train_event == 'MC_Failed':
            self.train_mc_action('reject')
        elif train_event in ['MC_Completed', 'MC_Rejected']:
            self.action_idx += 1
            self.train_mc_action('start')

    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        if data['streamName'] == 'sys':
            print('System stream subscribed, starting training.')
            self.train_mc_action('start')

    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(f"Error: {error_data}")

# Main script
def main():
    # Fill your application clientId and clientSecret
    your_app_client_id = 'HsepSPbDYvV4j6AYANyR2fUysroiV2O5Mm2ACGil'
    your_app_client_secret = '9ZzzlgiPnI04hvYl0eYYl485lhpCKj6qQ6vNJnOc4WPN3ZH55WbFPAyoGYDXeqz2iOa0D2x1UJmquGpz29bHaB2yrnMIXhLhCCd9UbGB8XwVL0g85gLCjfPiYyamPcMe'

    # Initialize training
    t = Train(your_app_client_id, your_app_client_secret)

    profile_name = 'my_training_profile'  # Set your profile name

    # Actions to train
    actions = ['neutral', 'push', 'pull']

    # Start training
    t.start(profile_name, actions)

if __name__ == '__main__':
    main()
