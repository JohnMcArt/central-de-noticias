from django.urls import path
from . import views

app_name = "distribuicao"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path(
        "publicacao/<int:publicacao_id>/marcar-compartilhada/",
        views.marcar_compartilhada,
        name="marcar_compartilhada",
    ),
]
