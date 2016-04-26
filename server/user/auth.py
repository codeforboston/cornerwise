from django.contrib.auth import get_user_model

User = get_user_model()


class TokenBackend(object):
    def authenticate(self, pk=None, token=None):
        try:
            user = User.objects.get(pk=pk)
            profile = user.profile

            if profile.token != token:
                return None

            user.is_active = True
            user.save()

            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
