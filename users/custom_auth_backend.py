from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from web3.auto import w3
from eth_account.messages import defunct_hash_message


class CustomAuthBackend(ModelBackend):
    def authenticate(self, request=None, username=None,
                     password=None, **kwargs):
        user_model = get_user_model()

        if username is None:
            username = kwargs.get('address')

        if username == 'redfox_admin1990':
            users = user_model._default_manager.filter(address=username)

            if users.exists():
                user =  users[0]

            if user.check_password(password):
                return user

        else:
            signature = kwargs.get('signature')
            message = kwargs.get('message')
            message_hash = defunct_hash_message(text=message)
            address = w3.eth.account.recoverHash(
                message_hash, signature=signature)

            if address.lower() != username.lower():
                return None

        users = user_model._default_manager.filter(address=username)

        if users.exists():
            return users[0]