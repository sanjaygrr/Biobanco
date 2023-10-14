from django.db import models


class Location(models.Model):
    STATE_CHOICES = [
        (0, 'Sin uso'),
        (1, 'En uso'),
    ]

    cell = models.IntegerField()
    box = models.IntegerField()
    rack = models.IntegerField()
    freezer = models.IntegerField()
    location_state = models.BooleanField(choices=STATE_CHOICES)
    description = models.TextField(default="")

    @property
    def id_location(self):
        """
        Genera un ID de localización en el formato: [box]-[cell]
        """
        return f"{self.box}-{self.cell}"

    def __str__(self):
        return self.id_location

    class Meta:
        unique_together = ['cell', 'box', 'rack', 'freezer']
        verbose_name = "Location"
        verbose_name_plural = "Locations"

    @property
    def get_space_type_and_value(self):
        if self.box != 0:
            return 'Caja', self.box
        elif self.cell != 0:
            return 'Celda', self.cell
        elif self.rack != 0:
            return 'Rack', self.rack
        elif self.freezer != 0:
            return 'Freezer', self.freezer
        else:
            return 'Desconocido', 0
