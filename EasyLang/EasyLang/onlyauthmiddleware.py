
from django.shortcuts import redirect
from django.http import HttpResponse

class onlyauthmiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # if contains webhooks, pass
        response = self.get_response(request)
        # set content type
        response['Content-Type'] = 'text/html; charset=utf-8'
        if request.path.startswith('/webhooks/'):
            return response
        
        if not request.user.is_authenticated and request.path != '/login/':
            return redirect('login')
        # Code to be executed for each request/response after
        # the view is called.
        return response
