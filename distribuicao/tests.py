
from django.test import TestCase
from django.urls import reverse

from .models import Destino, Noticia, Publicacao


class ModelosDistribuicaoTests(TestCase):
    def setUp(self):
        self.noticia = Noticia.objects.create(
            wordpress_id=987654321,
            titulo="Notícia de teste",
            resumo="Resumo para os testes automatizados.",
            url="https://example.com/noticia-de-teste/",
        )

        self.destino_facebook = Destino.objects.create(
            nome="Página de teste",
            plataforma=Destino.Plataforma.FACEBOOK,
            identificador="pagina-teste",
            ativo=True,
        )

        self.destino_whatsapp = Destino.objects.create(
            nome="Grupo de teste",
            plataforma=Destino.Plataforma.WHATSAPP,
            identificador="destino-teste",
            ativo=True,
        )

    def test_noticia_e_criada_corretamente(self):
        self.assertEqual(self.noticia.titulo, "Notícia de teste")
        self.assertEqual(self.noticia.wordpress_id, 987654321)

    def test_destinos_facebook_e_whatsapp_sao_suportados(self):
        self.assertEqual(
            self.destino_facebook.plataforma,
            "facebook",
        )
        self.assertEqual(
            self.destino_whatsapp.plataforma,
            "whatsapp",
        )

    def test_publicacao_comeca_pendente(self):
        publicacao = Publicacao.objects.create(
            noticia=self.noticia,
            destino=self.destino_facebook,
        )

        self.assertEqual(
            publicacao.status,
            Publicacao.Status.PENDENTE,
        )

    def test_nao_permite_publicacao_duplicada_no_mesmo_destino(self):
        Publicacao.objects.create(
            noticia=self.noticia,
            destino=self.destino_facebook,
        )

        with self.assertRaises(Exception):
            Publicacao.objects.create(
                noticia=self.noticia,
                destino=self.destino_facebook,
            )

    def test_mesma_noticia_pode_ter_dois_destinos(self):
        Publicacao.objects.create(
            noticia=self.noticia,
            destino=self.destino_facebook,
        )

        Publicacao.objects.create(
            noticia=self.noticia,
            destino=self.destino_whatsapp,
        )

        self.assertEqual(
            Publicacao.objects.filter(noticia=self.noticia).count(),
            2,
        )


class DashboardTests(TestCase):
    def test_dashboard_abre(self):
        resposta = self.client.get(reverse("distribuicao:dashboard"))
        self.assertEqual(resposta.status_code, 200)


class CompartilhamentoWhatsAppTests(TestCase):
    def setUp(self):
        self.noticia = Noticia.objects.create(
            wordpress_id=7654321,
            titulo="Matéria de validação",
            resumo="Resumo de validação.",
            url="https://example.com/materia-validacao/",
        )
        self.destino = Destino.objects.create(
            nome="Canal de teste",
            plataforma=Destino.Plataforma.WHATSAPP,
            ativo=True,
        )
        self.publicacao = Publicacao.objects.create(
            noticia=self.noticia,
            destino=self.destino,
        )

    def test_confirmacao_whatsapp_registra_envio_manual(self):
        resposta = self.client.post(
            reverse("distribuicao:marcar_compartilhada", args=[self.publicacao.pk])
        )
        self.assertEqual(resposta.status_code, 302)
        self.publicacao.refresh_from_db()
        self.assertEqual(self.publicacao.status, Publicacao.Status.ENVIADA)
        self.assertIn(self.noticia.url, self.publicacao.mensagem)

    def test_confirmacao_whatsapp_nao_aceita_get(self):
        resposta = self.client.get(
            reverse("distribuicao:marcar_compartilhada", args=[self.publicacao.pk])
        )
        self.assertEqual(resposta.status_code, 405)

    def test_nao_confirma_destino_facebook_com_rota_whatsapp(self):
        facebook = Destino.objects.create(
            nome="Página de teste",
            plataforma=Destino.Plataforma.FACEBOOK,
            ativo=True,
        )
        publicacao = Publicacao.objects.create(noticia=self.noticia, destino=facebook)
        resposta = self.client.post(
            reverse("distribuicao:marcar_compartilhada", args=[publicacao.pk])
        )
        self.assertEqual(resposta.status_code, 404)
