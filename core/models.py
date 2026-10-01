from django.db import models


class Animal(models.Model):
    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raca = models.CharField(max_length=100, blank=True)
    idade = models.PositiveIntegerField()
    sexo = models.CharField(max_length=20)
    cidade = models.CharField(max_length=100)
    descricao = models.TextField()
    foto = models.ImageField(upload_to='animais/', blank=True, null=True)
    status = models.CharField(max_length=30, default='Disponível')
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome