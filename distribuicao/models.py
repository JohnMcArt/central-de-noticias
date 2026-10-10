
from django.db import models


class Noticia(models.Model):
    wordpress_id = models.PositiveBigIntegerField(
        unique=True,
        verbose_name="ID no WordPress",
    )
    titulo = models.CharField(
        max_length=500,
        verbose_name="Título",
    )
    resumo = models.TextField(
        blank=True,
        verbose_name="Resumo",
    )
    url = models.URLField(
        max_length=1000,
        unique=True,
        verbose_name="Link da notícia",
    )
    imagem_url = models.URLField(
        max_length=1000,
        blank=True,
        verbose_name="URL da imagem",
    )
    data_publicacao = models.DateTimeField(
    blank=True,
    null=True,
    verbose_name="Data de publicação",
)
    detectada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de importação",
    )

    class Meta:
        ordering = ["-data_publicacao"]
        verbose_name = "Notícia"
        verbose_name_plural = "Notícias"

    def __str__(self):
        return self.titulo


class Destino(models.Model):
    class Plataforma(models.TextChoices):
        FACEBOOK = "facebook", "Facebook"
        WHATSAPP = "whatsapp", "WhatsApp"
        OUTRO = "outro", "Outro"

    nome = models.CharField(
        max_length=150,
        verbose_name="Nome do destino",
    )
    plataforma = models.CharField(
        max_length=20,
        choices=Plataforma.choices,
        verbose_name="Plataforma",
    )
    identificador = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Identificador do destino",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Destino ativo",
    )
    compartilhamento_assistido = models.BooleanField(
        default=False,
        verbose_name="Compartilhamento assistido",
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Destino"
        verbose_name_plural = "Destinos"

    def __str__(self):
        return f"{self.nome} ({self.get_plataforma_display()})"


class Publicacao(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        PREPARADA = "preparada", "Preparada"
        ENVIADA = "enviada", "Enviada"
        ERRO = "erro", "Erro"

    noticia = models.ForeignKey(
        Noticia,
        on_delete=models.CASCADE,
        related_name="publicacoes",
        verbose_name="Notícia",
    )
    destino = models.ForeignKey(
        Destino,
        on_delete=models.CASCADE,
        related_name="publicacoes",
        verbose_name="Destino",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status",
    )
    mensagem = models.TextField(
        blank=True,
        verbose_name="Mensagem preparada",
    )
    erro = models.TextField(
        blank=True,
        verbose_name="Detalhes do erro",
    )

    id_publicacao_externa = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="ID da publicação externa",
    )

    criada_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criada em",
    )
    atualizada_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Última atualização",
    )

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "Publicação"
        verbose_name_plural = "Publicações"
        constraints = [
            models.UniqueConstraint(
                fields=["noticia", "destino"],
                name="publicacao_unica_por_noticia_destino",
            ),
        ]

    def __str__(self):
        return f"{self.noticia.titulo} → {self.destino.nome}"
