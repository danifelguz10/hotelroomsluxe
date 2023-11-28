import random
import string

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin, Group, Permission)
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _



def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))



class CustomAccountManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, **other_fields):

        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name,
                          last_name=last_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.') 

        return self.create_user(email, first_name, last_name, password, **other_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    document_number = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(
        upload_to='users/', default='users/default.png')
    followers = models.ManyToManyField(
        "self",
        related_name='following',
        symmetrical=False,
        blank=True)
    slug = models.SlugField(max_length=255, unique=True)

    register_date = models.DateTimeField(default=timezone.now)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_absolute_url(self):
        return reverse('users:user_detail', args=[self.slug])

    def count_following(self):
        users_following = UserProfile.objects.filter(followers=self)
        return users_following.count()

    def is_follower(self, other_user):
        if other_user in self.followers.all():
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + "-" + self.email)
        super(UserProfile, self).save(*args, **kwargs)
        
class UserProfileGroup(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.email} - {self.group.name}'
        
class Room(models.Model):
    DISPONIBLE = 'Disponible'
    OCUPADO = 'Ocupado'
    DESHABILITADA = 'Deshabilitada'

    ESTADO_CHOICES = [
        (DISPONIBLE, 'Disponible'),
        (OCUPADO, 'Ocupado'),
        (DESHABILITADA, 'Deshabilitada'),
    ]

    number = models.IntegerField(verbose_name='Número')
    description = models.TextField(verbose_name='Descripción')
    price = models.IntegerField()
    ammount = models.PositiveIntegerField()
    state = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=DISPONIBLE,
        verbose_name='Estado'
    )
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name='Imagen')

    def __str__(self):
        return f'Habitación {self.number} - {self.get_estado_display()}'
        
class Reservation(models.Model):
    
    STATUS_CHOICES = [
        ('Solicitada', 'Solicitada'),
        ('Aprobada', 'Aprobada'),
        ('Desaprobada', 'Desaprobada'),
        ('Cancelada', 'Cancelada'),
    ]
    
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='Usuario')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, verbose_name='Habitación')
    check_in_date = models.DateField(verbose_name='Fecha de Check-In')
    check_out_date = models.DateField(verbose_name='Fecha de Check-Out')
    reservation_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Reserva')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Solicitada')

    def __str__(self):
        return f'Reservación de {self.user} para la Habitación {self.room.number}'

    class Meta:
        verbose_name = 'Reservación'
        verbose_name_plural = 'Reservaciones'