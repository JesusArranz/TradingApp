from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import login
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        print("🔍 Ejecutando pre_social_login")

        if request.user.is_authenticated:
            print("Usuario ya autenticado, no se hace nada")
            return

        email = sociallogin.account.extra_data.get('email')
        print("Email recibido desde Google:", email)

        if email:
            try:
                existing_user = User.objects.get(email=email)
                print(f"✅ Usuario encontrado con email: {email}, intentando fusionar...")

                if not SocialAccount.objects.filter(user=existing_user, provider=sociallogin.account.provider).exists():
                    print("🔗 Asignando cuenta social al usuario existente")
                    sociallogin.connect(request, existing_user)

                # 🔐 Forzar login con backend específico
                login(request, existing_user, backend='allauth.account.auth_backends.AuthenticationBackend')

                raise ImmediateHttpResponse(redirect('tradingapp:index-2'))

            except User.DoesNotExist:
                print("❌ No existe usuario con ese email, se creará uno nuevo")
