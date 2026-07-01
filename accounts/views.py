from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)

from django.contrib.auth.decorators import login_required, user_passes_test

from .forms import RegisterForm, ProfileForm

from django.contrib import messages


User = get_user_model()


from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from .models import User


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.role = "VENDEUR"  # ou "ADMIN" selon ton choix
            user.save()

            login(request, user)

            return redirect("home")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})
# CONNEXION
# ==========================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # redirection selon rôle
            if user.is_superuser or user.role in ["VENDEUR", "ADMIN"]:
                return redirect("dashboard")

            return redirect("home")

        messages.error(request, "Identifiants incorrects")

    return render(request, "accounts/login.html")


# ==========================
# DECONNEXION
# ==========================

def logout_view(request):

    logout(request)

    return redirect("home")


# ==========================
# PROFIL
# ==========================

@login_required
def profile(request):

    if request.method == "POST":

        form = ProfileForm(request.POST, instance=request.user)

        if form.is_valid():

            form.save()

            return redirect("profile")

    else:

        form = ProfileForm(instance=request.user)

    return render(
        request,
        "accounts/profile.html",
        {"form": form}
    )


# ==========================
# SUPERUSER - LISTE VENDEURS
# ==========================

def is_superuser(user):

    return user.is_superuser


@user_passes_test(is_superuser)
def seller_list(request):

    sellers = User.objects.filter(role="VENDEUR")

    return render(
        request,
        "accounts/seller_list.html",
        {"sellers": sellers}
    )