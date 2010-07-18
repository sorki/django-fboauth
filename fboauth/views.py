import re
import cgi
import urllib
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.functional import curry
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site, RequestSite

from models import FacebookSession

DOMAIN = "https://graph.facebook.com/oauth/"
URL = DOMAIN+"authorize?client_id=%s&redirect_uri=%s&scope=email&display=page"

def redirect_uri(request, redirect_to_reversed):
    ''' Build redirect uri '''
    if Site._meta.installed:
        domain = Site.objects.get_current().domain
    else:
        domain = RequestSite(request).domain
    
    http_or_https = ("https" if request.is_secure() else "http")+"://"

    return http_or_https+domain+redirect_to_reversed


def start(request, redirect_to='fboauth_complete'):
    return HttpResponseRedirect(URL % 
            (getattr(settings, 'FACEBOOK_APP_ID', ''), 
             redirect_uri(request, reverse(redirect_to))))

def default_render_failure(request, message, status=403, 
        template_name='fboauth/failure.html'):
    ''' Render an error page to the user '''

    data = render_to_string(
        template_name, dict(message=message),
        context_instance=RequestContext(request))
    return HttpResponse(data, status=status)

# TODO (minor): add posibility to pass function to complete view 
# which will be passed to authenticate method and which
# will affect the behaviour of user creation
# (to be able to use profile['id'] instead of profile['email'] etc
def complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
        render_failure=default_render_failure):

    render_failure = curry(render_failure, request)
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL

    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        redirect_to = settings.LOGIN_REDIRECT_URL

    error = None
    if request.GET:
        if 'code' in request.GET:
            args = {
                'client_id': getattr(settings, 'FACEBOOK_APP_ID', ''),
                'client_secret': getattr(settings, 'FACEBOOK_API_SECRET', ''),
                'redirect_uri':  redirect_uri(request, reverse(complete)),
                'code': request.GET['code'],
            }

            url = DOMAIN+'access_token?' + \
                    urllib.urlencode(args)
            response = cgi.parse_qs(urllib.urlopen(url).read())
            access_token = response['access_token'][0]
            expires = response['expires'][0]

            facebook_session = FacebookSession.objects.get_or_create(
                access_token=access_token,
            )[0]

            facebook_session.expires = expires
            facebook_session.save()

            user = auth.authenticate(token=access_token)
            if user:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(redirect_to)
                else:
                    render_failure('Disabled account') 
            else:
                render_failure('Authentication failed')
        elif 'error_reason' in request.GET:
            render_failure('Authentication cancelled')

    return HttpResponseRedirect(redirect_to)
