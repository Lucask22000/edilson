# Sistema de Orçamentos para Empresa de Pintura

Projeto web para cadastro de produtos, clientes e geração de orçamentos usando Python, Streamlit e SQLite.

## Recursos principais

- Login administrativo com usuário `admin` e senha `142536`.
- Dashboard com indicadores gerais.
- Cadastro completo de produtos e serviços.
- Cadastro completo de clientes.
- Criação de orçamentos com vários itens.
- Cálculo automático de subtotal, desconto, taxa adicional e total final.
- Consulta de orçamentos com filtros por cliente, status e período.
- Visualização detalhada com exportação em PDF e HTML imprimível.
- Compartilhamento rápido por e-mail e WhatsApp com mensagem pronta.
- Página de configurações para nome da empresa, CNPJ, contatos, nome do app e logo.
- Logo aplicada na interface, nos documentos e no ícone do app quando disponível no navegador/celular.
- Banco de dados SQLite criado automaticamente ao iniciar.

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
|   |-- auth.py
|   `-- calculations.py
`-- pages/
    |-- 1_Produtos_e_Servicos.py
    |-- 2_Clientes.py
    |-- 3_Novo_Orcamento.py
    |-- 4_Orcamentos.py
    `-- 5_Configuracoes.py
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

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o projeto

```bash
streamlit run app.py
```

O banco `orcamentos.db` será criado automaticamente na primeira execução.

## Primeiro acesso

- Login: `admin`
- Senha: `142536`

## Como usar

1. Faça login no sistema.
2. Abra `Configurações` para cadastrar nome da empresa, CNPJ, contatos e a logo.
3. Cadastre ou ajuste produtos e serviços.
4. Cadastre clientes.
5. Abra `Novo Orçamento` para montar e salvar um orçamento.
6. Consulte os registros na página `Orçamentos`.

## Observações técnicas

- O projeto usa Streamlit, SQLite e ReportLab.
- A logo é armazenada no banco de dados.
- A geração de PDF e HTML usa automaticamente os dados cadastrados da empresa.
- Clientes com orçamentos vinculados não podem ser excluídos para preservar histórico.
