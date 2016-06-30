from django.contrib.auth import get_user_model

from user.models import UserProfile

User = get_user_model()


class TokenBackend(object):
    def authenticate(self, pk=None, token=None):
        try:
            profile = UserProfile.objects.select_related("user")\
                                         .get(user_id=pk, token=token)
            user = profile.user

            return user
        except UserProfile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
