from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class StorageType(models.Model):
    """
    Modelo para representar los tipos de almacenamiento.
    """
    NAME_CHOICES = [
        (1, 'Caja'),
        (2, 'Rack'),
        (3, 'Freezer'),
    ]

    name_storagetype = models.IntegerField(choices=NAME_CHOICES, unique=True)

    def __str__(self):
        return self.get_name_storagetype_display()

    class Meta:
        verbose_name = "Tipo de Almacenamiento"
        verbose_name_plural = "Tipos de Almacenamiento"
        db_table = 'STORAGE_TYPE'


class Storage(models.Model):
    """
    Modelo para representar el almacenamiento.
    """
    storage_name = models.IntegerField(null=False, blank=False)
    storage_state = models.BooleanField(
        null=False, blank=False, default=True)
    storage_description = models.CharField(
        max_length=50, null=False, blank=False)
    STORAGE_TYPE_id_storagetype = models.ForeignKey(
        StorageType, on_delete=models.CASCADE)

    @property
    def id_storage(self):
        """
        Genera un ID de almacenamiento en el formato: [id_storagetype]-[storage_name]
        """
        return f"{self.STORAGE_TYPE_id_storagetype.name_storagetype}-{self.storage_name}"

    def __str__(self):
        return self.id_storage

    class Meta:
        verbose_name = "Almacenamiento"
        verbose_name_plural = "Almacenamientos"
        db_table = 'STORAGE'


class Sample(models.Model):
    id_sample = models.CharField(max_length=16, primary_key=True)

    id_subject = models.CharField(max_length=10)
    date_sample = models.DateField()

    ml_volume = models.FloatField(validators=[MinValueValidator(0)])
    state_analysis = models.BooleanField(
        default=False, help_text="Valores: 0. No analizada 1. Enviada a análisis")
    state_preservation = models.BooleanField(
        default=False, help_text="Valores: 0. Normal 1. Descongelada")

    specification = models.CharField(max_length=10)
    SHIPMENT_id_shipment = models.IntegerField(
        null=True, blank=True)

    def save(self, *args, **kwargs):
        self.id_sample = f"{self.id_subject}-{self.specification}{self.date_sample}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'SAMPLE'


class Location(models.Model):
    id_location = models.AutoField(primary_key=True)
    cell = models.IntegerField(null=True, blank=True)
    SAMPLE_id_sample_1 = models.ForeignKey(Sample, on_delete=models.CASCADE)
    STORAGE_id_storage_1 = models.ForeignKey(Storage, on_delete=models.CASCADE)
    STORAGE_TYPE_id_storagetype = models.ForeignKey(
        StorageType, on_delete=models.CASCADE)

    def __str__(self):
        return f"Location {self.id_location}"

    class Meta:
        db_table = 'LOCATION'


class Shipment(models.Model):
    id_shipment = models.AutoField(primary_key=True)
    date_shipment = models.DateField()
    laboratory = models.CharField(max_length=30)
    analysis = models.CharField(max_length=50)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='shipments',
        null=True  # Permite valores nulos
    )

    def __str__(self):
        return f"Shipment {self.id_shipment}"

    class Meta:
        db_table = 'SHIPMENT'


class SampleEvent(models.Model):
    id_event = models.AutoField(primary_key=True)
    event_user = models.CharField(max_length=15)
    event_date = models.DateField()
    action = models.CharField(max_length=15)
    action_information = models.CharField(max_length=100)
    SAMPLE_id_sample = models.ForeignKey(
        Sample, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Event {self.id_event} on Sample {self.SAMPLE_id_sample.id_sample}"

    class Meta:
        db_table = 'SAMPLE_EVENT'
