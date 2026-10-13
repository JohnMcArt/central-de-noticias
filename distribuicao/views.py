from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Destino, Noticia, Publicacao


def dashboard(request):
    hoje = timezone.localdate()
    noticias_de_hoje = Noticia.objects.filter(data_publicacao__date=hoje)

    fila = (
        Publicacao.objects.filter(
            noticia__data_publicacao__date=hoje,
            destino__ativo=True,
            status__in=[
                Publicacao.Status.PENDENTE,
                Publicacao.Status.PREPARADA,
                Publicacao.Status.ERRO,
            ],
        )
        .select_related("noticia", "destino")
        .order_by("noticia__data_publicacao", "destino__nome")
    )

    historico = (
        Publicacao.objects.filter(status=Publicacao.Status.ENVIADA)
        .select_related("noticia", "destino")
        .order_by("-atualizada_em")[:10]
    )

    contexto = {
        "total_noticias": noticias_de_hoje.count(),
        "total_destinos": Destino.objects.filter(ativo=True).count(),
        "total_publicacoes": Publicacao.objects.count(),
        "publicacoes_pendentes": fila.count(),
        "ultimas_noticias": noticias_de_hoje.order_by("-data_publicacao")[:10],
        "ultimas_publicacoes": fila[:50],
        "historico_publicacoes": historico,
    }
    return render(request, "distribuicao/dashboard.html", contexto)


@require_POST
def marcar_compartilhada(request, publicacao_id):
    """Registra confirmação humana de compartilhamento via WhatsApp; não envia mensagem."""
    with transaction.atomic():
        publicacao = get_object_or_404(
            Publicacao.objects.select_for_update().select_related("destino", "noticia"),
            pk=publicacao_id,
            destino__plataforma=Destino.Plataforma.WHATSAPP,
            destino__ativo=True,
        )
        if publicacao.status == Publicacao.Status.ENVIADA:
            messages.info(request, "Esta publicação já estava marcada como compartilhada.")
        elif publicacao.status not in {
            Publicacao.Status.PENDENTE,
            Publicacao.Status.PREPARADA,
            Publicacao.Status.ERRO,
        }:
            messages.error(request, "O status atual não permite confirmar este compartilhamento.")
        else:
            publicacao.status = Publicacao.Status.ENVIADA
            publicacao.erro = ""
            publicacao.mensagem = publicacao.mensagem.strip() or (
                f"📰 {publicacao.noticia.titulo}\n\n{publicacao.noticia.url}"
            )
            publicacao.save(update_fields=["status", "erro", "mensagem", "atualizada_em"])
            messages.success(
                request,
                "Confirmação registrada. O sistema não verifica o WhatsApp; confirme apenas se você enviou a notícia.",
            )
    return redirect("distribuicao:dashboard")
