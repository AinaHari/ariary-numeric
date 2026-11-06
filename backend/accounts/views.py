import base64
import datetime
import random
import uuid
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings as dj_settings

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle

from .models import User
from .serializers import RegisterSerializer, UserSerializer, ProfileUpdateSerializer
from django.conf import settings


class GuestView(APIView):
    """Crée un compte invité de démonstration avec un portefeuille déjà chargé."""
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "guest"

    def post(self, request):
        from wallet.services import get_or_create_wallet, topup_demo
        from decimal import Decimal
        from django.contrib.auth import get_user_model as gum

        User_ = gum()
        nonce = uuid.uuid4().hex[:10]
        password = "".join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789") for _ in range(18))
        user = User_.objects.create_user(
            email=f"invite.{nonce}@demo.local",
            password=password,
            first_name="Invité",
            last_name="Ariary",
            country="Madagascar",
        )
        lang = (request.data and (request.data.get("language") or "").lower()) or None
        if lang and lang in ("fr", "mg", "en"):
            user.preferred_language = lang
            user.save(update_fields=["preferred_language"])
        get_or_create_wallet(user)
        topup_demo(user, Decimal("50000"))
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": UserSerializer(user).data, "token": token.key, "demo": True,
             "detail": "Compte invité de démonstration créé (50 000 MGA préchargés, aucun argent réel)."},
            status=status.HTTP_201_CREATED,
        )


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = (ScopedRateThrottle,)
    throttle_scope = "login"

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""
        if not email or not password:
            return Response({"detail": "E-mail et mot de passe requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_locked():
            return Response({"detail": "Compte temporairement bloqué."}, status=status.HTTP_423_LOCKED)

        auth_user = authenticate(request, username=email, password=password)
        if auth_user is None:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.LOGIN_MAX_ATTEMPTS:
                user.locked_until = timezone.now() + datetime.timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
                user.failed_login_attempts = 0
            user.save(update_fields=["failed_login_attempts", "locked_until"])
            return Response({"detail": "Identifiants invalides."}, status=status.HTTP_401_UNAUTHORIZED)

        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"detail": "Déconnexion réussie."})


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProfileUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = ProfileUpdateSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(instance).data)


class PasswordResetRequestView(APIView):
    """Demande de réinitialisation : envoie un lien par e-mail (si le compte existe)."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f"{dj_settings.FRONTEND_BASE_URL if hasattr(dj_settings, 'FRONTEND_BASE_URL') else 'http://127.0.0.1:8001'}/reset?uid={uid}&token={token}"
            try:
                send_mail(
                    subject="Réinitialisation de votre mot de passe — Ariary Numeric",
                    message=f"Bonjour,\n\nPour réinitialiser votre mot de passe, ouvrez ce lien :\n{link}\n\nSi vous n'avez pas fait cette demande, ignorez ce message.",
                    from_email=dj_settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        # Réponse générique pour ne pas divulguer l'existence du compte.
        return Response({"detail": "Si un compte correspond à cet e-mail, un lien de réinitialisation a été envoyé."})


class PasswordResetConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password") or ""
        if not uid or not token or len(new_password) < 8:
            return Response({"detail": "Données invalides."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except Exception:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Lien expiré ou invalide."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        # invalider les tokens existants
        try:
            user.auth_token.delete()
        except Exception:
            pass
        return Response({"detail": "Mot de passe mis à jour."})


class EmailVerificationRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user = request.user
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        link = f"{dj_settings.FRONTEND_BASE_URL if hasattr(dj_settings, 'FRONTEND_BASE_URL') else 'http://127.0.0.1:8001'}/verify-email?uid={uid}&token={token}"
        try:
            send_mail(
                subject="Vérification de votre e-mail — Ariary Numeric",
                message=f"Bonjour,\n\nPour vérifier votre adresse e-mail, ouvrez ce lien :\n{link}",
                from_email=dj_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return Response({"detail": "E-mail de vérification envoyé."})


class EmailVerificationConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        if not uid or not token:
            return Response({"detail": "Données invalides."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            pk = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except Exception:
            return Response({"detail": "Lien invalide."}, status=status.HTTP_400_BAD_REQUEST)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Lien expiré ou invalide."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_verified_email = True
        user.save(update_fields=["is_verified_email"])
        return Response({"detail": "E-mail vérifié."})
