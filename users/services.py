from django.contrib.auth import authenticate
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from web3.auto import w3
from faker import Faker

from whack_blob.services import update_user_score

from .models import User


def user_login(address: str, signature: str, message: str):
    check_user = check_if_user_exists(address)

    if not check_user:
        new_user = create_user(address)
        address = new_user.address
        new_user.is_active = True
        new_user.save()

    authenticate_kwargs = {
        'address': address,
        'message': message,
        'signature': signature
    }

    user = authenticate(**authenticate_kwargs)

    if not user:
        raise ValidationError(
            'Incorrect login credentials'
        )
    tokens = RefreshToken.for_user(user)

    credit_referral_points(user)

    return {
        'access_token': str(tokens.access_token),
        'refresh_token': str(tokens),
    }


def check_if_user_exists(address: str):
    try:
        User.objects.get(address=address)
    except User.DoesNotExist:
        return False
    
    return True


def create_user(address: str):
    referral_username = create_referral_username()
    user = User.objects.create(
        address=address,
        referral_username=referral_username
    )
    
    return user


def credit_referral_points(user: User):
    old_referral_count = user.last_rewarded_referral_count
    new_referral_count = User.objects.filter(referrer_username=user.referral_username).count()
    extra_referrals = new_referral_count - old_referral_count
    referral_points = extra_referrals * 500

    if referral_points > 0:
        data = {
            'season': 1,
            'score': referral_points}

        update_user_score(user, data, ref_score=True)

    else:
        pass


def create_referral_username():
    gen_name = Faker().first_name_nonbinary()
    referral_username = 'redfox-{}'.format(gen_name)

    if not validate_ref_username(referral_username):
        create_referral_username()

    return referral_username


def validate_ref_username(re_username):
    try:
        User.objects.get(referral_username=re_username)
        return False
    except User.DoesNotExist:
        return True


def save_referral_details(referral_address: str, referrer_username: str):
    update_referral(referral_address, referrer_username)
    update_referrer(referrer_username)


def update_referral(referral_address: str, referrer_username: str):
    try:
        referral = User.objects.get(address=referral_address)
        referral.referrer_username = referrer_username
        referral.save(update_fields=['referrer_username'])
    except User.DoesNotExist:
        raise ValidationError(
            'Referral does not exist'
        )


def update_referrer(referrer_username: str):
    try:
        referrer = User.objects.get(referral_username=referrer_username)
        referrer.referral_count += 1
        referrer.save(update_fields=['referral_count'])
    except User.DoesNotExist:
        raise ValidationError(
            'Referrer does not exist'
        )
    

def get_player_profile(address: str) -> User:
    try:
        player = User.objects.get(address=address)
    except User.DoesNotExist:
        raise ValidationError(
            'User Does not exist'
        )
    return player


def update_user_task(
        user: User,
        twitter_task: int = 0,
        telegram_task: int = 0,
        whitelist_task: int = 0
):
    user.twitter_task = twitter_task
    user.telegram_task = telegram_task
    user.whitelist_task = whitelist_task
    user.save(update_fields=[
        'twitter_task',
        'telegram_task',
        'whitelist_task'])
