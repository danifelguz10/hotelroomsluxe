from django import forms
from .models import Room, Reservation
from django.utils import timezone
from django.core.exceptions import ValidationError  

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'id': 'loginEmail',
                'type': 'email',
                'class': 'form-control'
            }
        )
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'id': 'loginPassword',
            'type': 'password',
            'class': 'form-control',
        })
    )


class UserSignUpForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'id': 'signupEmail',
                'type': 'email',
                'class': 'form-control'
            }
        )
    )

    first_name = forms.CharField(
        label='Nombres',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control'
            }
        ))
    
    document_number = forms.CharField(
        label='Documento',
        widget=forms.TextInput(
            attrs={
                'type': 'number',
                'class': 'form-control'
            }
        ))

    last_name = forms.CharField(
        label='Apellidos',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'type': 'text',
                'class': 'form-control'
            }
        ))
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(
            attrs={
                'id': 'signupPassword',
                'type': 'password',
                'class': 'form-control'
            }
        ))

    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(
            attrs={
                'type': 'password',
                'class': 'form-control'
            }
        ))

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Las Contraseñas no coinciden')
        return cd['password2']
    
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'image', 'description', 'price', 'ammount', 'state']

    def __init__(self, *args, **kwargs):
        super(RoomForm, self).__init__(*args, **kwargs)
        # Puedes personalizar la presentación de los campos aquí, por ejemplo, agregar clases CSS
        self.fields['description'].widget.attrs['rows'] = 4  # Aumenta el número de filas para el campo description

        # Puedes agregar opciones adicionales para el campo estado
        self.fields['state'].widget.attrs['class'] = 'custom-select-class'
        
class RoomFormEdit(forms.ModelForm):
    # Nuevo campo para almacenar la imagen actual
    current_image = forms.ImageField(required=False)

    class Meta:
        model = Room
        fields = ['number', 'image', 'description', 'price', 'ammount', 'state']

    def __init__(self, *args, **kwargs):
        super(RoomFormEdit, self).__init__(*args, **kwargs)
        # Hacer que el campo de imagen sea opcional
        self.fields['image'].required = False
        
class ReservationForm(forms.Form):
    check_in_date = forms.DateField()
    check_out_date = forms.DateField()

    def clean(self):
        cleaned_data = super().clean()
        check_in_date = cleaned_data.get('check_in_date')
        check_out_date = cleaned_data.get('check_out_date')

        if check_in_date and check_out_date:
            if check_in_date <= timezone.now().date():
                raise ValidationError("La fecha de entrada debe ser en el futuro.")
            if check_out_date <= check_in_date:
                raise ValidationError("La fecha de salida debe ser después de la fecha de entrada.")
            
class UpdateReservationStatusForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['status']
