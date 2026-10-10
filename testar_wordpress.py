
from django.conf import settings

from distribuicao.services.wordpress import buscar_noticias


if __name__ == "__main__":
    noticias = buscar_noticias(
        settings.WORDPRESS_URL,
        quantidade=5,
    )

    print(f"\nNotícias encontradas: {len(noticias)}\n")

    for noticia in noticias:
        print("-" * 60)
        print("ID:", noticia["wordpress_id"])
        print("Título:", noticia["titulo"])
        print("Resumo:", noticia["resumo"][:200])
        print("Link:", noticia["url"])
