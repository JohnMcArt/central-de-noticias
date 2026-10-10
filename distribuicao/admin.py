
from django.contrib import admin

from .models import Destino, Noticia, Publicacao


@admin.register(Noticia)
class NoticiaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "wordpress_id", "data_publicacao")
    search_fields = ("titulo", "resumo")
    list_filter = ("data_publicacao",)
    readonly_fields = ("detectada_em",)


@admin.register(Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "plataforma",
        "ativo",
        "compartilhamento_assistido",
    )
    list_filter = ("plataforma", "ativo")


@admin.register(Publicacao)
class PublicacaoAdmin(admin.ModelAdmin):
    list_display = (
        "noticia",
        "destino",
        "status",
        "criada_em",
    )
    list_filter = ("status", "destino")
    search_fields = ("noticia__titulo", "destino__nome")
    readonly_fields = ("criada_em", "atualizada_em")
