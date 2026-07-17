import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
import os
import io

def extrair_dados_reais(ticker):
    """
    Extrai indicadores financeiros e balanços de empresas da B3.
    Utiliza CloudScraper para contornar proteções de WAF/Cloudflare.
    """
    print(f"[INFO] Iniciando extração de dados para o ativo: {ticker.upper()}")
    
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    url = f"https://www.fundamentus.com.br/detalhes.php?papel={ticker.upper()}"
    
    try:
        resposta = scraper.get(url)
        
        if "Verifique se você é um humano" in resposta.text or resposta.status_code != 200:
            print(f"[ERRO] Requisição bloqueada pelo servidor de origem. Status: {resposta.status_code}")
            return None
            
        soup = BeautifulSoup(resposta.text, 'html.parser')
        
        # Validação de integridade da base de dados
        if "mudou para" in soup.text:
            novo_ticker = soup.find('a').text if soup.find('a') else "Desconhecido"
            print(f"[WARNING] O ativo consultado foi alterado para {novo_ticker} na base de origem.")
            return None
            
        if "Nenhum papel encontrado" in soup.text or "not found" in soup.text:
            print(f"[WARNING] Ticker {ticker.upper()} não localizado na base de dados.")
            return None
            
        print("[INFO] Processando tabelas financeiras HTML...")
        
        try:
            # io.StringIO evita erro de leitura de path no Pandas ao receber HTML em formato string
            tabelas = pd.read_html(io.StringIO(resposta.text), decimal=',', thousands='.')
        except ValueError:
            print("[ERRO] Nenhuma tabela de dados financeiros estruturada foi encontrada.")
            return None
        
        linhas_dossie = [
            f"--- DOSSIÊ FINANCEIRO CORPORATIVO (MERCADO NACIONAL) ---",
            f"ALVO: {ticker.upper()}",
            "STATUS DOS DADOS: Extração em Tempo Real\n"
        ]
        
        for tab in tabelas:
            tab = tab.dropna(how='all') 
            linhas_dossie.append(tab.to_csv(index=False, header=False, sep='|'))
            linhas_dossie.append("-" * 50)
            
        texto_final = "\n".join(linhas_dossie)
        
        os.makedirs("output", exist_ok=True)
        caminho_arquivo = f"output/{ticker.upper()}_dados.txt"
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            f.write(texto_final)
            
        print(f"[SUCESSO] Arquivo de dados consolidado salvo em: {caminho_arquivo}")
        return caminho_arquivo
        
    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha na execução do extrator: {str(e)}")
        return None

if __name__ == "__main__":
    # Teste de execução local
    extrair_dados_reais("BBAS3")