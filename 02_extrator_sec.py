import requests
from bs4 import BeautifulSoup
import os
import re

def obter_cik(ticker):
    print(f"[1] Traduzindo Ticker '{ticker.upper()}' para CIK da SEC...")
    url = "https://www.sec.gov/files/company_tickers.json"
    
    # A SEC exige um User-Agent formal em formato corporativo, senão eles dão block na hora.
    headers = {'User-Agent': 'StefaniniConsulting (estudos@stefanini.com)'}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        dados = r.json()
        
        for key, value in dados.items():
            if value['ticker'].upper() == ticker.upper():
                cik = str(value['cik_str']).zfill(10)
                print(f"[SUCESSO] CIK encontrado: {cik}")
                return cik
                
        print(f"[WARNING] Ticker {ticker.upper()} não encontrado na base oficial americana.")
        return None
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao acessar base da SEC: {str(e)}")
        return None

def buscar_url_ultimo_relatorio(cik):
    print("[2] Vasculhando a base do EDGAR pelo último relatório anual (10-K)...")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {'User-Agent': 'StefaniniConsulting (estudos@stefanini.com)'}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        dados = r.json()
        filings = dados.get('filings', {}).get('recent', {})
        
        for i, form in enumerate(filings.get('form', [])):
            if form == '10-K':
                accession_number = filings['accessionNumber'][i].replace('-', '')
                primary_document = filings['primaryDocument'][i]
                url_doc = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_document}"
                print("[SUCESSO] Relatório 10-K corporativo localizado.")
                return url_doc
                
        print("[WARNING] Nenhum formulário 10-K recente foi encontrado para esta empresa.")
        return None
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao buscar relatório na estrutura JSON: {str(e)}")
        return None

def extrair_e_limpar_texto(url, ticker):
    print(f"[3] Baixando e dissecando o documento da SEC para {ticker.upper()}...")
    headers = {'User-Agent': 'StefaniniConsulting (estudos@stefanini.com)'}
    
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        texto_completo = soup.get_text(separator=' ', strip=True)
        
        print("[*] Aplicando filtro tático: Extraindo apenas a seção MD&A do relatório...")
        
        # ==============================================================================
        # NOTA DE ARQUITETURA PARA FUTURAS ATUALIZAÇÕES:
        # Quando a empresa aprovar a migração para um modelo LLM fundacional mais robusto
        # (ex: Claude 3.5 Sonnet, Gemini 1.5 Pro ou GPT-4o) que possua janela de contexto
        # gigantesca, VOCÊ PODE E DEVE REMOVER ESTE CORTE COM REGEX e enviar o texto_completo.
        # Atualmente, o modelo de fôlego curto ("Mini") exige extração focada apenas no Item 7 
        # (Management's Discussion and Analysis) para não esgotar a cota de tokens.
        # ==============================================================================
        
        # Expressão Regular agressiva: Captura tudo entre o "Item 7." e o "Item 8."
        padrao = re.compile(r"(?i)ITEM\s+7\.(.*?)ITEM\s+8\.", re.DOTALL)
        resultados = padrao.findall(texto_completo)
        
        texto_final = texto_completo
        
        if resultados:
            # Pegamos o maior bloco de texto. Isso evita que o código extraia a linha 
            # do "Item 7" lá na página de Sumário e ignore o texto real que vem páginas depois.
            file_mignon = max(resultados, key=len)
            
            if len(file_mignon) > 5000:
                texto_final = "--- FILÉ MIGNON DO 10-K (ITEM 7: MD&A) ---\n" + file_mignon
                print(f"[SUCESSO] Secão Item 7 isolada com perfeição. Contexto limpo garantido.")
            else:
                print("[WARNING] O corte isolou um bloco muito pequeno. Aplicando limite de segurança.")
                texto_final = texto_completo[:15000]
        else:
            print("[WARNING] Relatório fora do padrão de formatação. Aplicando limite de segurança bruto.")
            texto_final = texto_completo[:15000]
            
        os.makedirs("clean", exist_ok=True)
        caminho_arquivo = f"clean/{ticker.upper()}_relatorio_anual.txt"
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_final)
            
        tamanho_mb = len(texto_final) / (1024 * 1024)
        print(f"[INFO] Arquivo salvo em '{caminho_arquivo}' ({tamanho_mb:.2f} MB de texto destilado).")
        return caminho_arquivo
        
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao dissecar o documento original: {str(e)}")
        return None