
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from distribuicao.models import Publicacao
from distribuicao.services.facebook import (
    ErroPublicacaoFacebook,
    publicar_no_facebook,
)


class Command(BaseCommand):
    help = "Publica uma notícia específica no Facebook após confirmação."

    def add_arguments(self, parser):
        parser.add_argument(
            "--id",
            type=int,
            required=True,
            help="ID da publicação na fila.",
        )
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma o envio real para o Facebook.",
        )

    def handle(self, *args, **options):
        publicacao_id = options["id"]

        try:
            publicacao = (
                Publicacao.objects
                .select_related("noticia", "destino")
                .get(pk=publicacao_id)
            )
        except Publicacao.DoesNotExist:
            raise CommandError(
                f"Publicação de ID {publicacao_id} não encontrada."
            )

        if publicacao.destino.plataforma != "facebook":
            raise CommandError("O destino não é o Facebook.")

        if not publicacao.destino.ativo:
            raise CommandError("O destino está inativo.")

        if publicacao.status != Publicacao.Status.PENDENTE:
            raise CommandError(
                f"Status atual: {publicacao.status}. "
                "Somente publicações pendentes podem ser enviadas."
            )

        if publicacao.id_publicacao_externa:
            raise CommandError(
                "Esta publicação já possui ID externo. "
                "O envio foi bloqueado."
            )

        mensagem = publicacao.mensagem.strip()
        if not mensagem:
            mensagem = (
                f"{publicacao.noticia.titulo}\n\n"
                f"{publicacao.noticia.url}"
            )

        self.stdout.write(f"Publicação na fila: {publicacao.pk}")
        self.stdout.write(f"Destino: {publicacao.destino.nome}")
        self.stdout.write(f"Título: {publicacao.noticia.titulo}")
        self.stdout.write(f"URL: {publicacao.noticia.url}")
        self.stdout.write("\nMensagem que será enviada:\n")
        self.stdout.write(mensagem)

        if not options["confirmar"]:
            self.stdout.write(
                self.style.WARNING(
                    "\nPrévia apenas. Nada foi publicado. "
                    "Para enviar, acrescente --confirmar ao comando."
                )
            )
            return

        # Reserva o registro antes da chamada externa para evitar
        # que duas execuções concorrentes enviem a mesma publicação.
        with transaction.atomic():
            registro = (
                Publicacao.objects
                .select_for_update()
                .get(pk=publicacao_id)
            )

            if (
                registro.status != Publicacao.Status.PENDENTE
                or registro.id_publicacao_externa
            ):
                raise CommandError(
                    "O registro mudou ou já foi processado. "
                    "Nenhum envio foi iniciado."
                )

            registro.status = Publicacao.Status.PREPARADA
            registro.mensagem = mensagem
            registro.erro = ""
            registro.save(
                update_fields=[
                    "status",
                    "mensagem",
                    "erro",
                    "atualizada_em",
                ]
            )

        try:
            id_externo = publicar_no_facebook(
    mensagem=publicacao.mensagem,
    link=publicacao.noticia.url,
)

        except ErroPublicacaoFacebook as exc:
            Publicacao.objects.filter(
                pk=publicacao_id,
                status=Publicacao.Status.PREPARADA,
                id_publicacao_externa="",
            ).update(
                status=Publicacao.Status.ERRO,
                erro=str(exc),
            )
            raise CommandError(
                f"Falha ao publicar: {exc}. "
                "Confira a página antes de tentar novamente, "
                "pois uma falha de comunicação pode deixar "
                "o resultado incerto."
            ) from exc

        atualizadas = Publicacao.objects.filter(
            pk=publicacao_id,
            status=Publicacao.Status.PREPARADA,
            id_publicacao_externa="",
        ).update(
            status=Publicacao.Status.ENVIADA,
            id_publicacao_externa=id_externo,
            erro="",
        )

        if not atualizadas:
            self.stdout.write(
                self.style.ERROR(
                    f"O Facebook retornou o ID {id_externo}, "
                    "mas o registro não foi atualizado. "
                    "Não repita o envio sem verificar a página."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Publicação enviada! ID na fila: {publicacao_id}; "
                f"ID no Facebook: {id_externo}"
            )
        )
