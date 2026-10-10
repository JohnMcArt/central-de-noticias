
$ErrorActionPreference = "Stop"

$PastaProjeto = "C:\Users\Micro\Desktop\central-de-noticias"
$Python = Join-Path $PastaProjeto ".venv\Scripts\python.exe"
$Log = Join-Path $PastaProjeto "monitoramento.log"

Set-Location $PastaProjeto

"=== Inicio: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss') ===" |
    Out-File -FilePath $Log -Append -Encoding utf8

try {
    if (-not (Test-Path $Python)) {
        throw "Python do ambiente virtual não encontrado: $Python"
    }

    "Iniciando importação de notícias..." |
        Out-File -FilePath $Log -Append -Encoding utf8

    & $Python manage.py importar_noticias *>> $Log

    if ($LASTEXITCODE -ne 0) {
        throw "O comando importar_noticias falhou. Código: $LASTEXITCODE"
    }

    "Atualizando fila de publicações..." |
        Out-File -FilePath $Log -Append -Encoding utf8

    & $Python manage.py atualizar_fila *>> $Log

    if ($LASTEXITCODE -ne 0) {
        throw "O comando atualizar_fila falhou. Código: $LASTEXITCODE"
    }

    "Execução concluída com sucesso." |
        Out-File -FilePath $Log -Append -Encoding utf8
}
catch {
    "ERRO: $($_.Exception.Message)" |
        Out-File -FilePath $Log -Append -Encoding utf8
}
finally {
    "=== Fim: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss') ===" |
        Out-File -FilePath $Log -Append -Encoding utf8

    "`r`n" | Out-File -FilePath $Log -Append -Encoding utf8
}