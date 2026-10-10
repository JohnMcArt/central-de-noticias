from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from distribuicao.models import Destino, Noticia, Publicacao


class Command(BaseCommand):
    help = "Adiciona à fila as notícias de hoje para cada destino ativo."

    def handle(self, *args, **options):
        fuso = timezone.get_current_timezone()
        hoje = timezone.localdate()

        inicio = timezone.make_aware(
            datetime.combine(hoje, time.min),
            fuso,
        )
        fim = timezone.make_aware(
            datetime.combine(hoje + timedelta(days=1), time.min),
            fuso,
        )

        noticias = Noticia.objects.filter(
            data_publicacao__gte=inicio,
            data_publicacao__lt=fim,
        ).order_by("data_publicacao")

        destinos = Destino.objects.filter(ativo=True)

        criadas = 0
        existentes = 0

        if not destinos.exists():
            self.stdout.write(
                self.style.WARNING(
                    "Nenhum destino ativo. Cadastre ou ative um destino no admin."
                )
            )
            return

        for noticia in noticias:
            for destino in destinos:
                publicacao, criada = Publicacao.objects.get_or_create(
                    noticia=noticia,
                    destino=destino,
                    defaults={
                        "status": Publicacao.Status.PENDENTE,
                    },
                )

                if criada:
                    criadas += 1
                    self.stdout.write(
                        f"Na fila: {noticia.titulo} -> {destino.nome}"
                    )
                else:
                    existentes += 1

        self.stdout.write(
            self.style.SUCCESS(
                "\nAtualização da fila concluída."
                f"\nData considerada: {hoje}"
                f"\nNotícias de hoje: {noticias.count()}"
                f"\nDestinos ativos: {destinos.count()}"
                f"\nPublicações novas na fila: {criadas}"
                f"\nPublicações que já existiam: {existentes}"
            )
        )