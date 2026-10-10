from django.shortcuts import render
from django.utils import timezone

from .models import Destino, Noticia, Publicacao


def dashboard(request):
    hoje = timezone.localdate()

    noticias_de_hoje = Noticia.objects.filter(
        data_publicacao__date=hoje
    )

    # PublicaÃ§Ãµes que ainda precisam de atenÃ§Ã£o em cada destino.
    fila = (
        Publicacao.objects
        .filter(
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

    # HistÃ³rico separado: os registros enviados nÃ£o sÃ£o apagados.
    historico = (
        Publicacao.objects
        .filter(status=Publicacao.Status.ENVIADA)
        .select_related("noticia", "destino")
        .order_by("-atualizada_em")[:10]
    )

    contexto = {
        "total_noticias": noticias_de_hoje.count(),
        "total_destinos": Destino.objects.filter(ativo=True).count(),
        "total_publicacoes": Publicacao.objects.count(),
        "publicacoes_pendentes": fila.count(),
        "ultimas_noticias": noticias_de_hoje.order_by(
            "-data_publicacao"
        )[:10],
        "ultimas_publicacoes": fila[:50],
        "historico_publicacoes": historico,
    }

    return render(request, "distribuicao/dashboard.html", contexto)
