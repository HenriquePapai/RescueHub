from django.test import TestCase
from .models import User, Animal


# RF01 - Autenticação e Autorização
class AutenticacaoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='adotante', password='Senha@123456')

    def test_login_correto(self):
        logado = self.client.login(username='adotante', password='Senha@123456')
        self.assertTrue(logado)

    def test_login_incorreto(self):
        logado = self.client.login(username='adotante', password='errada')
        self.assertFalse(logado)

    def test_logout(self):
        self.client.login(username='adotante', password='Senha@123456')
        self.client.logout()
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_perfil_padrao_adotante(self):
        self.assertEqual(self.user.role, 'adotante')

    def test_perfil_voluntario(self):
        vol = User.objects.create_user(username='vol', password='Senha@123456', role='voluntario')
        self.assertTrue(vol.can_manage_animals())

    def test_perfil_admin(self):
        adm = User.objects.create_user(username='adm', password='Senha@123456', role='admin')
        self.assertTrue(adm.is_admin())


# RF02 - Cadastro e Gestão de Animais
class CadastroAnimalTestCase(TestCase):
    def test_cadastrar_animal(self):
        animal = Animal.objects.create(name='Rex', species='cao', sex='macho', age=3, size='medio', description='Dócil')
        self.assertEqual(Animal.objects.count(), 1)
        self.assertEqual(animal.status, 'disponivel')

    def test_editar_animal(self):
        animal = Animal.objects.create(name='Mimi', species='gato', sex='femea', age=2, size='pequeno', description='Tímida')
        animal.name = 'Mimi Atualizada'
        animal.save()
        self.assertEqual(Animal.objects.get(pk=animal.pk).name, 'Mimi Atualizada')

    def test_status_padrao_disponivel(self):
        animal = Animal.objects.create(name='Bolt', species='cao', sex='macho', age=1, size='grande', description='Ativo')
        self.assertEqual(animal.status, 'disponivel')


# RF03 - Visualização e Filtro do Catálogo
class CatalogoTestCase(TestCase):
    def setUp(self):
        Animal.objects.create(name='Rex', species='cao', sex='macho', age=3, size='medio', description='D', status='disponivel')
        Animal.objects.create(name='Mimi', species='gato', sex='femea', age=2, size='pequeno', description='D', status='disponivel')
        Animal.objects.create(name='Bolt', species='cao', sex='macho', age=5, size='grande', description='D', status='adotado')

    def test_listar_todos(self):
        self.assertEqual(Animal.objects.count(), 3)

    def test_filtrar_cao(self):
        self.assertEqual(Animal.objects.filter(species='cao').count(), 2)

    def test_filtrar_gato(self):
        self.assertEqual(Animal.objects.filter(species='gato').count(), 1)

    def test_filtrar_disponiveis(self):
        self.assertEqual(Animal.objects.filter(status='disponivel').count(), 2)

    def test_filtrar_faixa_etaria(self):
        self.assertEqual(Animal.objects.filter(age__lte=3).count(), 2)