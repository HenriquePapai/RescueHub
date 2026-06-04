from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLES = [
        ('adotante', 'Adotante'),
        ('voluntario', 'Voluntário'),
        ('admin', 'Administrador'),
    ]
    role = models.CharField('Perfil', max_length=20, choices=ROLES, default='adotante')
    phone = models.CharField('Telefone', max_length=20, blank=True)

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_voluntario(self):
        return self.role == 'voluntario'

    def is_adotante(self):
        return self.role == 'adotante'

    def can_manage_animals(self):
        return self.role in ('admin', 'voluntario') or self.is_superuser
    
    def can_approve_adoptions(self):
        return self.role == 'admin' or self.is_superuser

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

class Animal(models.Model):
    SPECIES = [('cao', 'Cão'), ('gato', 'Gato')]
    SEX = [('macho', 'Macho'), ('femea', 'Fêmea')]
    SIZE = [('pequeno', 'Pequeno'), ('medio', 'Médio'), ('grande', 'Grande')]
    STATUS = [
        ('disponivel', 'Disponível'),
        ('em_processo', 'Em Processo'),
        ('adotado', 'Adotado'),
    ]

    name = models.CharField('Nome', max_length=100)
    species = models.CharField('Espécie', max_length=10, choices=SPECIES)
    sex = models.CharField('Sexo', max_length=10, choices=SEX)
    age = models.PositiveIntegerField('Idade estimada (anos)')
    size = models.CharField('Porte', max_length=10, choices=SIZE)
    temperament = models.CharField('Temperamento', max_length=200, blank=True)
    description = models.TextField('Descrição')
    health_history = models.TextField('Histórico de saúde', blank=True)
    photo = models.ImageField('Foto', upload_to='animals/', blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS, default='disponivel')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='animals_created')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.get_species_display()})'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Animal'
        verbose_name_plural = 'Animais'
        
class AdoptionRequest(models.Model):
    STATUS_OPCOES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='pedidos_adocao')
    adotante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos_adocao')
    document = models.FileField('Documentação', upload_to='documentos/')
    status = models.CharField('Status', max_length=20, choices=STATUS_OPCOES, default='pendente')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Pedido de {self.adotante.username} para {self.animal.name}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pedido de Adoção'
        verbose_name_plural = 'Pedidos de Adoção'

class AuditLog(models.Model):
    adoption_request = models.ForeignKey('AdoptionRequest', on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField('Ação', max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'