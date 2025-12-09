
from django.urls import path
from . import views

urlpatterns = [
   path("login/",views.login),
   path("complaints/",views.getlist),
   path("complaints/add/",views.add),
   path("complaints/update/<int:id>/",views.update),
   path("complaints/delete/<int:id>/",views.delete),
]
