import requests

from django.conf import settings


GRAPH_API_VERSION = "v23.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class ErroPublicacaoFacebook(Exception):
    """Erro ao enviar uma publicação para o Facebook."""


def publicar_no_facebook(mensagem, link=None):
    """
    Publica texto ou texto com link na página configurada.
    Retorna o ID da publicação criado pelo Facebook.
    """

    page_id = getattr(settings, "FACEBOOK_PAGE_ID", "")
    access_token = getattr(
        settings, "FACEBOOK_PAGE_ACCESS_TOKEN", ""
    )

    if not page_id or not access_token:
        raise ErroPublicacaoFacebook(
            "Configure FACEBOOK_PAGE_ID e "
            "FACEBOOK_PAGE_ACCESS_TOKEN no ambiente."
        )

    if not mensagem or not mensagem.strip():
        raise ErroPublicacaoFacebook(
            "A mensagem da publicação está vazia."
        )

    dados_envio = {
        "message": mensagem.strip(),
        "access_token": access_token,
    }

    if link:
        dados_envio["link"] = link.strip()

    url = f"{GRAPH_API_BASE}/{page_id}/feed"

    try:
        resposta = requests.post(
            url,
            data=dados_envio,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise ErroPublicacaoFacebook(
            f"Falha de comunicação com o Facebook: {exc}"
        ) from exc

    try:
        dados = resposta.json()
    except ValueError as exc:
        raise ErroPublicacaoFacebook(
            f"O Facebook retornou uma resposta inválida "
            f"(HTTP {resposta.status_code})."
        ) from exc

    if not resposta.ok or not dados.get("id"):
        detalhe = dados.get("error", {}).get(
            "message",
            "Resposta sem ID de publicação.",
        )
        raise ErroPublicacaoFacebook(
            f"Facebook HTTP {resposta.status_code}: {detalhe}"
        )

    return dados["id"]
