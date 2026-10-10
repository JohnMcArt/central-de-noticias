from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from distribuicao.models import Noticia
from distribuicao.services.wordpress import buscar_noticias


class Command(BaseCommand):
    help = "Importa as notícias publicadas no dia atual."

    def handle(self, *args, **options):
        try:
            noticias = buscar_noticias(settings.WORDPRESS_URL)
        except Exception as erro:
            raise CommandError(
                f"Falha ao consultar o WordPress: {erro}"
            ) from erro

        novas = 0
        atualizadas = 0
        ignoradas = 0

        hoje = timezone.localdate()

        for dados in noticias:
            try:
                data_publicacao = datetime.fromisoformat(
                    dados["data_publicacao"]
                )

                if timezone.is_naive(data_publicacao):
                    data_publicacao = timezone.make_aware(
                        data_publicacao,
                        timezone.get_current_timezone(),
                    )

                data_local = timezone.localtime(data_publicacao)

                # Barreira adicional contra notícias de outros dias.
                if data_local.date() != hoje:
                    ignoradas += 1
                    continue

                
                imagem_url = (dados.get("imagem_url") or "").strip()

                defaults = {
                    "titulo": dados["titulo"],
                    "resumo": dados["resumo"],
                    "url": dados["url"],
                    "data_publicacao": data_publicacao,
                }

                # Não apaga uma imagem existente se a API retornar vazio.
                if imagem_url:
                    defaults["imagem_url"] = imagem_url

                noticia, criada = Noticia.objects.update_or_create(
                    wordpress_id=dados["wordpress_id"],
                    defaults=defaults,
                )


                if criada:
                    novas += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Nova notícia: {noticia.titulo}"
                        )
                    )
                else:
                    atualizadas += 1

            except Exception as erro:
                ignoradas += 1
                self.stderr.write(
                    self.style.ERROR(
                        f"Erro na notícia {dados.get('wordpress_id')}: {erro}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\nColeta concluída."
                f"\nData local: {hoje}"
                f"\nNovas notícias: {novas}"
                f"\nAtualizadas: {atualizadas}"
                f"\nIgnoradas: {ignoradas}"
            )
        )