# Central de Distribuição de Notícias — Folha do Vale

Aplicação Django para importar notícias publicadas no WordPress, organizar uma fila por destino e apoiar a distribuição editorial. O compartilhamento pelo WhatsApp é manual: a aplicação prepara/copia o texto e registra uma confirmação feita por uma pessoa. Ela não envia mensagens para grupos ou canais do WhatsApp.

## Requisitos

- Python 3.11 ou compatível com a versão de Django instalada no projeto
- Acesso à internet para consultar o WordPress e publicar no Facebook
- Credenciais da Página do Facebook, caso a integração seja usada

## Instalação local (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py test distribuicao
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para o painel e `http://127.0.0.1:8000/admin/` para administrar notícias, destinos e publicações.

## Importar e montar a fila

```powershell
python manage.py importar_noticias
python manage.py atualizar_fila
```

A importação depende de o WordPress estar acessível e de sua API REST responder. Se o site de origem retornar HTTP 5xx/Cloudflare, isso precisa ser investigado no servidor de origem; o painel não consegue corrigir uma indisponibilidade externa.

## Facebook: proteção contra publicação acidental

A integração existente usa `FACEBOOK_PAGE_ID` e `FACEBOOK_PAGE_ACCESS_TOKEN` no `.env`. Nunca publique tokens em repositórios, capturas de tela ou mensagens. Para pré-visualizar uma publicação específica, use o ID interno da fila:

```powershell
python manage.py publicar_facebook --id ID_DA_PUBLICACAO
```

Esse comando apenas mostra a prévia. O envio real exige acrescentar explicitamente `--confirmar`:

```powershell
python manage.py publicar_facebook --id ID_DA_PUBLICACAO --confirmar
```

Não use `--confirmar` em testes. Antes de repetir uma tentativa com resultado incerto, verifique a página do Facebook para evitar duplicidade. O envio automático agendado não é ativado por este projeto; exige configuração operacional e testes no ambiente do responsável técnico.

## Variáveis de ambiente

Consulte `.env.example`. Em produção, defina uma `DJANGO_SECRET_KEY` forte, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` e os tokens necessários. Não use o servidor `runserver` como servidor de produção.

## O que ainda depende do técnico

1. Confirmar a API REST e a origem das imagens do WordPress; resolver erros de hospedagem/Cloudflare no servidor de origem, se ocorrerem.
2. Configurar credenciais, permissões e validade do token da Meta/Facebook de forma segura.
3. Configurar domínio, HTTPS, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, banco de produção, backups, logs e servidor WSGI/ASGI.
4. Configurar e monitorar a rotina de importação e atualização da fila em produção. Publicação automática só deve ser habilitada depois de aprovação expressa, testes e procedimento de pausa.
5. Testar manualmente o fluxo completo com destinos reais e uma notícia não sensível antes da operação.

## Limitações conhecidas

- WhatsApp: o fluxo é assistido/manual; não existe envio automático para grupos ou canais.
- WordPress: a importação exige API acessível. Imagens aparecem apenas quando a API entrega `imagem_url` válida.
- Facebook: o envio é individual por comando e exige confirmação explícita; não existe rotina automática agendada incluída.
