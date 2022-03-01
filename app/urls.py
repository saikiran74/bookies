from django.urls import URLPattern, path
from . import views

urlpatterns=[
    path("",views.createaccount,name="createaccount"),
    path("createaccount",views.createaccount,name="createaccount"),
    path("signin",views.signin,name="signin"),
    path("index",views.index,name="index"),
    path("logout",views.logout,name="logout"),
    path("search",views.search,name="search"),
    path("update",views.update,name="update"),
    path("history",views.history,name="history"),
    path('visit/<str:pk>/',views.visit,name='visit'),

]