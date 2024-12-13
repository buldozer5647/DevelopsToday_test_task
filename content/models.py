from django.db import models

class SpyCat(models.Model):
    name = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    breed = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Mission(models.Model):
    cat = models.OneToOneField(SpyCat, on_delete=models.SET_NULL, null=True, blank=True, related_name="mission")
    is_completed = models.BooleanField(default=False)
    is_done_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Mission #{self.id} - {'Completed' if self.is_completed else 'Pending'}"

class Target(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='targets')
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.country}"
