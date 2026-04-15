### clientes/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class TerminosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            return self.get_response(request)

        path_excepciones = [
            reverse('clientes:aceptar_terminos'),
            reverse('logout'),
            '/admin/',
            '/static/',
            '/media/',
        ]

        if any(request.path.startswith(path) for path in path_excepciones):
            return self.get_response(request)

        from .models import AceptacionTerminos
        ya_acepto = AceptacionTerminos.objects.filter(user=request.user).exists()

        if not ya_acepto:
            return redirect('clientes:aceptar_terminos')

        return self.get_response(request)