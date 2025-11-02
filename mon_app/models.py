from django.db import models

class Transaction(models.Model):
    OPERATEUR_CHOICES = [
        ('Wave', 'Wave'),
        ('Orange Money', 'Orange Money'),
        ('Moov', 'Moov'),
        ('Telecel', 'Telecel'),
        ('Sank', 'Sank'),
    ]
    
    TYPE_TRANSACTION_CHOICES = [
        ('Dépôt', 'Dépôt'),
        ('Retrait', 'Retrait'),
    ]
    
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    CNIB = models.CharField(max_length=50)
    type_transaction = models.CharField(max_length=10, choices=TYPE_TRANSACTION_CHOICES)
    operateur = models.CharField(max_length=15, choices=OPERATEUR_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} {self.prenom} - {self.type_transaction} - {self.montant}"