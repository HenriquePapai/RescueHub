from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Animal, AdoptionRequest, AuditLog
from django.views.decorators.csrf import ensure_csrf_cookie
import re


# Autenticacao
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
    
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(username=username).exists():
            error = 'Nome de usuário já existe.'
            return render(request, 'core/register.html', {'error': error})
        
        if User.objects.filter(email=email).exists():
            error = 'E-mail já cadastrado.'
            return render(request, 'core/register.html', {'error': error})
            
        if len(password) < 12:
            error = 'A senha deve ter pelo menos 12 caracteres.'
            return render(request, 'core/register.html', {'error': error})
            
        if not re.search(r'[A-Z]', password):
            error = 'A senha deve ter pelo menos uma letra maiúscula.'
            return render(request, 'core/register.html', {'error': error})
            
        if not re.search(r'[a-z]', password):
            error = 'A senha deve ter pelo menos uma letra minúscula.'
            return render(request, 'core/register.html', {'error': error})
            
        if not re.search(r'[0-9]', password):
            error = 'A senha deve ter pelo menos um número.'
            return render(request, 'core/register.html', {'error': error})
            
        if not re.search(r'[!@#$%&*._]', password):
            error = 'A senha deve ter pelo menos um caractere especial.'
            return render(request, 'core/register.html', {'error': error})
            
        user = User.objects.create_user(username=username, password=password,
                                        email=email, first_name=first_name, last_name=last_name)
        login(request, user)
        return redirect('home')
    return render(request, 'core/register.html')

# Home
def home(request):
    return render(request, 'core/home.html')

# RF02 e RF03
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
        return redirect('animal_detail', pk=animal.pk)
    return render(request, 'core/animal_form.html', {'title': f'Editar {animal.name}', 'animal': animal})

@login_required
def solicitar_adocao(request, pk):
    animal_selecionado = get_object_or_404(Animal, pk=pk)
    if not request.user.is_adotante():
        messages.error(request, 'Apenas usuários com perfil "Adotante" podem solicitar adoções.')
        return redirect('animal_detail', pk=animal_selecionado.pk)
        
    if animal_selecionado.status != 'disponivel':
        messages.error(request, 'Este animal não está mais disponível para adoção.')
        return redirect('animal_detail', pk=animal_selecionado.pk)
        
    if request.method == 'POST':
        arquivo_documento = request.FILES.get('documento')
        
        # Valida o arquivo e se a extensão é PDF
        if not arquivo_documento or not arquivo_documento.name.lower().endswith('.pdf'):
            messages.error(request, 'Você deve anexar a documentação obrigatória estritamente no formato PDF.')
        else:
            # Cria a solicitação no Serviço de Adoções
            AdoptionRequest.objects.create(
                animal=animal_selecionado,
                adotante=request.user,
                document=arquivo_documento,
                status='pendente'
            )
            
            # Atualiza o status do animal
            animal_selecionado.status = 'em_processo'
            animal_selecionado.save()
            
            messages.success(request, 'Sua solicitação de adoção foi enviada com sucesso! Em breve nossa equipe entrará em contato.')
            return redirect('animal_detail', pk=animal_selecionado.pk)
            
    return render(request, 'core/adoption_form.html', {'animal': animal_selecionado})

# Req 8: Área do adotante
@login_required
def meus_pedidos(request):
    if not request.user.is_adotante():
        messages.error(request, 'Acesso restrito para adotantes.')
        return redirect('home')
    
    pedidos = AdoptionRequest.objects.filter(adotante=request.user).order_by('-created_at')
    return render(request, 'core/meus_pedidos.html', {'pedidos': pedidos})

# Req 9: Área de gerêncianciamento
@login_required
def gerenciar_adocoes(request):
    if not request.user.can_manage_animals():
        messages.error(request, 'Acesso negado.')
        return redirect('home')
    
    pedidos = AdoptionRequest.objects.all().order_by('-created_at')
    return render(request, 'core/gerenciar_adocoes.html', {'pedidos': pedidos})

# Req 10: Aprovação e Log de Auditoria
@login_required
@ensure_csrf_cookie
def avaliar_adocao(request, pk):
    if not request.user.can_manage_animals():
        return redirect('home')
        
    pedido = get_object_or_404(AdoptionRequest, pk=pk)
    
    if request.method == 'POST':
        # Apenas admins podem aprovar/rejeitar (Requisito 2)
        if not request.user.can_approve_adoptions():
            messages.error(request, 'Apenas administradores podem alterar o status de adoções.')
            return redirect('avaliar_adocao', pk=pedido.pk)
            
        novo_status = request.POST.get('status')
        status_opcoes_dict = dict(AdoptionRequest.STATUS_OPCOES)
        
        if novo_status in status_opcoes_dict:
            status_antigo_display = pedido.get_status_display()
            pedido.status = novo_status
            pedido.save()
            
            # Requisito 3: Registrar Log
            AuditLog.objects.create(
                adoption_request=pedido,
                user=request.user,
                action=f"Status alterado de '{status_antigo_display}' para '{pedido.get_status_display()}'"
            )
            
            # Atualiza status do animal se necessário
            if novo_status == 'aprovado':
                pedido.animal.status = 'adotado'
            elif novo_status in ['rejeitado', 'pendente']:
                pedido.animal.status = 'disponivel'
            pedido.animal.save()
            
            messages.success(request, 'Status da adoção atualizado com sucesso.')
            return redirect('gerenciar_adocoes')
            
    return render(request, 'core/avaliar_adocao.html', {'pedido': pedido})