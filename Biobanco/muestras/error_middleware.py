from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import Http404 

class CustomErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        response = self.get_response(request)

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            #manejo error 404
            return render(request, 'login_screen.html', status=404)
        
        else:
            logout(request)
            # manejo de otro tipo de error, ej 500
            # For instance, for a generic error page
            return render(request, 'generic_error.html', status=500)