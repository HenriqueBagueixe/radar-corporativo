Beleza. Tudo em um bloco só para facilitar a sua vida. Sinceramente, se o próximo desenvolvedor não conseguir rodar o projeto com um `README` mastigado desse jeito, ele não deveria nem estar encostando no código.

Clica no botão de copiar no canto superior direito e joga direto lá no repositório.

```markdown
# 🎯 Radar de Diagnóstico Corporativo

Ferramenta automatizada de inteligência de mercado desenvolvida para realizar o mapeamento rápido da saúde financeira e de riscos operacionais de empresas listadas na bolsa (Nacional/B3 e Internacional/SEC). 

O sistema extrai balanços e relatórios oficiais em tempo real, higieniza os dados e utiliza Inteligência Artificial (LLM) para cruzar as dores corporativas identificadas com o portfólio de soluções de tecnologia e negócios, gerando um pitch de turnaround cirúrgico e direcionado.

## 🏗️ Arquitetura do Sistema

O projeto adota uma arquitetura modular para evitar acoplamento desnecessário e facilitar a manutenção:

*   **`app.py`:** Motor visual (Front-end) construído em Streamlit. Gerencia a interface, os inputs e a renderização do laudo final em tela.
*   **`04_scrapper_nacional.py`:** Extrator do mercado nacional. Utiliza `cloudscraper` para contornar proteções WAF/Cloudflare e raspar os balanços mastigados da B3 em tempo real.
*   **`02_extrator_sec.py`:** Extrator do mercado internacional. Conecta-se à API EDGAR da SEC (EUA) para buscar e dissecar relatórios anuais (10-K), isolando as seções críticas (MD&A).
*   **`03_sintese_ia.py`:** Cérebro cognitivo. Recebe a matriz financeira limpa, aplica o prompt de consultoria estratégica e consome a API de IA da infraestrutura corporativa para gerar o JSON final do laudo.

## 🚀 Pré-requisitos e Instalação

### 1. Preparando o Ambiente
Para não poluir a máquina com dependências globais, o uso de um ambiente virtual (`venv`) é estritamente recomendado.

```bash
# Criação do ambiente virtual
python -m venv venv

# Ativação (Windows)
venv\Scripts\activate

# Ativação (Linux/Mac)
source venv/bin/activate

```

### 2. Instalando as Dependências

Com o ambiente ativado, instale as bibliotecas mapeadas no projeto:

```bash
pip install -r requirements.txt

```

*(Caso o `requirements.txt` apresente falhas, certifique-se de que os pacotes essenciais estão na máquina: `streamlit`, `pandas`, `cloudscraper`, `beautifulsoup4`, `requests`, `python-dotenv`, `lxml`, `html5lib`)*.

## 🔐 Configuração de Segurança (.env)

**ATENÇÃO:** Por motivos óbvios de segurança e compliance, a chave da API de Inteligência Artificial **não está e nunca deve ser comitada** neste repositório.

Para rodar o projeto localmente, crie um arquivo chamado `.env` na raiz do diretório contendo a seguinte credencial:

```env
SAI_API_KEY="SUA_CHAVE_DE_API_AQUI"

```

O módulo `03_sintese_ia.py` fará a leitura e injeção automática dessa chave em tempo de execução.

## ⚙️ Como Executar

Com as dependências instaladas e as chaves configuradas, suba o servidor local:

```bash
streamlit run app.py

```

A interface gráfica ficará disponível no navegador em `http://localhost:8501`.

### Guia de Uso Básico:

1. **Nacional:** Selecione "Nacional (B3)", insira o Ticker oficial da empresa (ex: `BBAS3` ou `PETR4`) e execute.
2. **Internacional:** Selecione "Internacional (SEC)", insira o Ticker da bolsa americana (ex: `TSLA` ou `AMZN`) e execute.
