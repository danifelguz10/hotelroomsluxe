from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'hotel'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<slug:slug>', views.user_detail, name='user_detail'),
    path('signupview/', views.signupview, name='signupview'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    
    
    path('rooms/', views.room_list, name='roomlist'),
    path('rooms/<int:pk>/', views.room_detail, name='roomdetail'),
    path('rooms/create/', views.room_create, name='roomcreate'),
    path('rooms/<int:pk>/update/', views.room_update, name='roomupdate'),       
    path('rooms/<int:pk>/delete/', views.room_delete, name='roomdelete'),
    
    
    path('reservation/', views.reservation_list, name='reservationlist'),
    path('reservation/<int:pk>/', views.reservation_create, name='reservationcreate'),
    path('reservation/update_status/<int:pk>/', views.reservation_update, name='reservationupdate'),
    path('reservation/delete/<int:pk>/', views.reservation_delete, name='reservationdelete'),
    
    path('reservations/user', views.reservation_user, name='reservationuser'),
    path('reservation/cancel/<int:pk>/', views.reservation_cancel, name='reservation_cancel'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)