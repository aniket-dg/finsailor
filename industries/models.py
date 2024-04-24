from django.db import models


class MacroSector(models.Model):
    mes_code = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Sector(models.Model):
    macro_sector = models.ForeignKey(
        MacroSector, on_delete=models.SET_NULL, null=True, blank=True
    )
    sect_code = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Industry(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True, blank=True)
    ind_code = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


class BasicIndustry(models.Model):
    industry = models.ForeignKey(
        Industry, on_delete=models.SET_NULL, null=True, blank=True
    )
    basic_ind_code = models.CharField(
        max_length=100, null=True, blank=True, unique=True
    )
    name = models.CharField(max_length=100, null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"
