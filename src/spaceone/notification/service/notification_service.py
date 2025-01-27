import logging
import time
from spaceone.core.service import *
from spaceone.notification.manager.notification_manager import NotificationManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
class NotificationService(BaseService):

    def __init__(self, metadata):
        super().__init__(metadata)

    @transaction
    @check_required(['options', 'message', 'notification_type'])
    def dispatch(self, params):
        """
        Args:
            params:
                - options
                - message
                    - title
                    - description
                    - tags (list)
                        - key
                        - value
                        - options
                    - callbacks (list)
                        - url
                        - options
                - notification_type
                - secret_data:
                    - access_key
                    - sender
                - channel_data
                    - phone_number
        """

        secret_data = params.get('secret_data', {})
        channel_data = params.get('channel_data', {})
        notification_type = params['notification_type']
        params_message = params['message']

        access_key = secret_data.get('access_key')
        phone_number = channel_data.get('phone_number')
        kwargs = {}

        if 'sender' in secret_data:
            kwargs['sender'] = secret_data['sender']

        phone_numbers = phone_number.replace(" ", "").split(',')
        phone_numbers = [ph for ph in phone_numbers if ph != '']

        body = self.make_sms_body(params_message, notification_type)

        noti_mgr: NotificationManager = self.locator.get_manager('NotificationManager')
        noti_mgr.dispatch(access_key, params_message.get('title'), body, phone_numbers, **kwargs)

    @staticmethod
    def make_sms_body(message, notification_type):
        body = f'알림 타입: {notification_type}\n'

        if description := message.get('description', ''):
            body = f'{body}\n{description}\n'

        for tag in message.get('tags', []):
            tag_message = f'- {tag.get("key", "")}: {tag.get("value", "")}'

            body = f'{body}\n{tag_message}'

        return body
