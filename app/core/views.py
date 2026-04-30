from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Animal


# AUTH
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = None
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user:
            login(request, user)
            return redirect('home')
        error = 'Usuário ou senha incorretos.'
    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe.')
            return render(request, 'core/register.html')
        if len(password) < 12:
            messages.error(request, 'A senha deve ter pelo menos 12 caracteres.')
            return render(request, 'core/register.html')
        user = User.objects.create_user(username=username, password=password,
                                        email=email, first_name=first_name, last_name=last_name)
        login(request, user)
        messages.success(request, f'Bem-vindo(a), {first_name or username}!')
        return redirect('home')
    return render(request, 'core/register.html')


# HOME
def home(request):
    return render(request, 'core/home.html')


# ANIMALS — RF02 e RF03
def catalog(request):
    animals = Animal.objects.all()
    species = request.GET.get('species', '')
    sex = request.GET.get('sex', '')
    size = request.GET.get('size', '')
    status = request.GET.get('status', 'disponivel')
    if species:
        animals = animals.filter(species=species)
    if sex:
        animals = animals.filter(sex=sex)
    if size:
        animals = animals.filter(size=size)
    if status:
        animals = animals.filter(status=status)
    return render(request, 'core/catalog.html', {
        'animals': animals, 'species': species, 'sex': sex,
        'size': size, 'status': status,
    })


def animal_detail(request, pk):
    animal = get_object_or_404(Animal, pk=pk)
    can_manage = request.user.is_authenticated and request.user.can_manage_animals()
    return render(request, 'core/animal_detail.html', {'animal': animal, 'can_manage': can_manage})


@login_required
def animal_create(request):
    if not request.user.can_manage_animals():
        messages.error(request, 'Acesso negado.')
        return redirect('catalog')
    if request.method == 'POST':
        animal = Animal.objects.create(
            name=request.POST.get('name'),
            species=request.POST.get('species'),
            sex=request.POST.get('sex'),
            age=request.POST.get('age'),
            size=request.POST.get('size'),
            temperament=request.POST.get('temperament', ''),
            description=request.POST.get('description'),
            health_history=request.POST.get('health_history', ''),
            status=request.POST.get('status', 'disponivel'),
            created_by=request.user,
        )
        if request.FILES.get('photo'):
            animal.photo = request.FILES['photo']
            animal.save()
        messages.success(request, f'{animal.name} cadastrado!')
        return redirect('animal_detail', pk=animal.pk)
    return render(request, 'core/animal_form.html', {'title': 'Cadastrar Animal'})


@login_required
def animal_edit(request, pk):
    if not request.user.can_manage_animals():
        messages.error(request, 'Acesso negado.')
        return redirect('catalog')
    animal = get_object_or_404(Animal, pk=pk)
    if request.method == 'POST':
        animal.name = request.POST.get('name')
        animal.species = request.POST.get('species')
        animal.sex = request.POST.get('sex')
        animal.age = request.POST.get('age')
        animal.size = request.POST.get('size')
        animal.temperament = request.POST.get('temperament', '')
        animal.description = request.POST.get('description')
        animal.health_history = request.POST.get('health_history', '')
        animal.status = request.POST.get('status', 'disponivel')
        if request.FILES.get('photo'):
            animal.photo = request.FILES['photo']
        animal.save()
        messages.success(request, f'{animal.name} atualizado.')
        return redirect('animal_detail', pk=animal.pk)
    return render(request, 'core/animal_form.html', {'title': f'Editar {animal.name}', 'animal': animal})