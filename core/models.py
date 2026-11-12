from django.db import models


class Animal(models.Model):
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raca = models.CharField(max_length=100, blank=True)
    idade = models.PositiveIntegerField()

    UNIDADE_IDADE_CHOICES = [
        ('meses', 'Meses'),
        ('anos', 'Anos'),
    ]

    unidade_idade = models.CharField(
        max_length=5,
        choices=UNIDADE_IDADE_CHOICES,
        default='anos'
    )

    sexo = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='animais/', blank=True, null=True)
    status = models.CharField(max_length=30, default='Disponível')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'animal'
        verbose_name_plural = 'animais'

    def __str__(self):
        return self.nome

class SolicitacaoAdocao(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Em análise', 'Em análise'),
        ('Aprovada', 'Aprovada'),
        ('Recusada', 'Recusada'),
        ('Cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )

    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='solicitacoes'
    )

    data_solicitacao = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pendente'
    )

    class Meta:
        verbose_name = 'solicitação de adoção'
        verbose_name_plural = 'solicitações de adoção'

    def __str__(self):
        return f'{self.usuario.username} - {self.animal.nome}'