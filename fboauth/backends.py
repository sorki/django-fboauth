from django.contrib.auth.models import User

from models import FacebookSession, FacebookSessionError

class FacebookBackend:
    def authenticate(self, token=None):
        facebook_session = FacebookSession.objects.get(access_token=token)

        try:
            profile = facebook_session.query('me')
        except FacebookSessionError:
            return None

   
        try:
            user = User.objects.get(username=profile['email'])
        except User.DoesNotExist, e:
            # create user
            i = 1
            while True:
                username = profile['email']
                if i > 1:
                    username += str(i)
                try:
                    User.objects.get(username__exact=username)
                except User.DoesNotExist:
                    break
                i += 1

            user = User(username=username)

    
        user.set_unusable_password()
        user.email = profile['email']
        user.first_name = profile['first_name']
        user.last_name = profile['last_name']
        user.save()

        try:
            FacebookSession.objects.get(uid=profile['id']).delete()
        except FacebookSession.DoesNotExist, e:
            pass

        facebook_session.uid = profile['id']
        facebook_session.user = user
        facebook_session.save()
   
        return user
   
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
