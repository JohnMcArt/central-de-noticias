
import html
import re
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.utils import timezone


def limpar_html(texto):
    """Remove tags HTML e normaliza espaços."""
    texto = re.sub(r"<[^>]+>", " ", texto or "")
    texto = html.unescape(texto)
    return " ".join(texto.split())


def buscar_noticias(site_url, quantidade=None):
    """
    Busca notícias publicadas no dia atual,
    incluindo a imagem destacada do WordPress.
    """
    fuso = ZoneInfo(settings.TIME_ZONE)
    hoje = timezone.localdate()

    inicio = datetime.combine(hoje, time.min, tzinfo=fuso)
    fim = datetime.combine(
        hoje + timedelta(days=1),
        time.min,
        tzinfo=fuso,
    )

    base_url = site_url.rstrip("/")
    endpoint = f"{base_url}/wp-json/wp/v2/posts"

    parametros_base = {
        "status": "publish",
        "per_page": 100,
        "orderby": "date",
        "order": "asc",
        "after": (inicio - timedelta(seconds=1)).isoformat(),
        "before": fim.isoformat(),
        "_embed": "wp:featuredmedia",
        "_fields": "id,date,date_gmt,link,title,excerpt,_embedded",
    }

    noticias = []
    pagina = 1

    while True:
        parametros = {
            **parametros_base,
            "page": pagina,
        }

        resposta = requests.get(
            endpoint,
            params=parametros,
            timeout=30,
            headers={"User-Agent": "CentralNoticias/1.0"},
        )
        resposta.raise_for_status()
        posts = resposta.json()

        if not posts:
            break

        for post in posts:
            data_texto = post.get("date")
            if not data_texto:
                continue

            data_post = datetime.fromisoformat(data_texto)

            if timezone.is_naive(data_post):
                data_post = data_post.replace(tzinfo=fuso)

            data_local = data_post.astimezone(fuso)

            # Nunca aceitar notícias de outro dia.
            if data_local.date() != hoje:
                continue

            incorporados = post.get("_embedded", {})
            midias = incorporados.get("wp:featuredmedia", [])

            imagem_url = ""
            if midias:
                imagem_url = midias[0].get("source_url", "") or ""

            noticias.append({
                "wordpress_id": post["id"],
                "titulo": limpar_html(post["title"]["rendered"]),
                "resumo": limpar_html(post["excerpt"]["rendered"]),
                "url": post["link"],
                "imagem_url": imagem_url,
                "data_publicacao": data_post.isoformat(),
            })

        total_paginas = int(
            resposta.headers.get("X-WP-TotalPages", pagina)
        )

        if pagina >= total_paginas:
            break

        pagina += 1

    return noticias
