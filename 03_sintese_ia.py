import os
import json
import re
import requests
from dotenv import load_dotenv

# Inicialização de variáveis de ambiente e credenciais
load_dotenv()

def ler_arquivo_limpo(alvo):
    """
    Localiza e carrega os dados corporativos extraídos em texto plano.
    Varre os diretórios de saída (output/clean) em busca de dados nacionais (B3) ou internacionais (SEC).
    """
    caminho_cvm = f"output/{alvo.lower()}_dados.txt"
    caminho_sec = f"clean/{alvo.upper()}_relatorio_anual.txt"
    
    if os.path.exists(caminho_cvm):
        with open(caminho_cvm, 'r', encoding='utf-8') as f:
            return f.read()
    elif os.path.exists(caminho_sec):
        with open(caminho_sec, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def analisar_com_claude(texto_cru, alvo):
    """
    Submete os dados brutos à API de Inteligência Artificial para estruturação do laudo executivo.
    """
    api_key = os.getenv("SAI_API_KEY")
    
    if not api_key:
        print("[ERRO CRÍTICO] Falha de Autenticação: SAI_API_KEY não localizada no ambiente (.env).")
        return False

    # ==============================================================================
    # DÍVIDA TÉCNICA / NOTA DE ARQUITETURA PARA FUTURAS ATUALIZAÇÕES:
    # A atual restrição agressiva de tamanho ("máximo de 3 frases", "1 ação curta")
    # existe EXCLUSIVAMENTE para contornar o limite de tokens de saída (output limit)
    # da chave de testes atual / modelo "mini". 
    #
    # AÇÃO REQUERIDA NA ATUALIZAÇÃO DA API: 
    # Quando o sistema for integrado a um LLM de grau corporativo e maior janela de contexto,
    # REMOVA as regras de "seja extremamente breve" e permita que a Inteligência Artificial 
    # gere parágrafos aprofundados e analíticos em cada chave do JSON.
    # ==============================================================================

    prompt_consultor = """
    Você é um consultor de Estratégia de Negócios e Turnaround de altíssimo nível. Sua abordagem é cirúrgica, pragmática e friamente analítica.
    Sua missão é ler dados financeiros ou operacionais de empresas para mapear a real situação da companhia. Não destrua a empresa gratuitamente, mas não mascare a realidade matemática.
    
    Lembre-se: a diretoria não é amadora. Eles sabem que têm problemas e já estão agindo. O seu diferencial é entender o que eles já estão tentando mudar e apontar cirurgicamente onde o plano deles é insuficiente ou lento demais.
    
    =========================================
    ARSENAL DE SOLUÇÕES (PORTFÓLIO STEFANINI):
    Para o pitch final, você DEVE cruzar a dor encontrada com UMA ou no máximo DUAS soluções exatas desta lista. NUNCA invente um serviço que não esteja aqui.
    
    - Applications: App Development/Maintenance, App Modernization, App Performance, Architecture/APIs & Integrations, Digital Product/Platform Engineering, Quality & Testing.
    - Cloud Services: Adoption, Advisory, Management & Optimization, Migration, Modernization, Native Apps, Public Cloud Re-selling.
    - Hybrid Infrastructure: Data Center, Database & Middleware, Edge Computing, Hybrid Infra Operations, Intelligent Networks/Telecom, Private/Hybrid Cloud Services.
    - Digital Workplace: Collaboration & Communication, Field Services, IT Asset Management, ITSM & SIAM, Managed Endpoint, Service Desk, Workplace Automation.
    - Enterprise Platforms: Advisory, AMS & Improvement, Implementation.
    - Cybersecurity: App Security, Cloud Security, Cyber OT, Advisory, Managed Services, Data Privacy/Security, GRC, IT Infra Security, Threat Readiness/Mitigation.
    - Data & Analytics: Data Architecture/Engineering, Data Governance, Data Science, Data-driven Transformation, Insights/Democratization.
    - Commerce & Marketing: Advertising, Agile Research, Commerce & DXP, Content/Social, CRM/Loyalty, Design, Full Funnel Media, Martech.
    - Smart Manufacturing & Supply Chain: Automation/Robotics, Digital Manufacturing Advisory, Manufacturing Apps/Analytics/Optimization, Supply Chain Optimization.
    - Financial & Payments (Topaz One/ATM): ATM Cash Reduction, Cash Management, BaaS, Card/Payment Processing, Antifraud, Core Banking, Open Finance, Origination.
    - Operations: BPO (Business Process Outsourcing), BPO Customer Services, BPO Legal, Hyperautomation Implementation.
    - Consulting Services: Benchmarking & Diagnosis, Business Efficiency, Change Management, Technology Strategy & Transformation.
    =========================================
    
    Você DEVE retornar a sua resposta EXCLUSIVAMENTE em um JSON válido com a seguinte estrutura:
    {
      "diagnostico_frio": "Análise executiva incisiva (máximo de 3 frases) apontando margens, estrutura de capital e o real problema financeiro.",
      "movimentos_estrategicos": [
        "Ação 1 que a empresa está tentando fazer para se salvar/otimizar.",
        "Ação 2 detalhando onde eles estão alocando esforço hoje."
      ],
      "focos_de_sangramento": [
        "Gargalo 1 detalhado (onde estão queimando caixa ou perdendo eficiência).",
        "Gargalo 2 detalhado (qual processo interno está travando a empresa)."
      ],
      "oportunidade_insercao": "Pitch de vendas agressivo e inteligente cruzando as dores acima com um serviço específico do nosso 'ARSENAL DE SOLUÇÕES'. Justifique o ROI dessa inserção. (Máximo de 3 frases)."
    }

    REGRAS RÍGIDAS DE FORMATAÇÃO E LIMITES (RISCO CRÍTICO):
    1. SEJA PROFUNDO, MAS CIRÚRGICO. O seu limite de resposta é curto. Entregue valor denso em poucas frases para não ter a conexão cortada.
    2. USE ASPAS DUPLAS (") estritamente para envolver as chaves e os valores principais do JSON.
    3. NUNCA use aspas duplas dentro do texto de resposta. Se precisar destacar ou citar um termo, use aspas simples (').
    4. NUNCA quebre linhas (\n) no meio das strings. Todo o texto de um campo deve ser contínuo.
    5. Retorne APENAS o JSON. Zero texto de introdução ou conclusão.
    """
    
    url = "https://sai-library.saiapplications.com/api/templates/643388be603840da1c23b1b7/execute"
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": {
            "text": texto_cru,
            "question": prompt_consultor
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            texto_bruto = response.text
            
            # ==============================================================================
            # BLINDAGEM DE INTERFACE (FALLBACK):
            # Previne falha de parsing caso o payload retorne formato raw text ao invés de JSON.
            # ==============================================================================
            try:
                dados_retorno = response.json()
                if isinstance(dados_retorno, dict):
                    texto_ia = str(dados_retorno.get("output", dados_retorno.get("result", dados_retorno.get("answer", texto_bruto))))
                else:
                    texto_ia = str(dados_retorno)
            except json.JSONDecodeError:
                texto_ia = texto_bruto
                
            # Limpeza de artefatos Markdown para assegurar integridade no parse
            texto_ia = re.sub(r"^```json\s*", "", texto_ia, flags=re.IGNORECASE)
            texto_ia = re.sub(r"^```\s*", "", texto_ia)
            texto_ia = re.sub(r"\s*```$", "", texto_ia)
            texto_ia = texto_ia.strip()
            
            # Validação estrutural de integridade do payload gerado
            try:
                json.loads(texto_ia)
            except json.JSONDecodeError:
                print("\n[ERRO CRÍTICO] Falha de formatação: A resposta gerada não representa um JSON interpretável.")
                print(f"[DEBUG LOG] Estrutura residual da inferência:\n{texto_ia}\n")
                return False

            # Gravação do artefato validado
            caminho_laudo = f"output/{alvo.lower()}_laudo.json"
            os.makedirs("output", exist_ok=True)
            
            with open(caminho_laudo, 'w', encoding='utf-8') as f:
                f.write(texto_ia)
                
            print(f"[SUCESSO] Processamento cognitivo concluído. Artefato disponível em: {caminho_laudo}")
            return True
            
        else:
            print(f"[ERRO] Falha de comunicação com o endpoint de IA. HTTP Status: {response.status_code}")
            print(f"[DEBUG LOG] Diagnóstico do servidor: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERRO CRÍTICO] Timeout ou interrupção na infraestrutura de rede: {str(e)}")
        return False