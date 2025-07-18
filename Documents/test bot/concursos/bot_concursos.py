import pywhatkit as kit
import datetime
import requests
from bs4 import BeautifulSoup

def buscar_todos_concursos(limite=15):
    sites = {
        "PCI Concursos": "https://www.pciconcursos.com.br/concursos/",
        "Gran Cursos": "https://www.grancursosonline.com.br/",
        "Direção Concursos": "https://www.direcaoconcursos.com.br/concursos",
        "QConcursos": "https://www.qconcursos.com/questoes-de-concursos/concursos?by_situation[]=4"
    }

    mensagens = ["📢 *Concursos Atualizados - {}*".format(datetime.date.today().strftime("%d/%m/%Y"))]
    concursos_gerais = set()

    for nome_site, url in sites.items():
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            if "pciconcursos" in url:
                divs_concursos = soup.find_all("div", class_="ca")
                for div in divs_concursos:
                    link = div.find("a")
                    if link:
                        titulo = link.text.strip()
                        url_concurso = link['href']
                        if not url_concurso.startswith("http"):
                            url_concurso = "https://www.pciconcursos.com.br" + url_concurso
                        concursos_gerais.add((titulo, url_concurso))

            elif "grancursos" in url:
                links = soup.find_all("a", href=True)
                for link in links:
                    if "concurso" in link['href'] and "noticia" not in link['href']:
                        titulo = link.text.strip()
                        url_concurso = link['href']
                        if not url_concurso.startswith("http"):
                            url_concurso = "https://www.grancursosonline.com.br" + url_concurso
                        concursos_gerais.add((titulo, url_concurso))

            elif "direcaoconcursos" in url:
                links = soup.find_all("a", href=True)
                for link in links:
                    if "/concursos/" in link['href']:
                        titulo = link.text.strip()
                        url_concurso = "https://www.direcaoconcursos.com.br" + link['href']
                        concursos_gerais.add((titulo, url_concurso))

            elif "qconcursos" in url:
                links = soup.find_all("a", href=True)
                for link in links:
                    if "/questoes-de-concursos/" in link['href'] and link.text.strip():
                        titulo = link.text.strip()
                        url_concurso = "https://www.qconcursos.com" + link['href']
                        concursos_gerais.add((titulo, url_concurso))

        except Exception as e:
            print(f"⚠️ Erro ao acessar {nome_site}: {e}")

    # Limita quantidade
    concursos_lista = list(concursos_gerais)[:limite]

    for titulo, link in concursos_lista:
        mensagens.append(f"\n🔹 {titulo}\n{link}")

    if not concursos_lista:
        return "⚠️ Nenhum concurso encontrado no momento."
    
    return "\n".join(mensagens)

# === CONFIGURAÇÕES DE ENVIO ===
numero = "+5581998295079"  # <-- Substitua pelo seu número

mensagem = buscar_todos_concursos(limite=15)

# Agenda o envio para 2 minutos após o horário atual
agora = datetime.datetime.now()
hora = agora.hour
minuto = agora.minute + 2

if minuto >= 60:
    minuto -= 60
    hora += 1

# Envia via WhatsApp
kit.sendwhatmsg(numero, mensagem, hora, minuto)
