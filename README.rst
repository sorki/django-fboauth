django-fboauth
===============

WARNING:
This app is not mature enough to be used in production.

Facebook OAuth 2.0 authentication for Django

Installation
-------------

Add ``'fboauth'`` to INSTALLED_APPS.

.. TODO (minor): add minimal requirements for installed apps

To get your API keys register your app on http://facebook.com/developers/.
Then set these api keys with:

 * FACEBOOK_APP_ID
 * FACEBOOK_API_KEY

Add ``'fboauth.backends.FacebookBackend'`` to AUTHENTICATION_BACKENDS. This should be in addition to the 
default ModelBackend::

    AUTHENTICATION_BACKENDS = (
      'fboauth.backends.FacebookBackend',
      'django.contrib.auth.backends.ModelBackend',
    )

Add fboauth URLs to your application's urlconf. Example::

    urlpatterns = patterns('',
        ...
        (r'^fb/', include('fboauth.urls')),
        ...
    )

Configure LOGIN_URL adn LOGIN_REDIRECT_URL appropriately for your site.

Rerun 
    python manage.py syncdb

Usage
------

Authentication process is started automaticly when you visit::

    {% url fboauth_start %}



This application is based on http://djangosnippets.org/snippets/2065/
