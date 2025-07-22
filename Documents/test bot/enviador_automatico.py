import pywhatkit as kit
import datetime
import requests
from bs4 import BeautifulSoup
import time

def buscar_todos_concursos(limite=20, filtro_localidade='PE'):
    """
    Busca concursos em diversos sites e, opcionalmente, filtra por localidade.
    
    Args:
        limite (int): Número máximo de concursos a serem retornados.
        filtro_localidade (list): Lista de palavras-chave para filtrar os títulos (ex: ['PE', 'Recife']).
                                  Se for None, retorna todos os concursos.
    """
    sites = {
        "PCI Concursos": "https://www.pciconcursos.com.br/concursos/nordeste/", # <<< MODIFICADO para já focar na região Nordeste
        "JC Concursos": "https://jcconcursos.com.br/concursos/nordeste/",
    }

    # <<< MODIFICADO: Adapta o cabeçalho se o filtro estiver ativo
    if filtro_localidade:
        titulo_cabecalho = "📢 *Concursos para Pernambuco - {}*".format(datetime.date.today().strftime("%d/%m/%Y"))
    else:
        titulo_cabecalho = "📢 *Concursos Nacionais/Nordeste - {}*".format(datetime.date.today().strftime("%d/%m/%Y"))

    mensagens = [titulo_cabecalho]
    concursos_gerais = set()

    print("Iniciando a busca nos sites de concursos...")
    for nome_site, url in sites.items():
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lógica de extração para PCI Concursos
            if "pciconcursos" in url:
                divs_concursos = soup.find_all("div", class_="ca")
                for div in divs_concursos:
                    link_tag = div.find("a")
                    if link_tag and link_tag.text.strip():
                        titulo = link_tag.text.strip()
                        url_concurso = link_tag['href']
                        if not url_concurso.startswith("http"):
                            url_concurso = "https://www.pciconcursos.com.br" + url_concurso
                        concursos_gerais.add((titulo, url_concurso))
            
            # Lógica de extração para JC Concursos
            elif "jcconcursos" in url:
                articles = soup.find_all("a", class_="box-concurso-item")
                for article in articles:
                    titulo_tag = article.find("h2")
                    if titulo_tag and titulo_tag.text.strip():
                        titulo = titulo_tag.text.strip()
                        url_concurso = article['href']
                        concursos_gerais.add((titulo, url_concurso))

        except Exception as e:
            print(f"⚠️ Erro ao acessar {nome_site}: {e}")

    # <<< NOVO: Bloco de filtragem por localidade
    if filtro_localidade:
        print(f"Aplicando filtro para: {filtro_localidade}")
        concursos_filtrados = set()
        # Converte as palavras do filtro para minúsculo para a comparação não diferenciar maiúsculas/minúsculas
        filtro_lower = [f.lower() for f in filtro_localidade]
        
        for titulo, link in concursos_gerais:
            titulo_lower = titulo.lower()
            # Verifica se alguma palavra do filtro está no título
            if any(palavra in titulo_lower for palavra in filtro_lower):
                concursos_filtrados.add((titulo, link))
        
        # Usa a lista filtrada se algum concurso for encontrado
        if concursos_filtrados:
            concursos_a_processar = concursos_filtrados
        else:
            # Se o filtro não retornar nada, avisa no console e não retorna nenhum.
            print("Nenhum concurso encontrado para a localidade especificada.")
            return "⚠️ Nenhum concurso encontrado para Pernambuco no momento."
    else:
        # Se não houver filtro, usa todos os concursos encontrados
        concursos_a_processar = concursos_gerais

    if not concursos_a_processar:
        return "⚠️ Nenhum concurso encontrado no momento."
    
    concursos_lista = list(concursos_a_processar)[:limite]

    for titulo, link in concursos_lista:
        mensagens.append(f"\n🔹 {titulo}\n{link}")
    
    return "\n".join(mensagens)

def enviar_automaticamente():
    """
    Função principal que roda em loop para enviar as mensagens.
    """
    # ========================== CONFIGURAÇÕES ==========================
    numero_destino = "00000000000000"  # <-- Coloque o número de destino aqui
    intervalo_em_horas = 24            # Intervalo entre os envios (ex: 24h)
    
    # <<< NOVO: Chave para ligar/desligar o filtro de localidade
    FILTRAR_POR_LOCALIDADE = True      # Mude para False se quiser concursos de todo o Nordeste/Brasil

    # Palavras-chave para o filtro. Você pode adicionar ou remover cidades.
    localidades_filtro = ['nordeste','pe', 'pernambuco', 'recife', 'nordeste', 'olinda', 'jaboatão', 'caruaru', 'petrolina''']
    # ===================================================================

    while True:
        try:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Iniciando ciclo de busca...")
            
            # Decide se passa a lista de filtros para a função ou não
            filtro_ativo = localidades_filtro if FILTRAR_POR_LOCALIDADE else None
            
            mensagem = buscar_todos_concursos(limite=20, filtro_localidade=filtro_ativo)

            if "Nenhum concurso" not in mensagem:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Preparando para enviar a mensagem...")
                
                agora = datetime.datetime.now()
                hora_envio = agora.hour
                minuto_envio = agora.minute + 2 # Agendamento para 2 min no futuro para dar tempo de conectar

                kit.sendwhatmsg(
                    numero_destino, 
                    mensagem, 
                    hora_envio, 
                    minuto_envio, 
                    wait_time=15, 
                    close_time=10 # Fecha a aba 10 segundos após o envio
                )
                
                print(f"✔️ [{datetime.datetime.now().strftime('%H:%M:%S')}] Mensagem agendada com sucesso!")
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Nenhuma novidade encontrada. Pulando o envio.")

        except Exception as e:
            print(f"❌ Ocorreu um erro inesperado: {e}")
            print("Tentando novamente no próximo ciclo.")

        tempo_de_espera_segundos = intervalo_em_horas * 3600
        print(f"Aguardando {intervalo_em_horas} horas para o próximo envio...")
        time.sleep(tempo_de_espera_segundos)


# --- Inicia o processo ---
if __name__ == "__main__":
    enviar_automaticamente()