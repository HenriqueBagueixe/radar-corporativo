import streamlit as st
import importlib
import os
import json

# Configuração inicial da página e aba do navegador
st.set_page_config(page_title="Radar Corporativo", page_icon="🎯", layout="wide")

@st.cache_resource
def carregar_motores():
    """
    Carrega os módulos de extração e inteligência artificial em cache
    para otimizar a performance da aplicação e evitar reloads desnecessários.
    """
    scrapper_nac = importlib.import_module("04_scrapper_nacional")
    sec = importlib.import_module("02_extrator_sec")
    ia = importlib.import_module("03_sintese_ia")
    return scrapper_nac, sec, ia

scrapper_nac, sec, ia = carregar_motores()

def blindar_cifrao(texto):
    """
    Escapa o caractere de cifrão para evitar que o Streamlit
    interprete valores financeiros como fórmulas matemáticas (LaTeX).
    """
    return str(texto).replace("$", r"\$")

# Cabeçalho da Aplicação
st.title("🎯 Radar de Diagnóstico Corporativo")
st.markdown("Identificação automatizada de ineficiências financeiras e estruturação de propostas de valor estratégico.")
st.divider()

# Estrutura de colunas da Interface
col1, col2 = st.columns([1, 2.5])

with col1:
    st.subheader("Parâmetros da Análise")
    
    # Atualização do seletor para refletir a nova arquitetura baseada em Tickers
    mercado = st.radio("Selecione o Mercado de Atuação:", ["Nacional (B3 - Ticker)", "Internacional (SEC - Ticker)"])
    
    # Textos de apoio padronizados para o usuário final
    if mercado == "Nacional (B3 - Ticker)":
        st.caption("⚙️ **Motor Estrutural:** Conecta-se a bases de dados financeiras para extração de indicadores em tempo real de empresas da B3.")
        st.info("💡 **Guia de Pesquisa:** O sistema exige o Ticker oficial da ação. \n\n**Exemplo:** *Para Banco do Brasil* ➔ Digite: **BBAS3**")
    else:
        st.caption("🧠 **Motor Qualitativo:** Acessa o sistema EDGAR (EUA), processa o relatório anual (10-K) e utiliza IA para mapear riscos operacionais nas entrelinhas.")
        st.info("💡 **Guia de Pesquisa:** O sistema exige o código de bolsa (Ticker). \n\nPara encontrar, busque no Google por *'[Nome da Empresa] stock ticker'*. \n\n**Exemplo:** *Tesla* ➔ Digite: **TSLA**")
        
    alvo = st.text_input("Insira o Alvo (Ticker):")
    btn_analisar = st.button("Executar Diagnóstico Automático", type="primary", use_container_width=True)

with col2:
    st.subheader("Laudo Executivo")
    
    if btn_analisar and alvo:
        with st.spinner(f"Estabelecendo conexão e extraindo dados oficiais de {alvo.upper()}..."):
            texto_cru = None
            
            try:
                # 1. Fluxo de Extração de Dados
                if mercado == "Nacional (B3 - Ticker)":
                    caminho_dados = scrapper_nac.extrair_dados_reais(alvo)
                    if caminho_dados:
                        texto_cru = ia.ler_arquivo_limpo(alvo)
                else:
                    cik = sec.obter_cik(alvo)
                    if cik:
                        url_doc = sec.buscar_url_ultimo_relatorio(cik)
                        if url_doc:
                            sec.extrair_e_limpar_texto(url_doc, alvo)
                            texto_cru = ia.ler_arquivo_limpo(alvo)
            
                # 2. Fluxo de Análise via Inteligência Artificial
                if texto_cru:
                    st.info("Dados brutos capturados com sucesso. Processando análise cognitiva via IA...")
                    
                    sucesso_ia = ia.analisar_com_claude(texto_cru, alvo)
                    caminho_laudo = f"output/{alvo.lower()}_laudo.json"
                    
                    if sucesso_ia and os.path.exists(caminho_laudo):
                        with open(caminho_laudo, 'r', encoding='utf-8') as f:
                            laudo = json.load(f)
                        
                        st.success("Análise Executiva concluída e validada.")
                        
                        # 3. Renderização Estruturada do Laudo na Tela
                        st.markdown("### 📊 Síntese do Diagnóstico")
                        st.write(blindar_cifrao(laudo.get("diagnostico_frio", "Informação indisponível.")))
                        
                        st.markdown("### 🔄 Movimentos Estratégicos (Em Curso)")
                        for m in laudo.get("movimentos_estrategicos", []):
                            st.markdown(f"- {blindar_cifrao(m)}")
                        
                        st.markdown("### ⚠️ Focos Críticos de Sangramento")
                        for s in laudo.get("focos_de_sangramento", []):
                            st.markdown(f"- {blindar_cifrao(s)}")
                            
                        st.markdown("### 🎯 Oportunidade de Inserção (Pitch)")
                        st.info(blindar_cifrao(laudo.get("oportunidade_insercao", "Pitch não gerado.")))
                    else:
                        st.error("[ERRO] Falha na comunicação com a API de Inteligência Artificial ou laudo não gerado.")
                else:
                    st.warning("Não foi possível localizar os dados na base oficial. Verifique a ortografia do Ticker informado.")
                    
            except Exception as e:
                st.error(f"[ERRO CRÍTICO] Falha na execução do pipeline de dados: {str(e)}")
                
    elif btn_analisar and not alvo:
        st.warning("Por favor, insira um parâmetro válido antes de iniciar o processamento.")