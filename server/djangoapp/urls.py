from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # route is a string contains a URL pattern
    # view refers to the view function
    # name the URL
    #path('', views.index, name='index'),
    path('static/', views.static_view, name='static'),
    # path for about view
    #path('', views.index, name='index'),
    
    path('about/', views.about, name='about'),

    # path for contact us view
    path('contact/', views.contact, name='contact'),
    # path for registration
    path('signup/', views.signup, name='signup'),

    # path for login
    path('login/', views.login_view, name='login'),
    # path for logout
    path('logout/', views.logout_view, name='logout'),
    path(route='', view=views.get_dealerships, name='index'),

    # path for dealer reviews view

    # path for add a review view

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)