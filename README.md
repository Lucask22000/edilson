# Sistema de Orcamentos para Empresa de Pintura

Projeto web simples e funcional para cadastro de produtos, clientes e geracao de orcamentos usando Python, Streamlit e SQLite.

## Recursos principais

- Dashboard com indicadores gerais.
- Cadastro completo de produtos e servicos.
- Cadastro completo de clientes.
- Criacao de orcamentos com varios itens.
- Calculo automatico de subtotal, desconto, taxa adicional e total final.
- Consulta de orcamentos com filtros por cliente, status e periodo.
- Visualizacao detalhada com exportacao em PDF e HTML imprimivel.
- Compartilhamento rapido por e-mail e WhatsApp com mensagem pronta.
- Banco de dados SQLite criado automaticamente ao iniciar.
- Dados de exemplo opcionais para teste rapido.

## Estrutura do projeto

```text
.
|-- app.py
|-- database.py
|-- models.py
|-- requirements.txt
|-- README.md
|-- utils.py
|-- services/
|   `-- calculations.py
`-- pages/
    |-- 1_Produtos_e_Servicos.py
    |-- 2_Clientes.py
    |-- 3_Novo_Orcamento.py
    `-- 4_Orcamentos.py
```

## Como executar localmente

### 1. Criar ambiente virtual

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Rodar o projeto

```bash
streamlit run app.py
```

O banco `orcamentos.db` sera criado automaticamente na primeira execucao.

## Como usar

1. Acesse a pagina inicial para ver o dashboard.
2. Opcionalmente, clique em `Popular dados de exemplo` no painel.
3. Cadastre ou ajuste produtos e servicos.
4. Cadastre clientes.
5. Abra `Novo orcamento` para montar e salvar um orcamento.
6. Consulte os registros na pagina `Orcamentos`.

## Hospedagem no Streamlit Community Cloud

1. Envie os arquivos para um repositorio Git.
2. No Streamlit Community Cloud, crie um novo app apontando para este repositorio.
3. Defina `app.py` como arquivo principal.
4. O `requirements.txt` sera usado para instalar as dependencias automaticamente.

## Observacoes tecnicas

- O projeto usa apenas Streamlit e SQLite.
- A geracao de PDF usa a biblioteca `reportlab`.
- O banco e local, ideal para prototipos, pequenas operacoes e hospedagem simples.
- Os itens do orcamento guardam uma copia do nome, unidade e preco usado no momento do cadastro do orcamento.
- Clientes com orcamentos vinculados nao podem ser excluidos para preservar historico.

## Melhorias futuras sugeridas

- Edicao completa de orcamentos ja salvos.
- Exportacao PDF nativa.
- Autenticacao de usuarios.
- Backup automatico do banco.
