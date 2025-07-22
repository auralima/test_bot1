import pywhatkit as kit
import datetime
import requests
from bs4 import BeautifulSoup
import time # <-- 1. Importado para usar o sleep

def buscar_todos_concursos(limite=15):
    """
    Busca concursos em diversos sites e formata uma mensagem.
    (Seu código original, sem alterações)
    """
    sites = {
        "PCI Concursos": "https://www.pciconcursos.com.br/concursos/",
        # Removi os outros para o exemplo ser mais rápido, mas mantenha os seus
        # "Gran Cursos": "https://www.grancursosonline.com.br/", 
        # "Direção Concursos": "https://www.direcaoconcursos.com.br/concursos",
        # "QConcursos": "https://www.qconcursos.com/questoes-de-concursos/concursos?by_situation[]=4"
    }

    mensagens = ["📢 *Concursos Atualizados - {}*".format(datetime.date.today().strftime("%d/%m/%Y"))]
    concursos_gerais = set()

    for nome_site, url in sites.items():
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status() # Verifica se a requisição foi bem sucedida
            soup = BeautifulSoup(response.text, 'html.parser')

            if "pciconcursos" in url:
                divs_concursos = soup.find_all("div", class_="ca")
                for div in divs_concursos:
                    link = div.find("a")
                    if link and link.text.strip():
                        titulo = link.text.strip()
                        url_concurso = link['href']
                        if not url_concurso.startswith("http"):
                            url_concurso = "https://www.pciconcursos.com.br" + url_concurso
                        concursos_gerais.add((titulo, url_concurso))
            
            # ... (mantenha a lógica para os outros sites aqui) ...

        except Exception as e:
            print(f"⚠️ Erro ao acessar {nome_site}: {e}")

    if not concursos_gerais:
        return "⚠️ Nenhum concurso novo encontrado no momento."
    
    concursos_lista = list(concursos_gerais)[:limite]

    for titulo, link in concursos_lista:
        mensagens.append(f"\n🔹 {titulo}\n{link}")
    
    return "\n".join(mensagens)

def enviar_automaticamente():
    """
    Função principal que roda em loop para enviar as mensagens.
    """
    # === CONFIGURAÇÕES DE ENVIO ===
    numero_destino = "+5581998295079"  # <-- Substitua pelo número de destino
    intervalo_em_horas = 24  # Enviar a cada 24 horas

    while True: # <-- 2. Loop infinito para automação
        try:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Buscando novos concursos...")
            mensagem = buscar_todos_concursos(limite=15)

            if "Nenhum concurso" not in mensagem:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Preparando para enviar a mensagem...")
                
                # Agenda o envio para 2 minutos no futuro para dar tempo de conectar
                agora = datetime.datetime.now()
                hora_envio = agora.hour
                minuto_envio = agora.minute + 2

                # Envia via WhatsApp
                kit.sendwhatmsg(numero_destino, mensagem, hora_envio, minuto_envio, wait_time=15, close_tab=True, tab_close_time=5)
                
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Mensagem agendada com sucesso!")
            else:
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Nenhum concurso novo encontrado. Pulando o envio.")

        except Exception as e:
            # 4. Tratamento de erro para o loop não quebrar
            print(f"❌ Ocorreu um erro inesperado: {e}")
            print("Tentando novamente no próximo ciclo.")

        # 3. Pausa o script pelo intervalo definido
        tempo_de_espera_segundos = intervalo_em_horas * 3600
        print(f"Aguardando {intervalo_em_horas} horas para o próximo envio...")
        time.sleep(tempo_de_espera_segundos)

# --- Inicia o processo ---
if __name__ == "__main__":
    enviar_automaticamente()