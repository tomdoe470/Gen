#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GEN - Contact Information Scraper
Herramienta avanzada de scraping para extraer información de contacto de sitios web
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import random
import time
import signal
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style

# Inicializar colorama
init(autoreset=True)

# Variable global para manejar interrupción
interrupted = False

class Gen:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/119.0.0.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0'
        ]
        
        self.visited_urls = set()
        self.emails = set()
        self.phones = set()
        self.forms = []
        self.chatbots = []
        self.addresses = set()
        
        self.base_url = None
        self.domain = None
        self.timeout = 10
        self.max_pages = None
        self.pages_crawled = 0
        
        # Keywords multiidioma para detectar secciones de contacto
        self.contact_keywords = [
            'contact', 'contacto', 'contato', 'kontakt', 'contactez',
            'about', 'acerca', 'sobre', 'über',
            'location', 'ubicacion', 'dirección', 'direccion', 'endereço', 'address',
            'support', 'soporte', 'ayuda', 'help', 'aide',
            'office', 'oficina', 'escritório'
        ]
        
    def show_banner(self):
        """Muestra el banner de Gen"""
        banner = f"""
{Fore.CYAN}{'='*70}
{Fore.GREEN}
   ██████╗ ███████╗███╗   ██╗
  ██╔════╝ ██╔════╝████╗  ██║
  ██║  ███╗█████╗  ██╔██╗ ██║
  ██║   ██║██╔══╝  ██║╚██╗██║
  ╚██████╔╝███████╗██║ ╚████║
   ╚═════╝ ╚══════╝╚═╝  ╚═══╝
{Fore.YELLOW}
  Contact Information Scraper v1.0
  Extrae información de contacto de cualquier sitio web
{Fore.CYAN}{'='*70}{Style.RESET_ALL}
"""
        print(banner)
    
    def get_random_user_agent(self):
        """Retorna un user agent aleatorio"""
        return random.choice(self.user_agents)
    
    def configure(self):
        """Configuración interactiva"""
        print(f"\n{Fore.YELLOW}[*] Configuración de Gen{Style.RESET_ALL}\n")
        
        # URL
        while True:
            url = input(f"{Fore.GREEN}[?] URL objetivo: {Style.RESET_ALL}").strip()
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                self.base_url = url
                parsed = urlparse(url)
                self.domain = parsed.netloc
                break
            print(f"{Fore.RED}[!] Por favor ingresa una URL válida{Style.RESET_ALL}")
        
        # Límite de páginas
        limit_input = input(f"{Fore.GREEN}[?] Límite de páginas (Enter para ilimitado): {Style.RESET_ALL}").strip()
        if limit_input and limit_input.isdigit():
            self.max_pages = int(limit_input)
            print(f"{Fore.CYAN}[+] Límite establecido: {self.max_pages} páginas{Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}[+] Sin límite de páginas{Style.RESET_ALL}")
        
        # Timeout
        timeout_input = input(f"{Fore.GREEN}[?] Timeout por request en segundos (default: 10): {Style.RESET_ALL}").strip()
        if timeout_input and timeout_input.isdigit():
            self.timeout = int(timeout_input)
        print(f"{Fore.CYAN}[+] Timeout: {self.timeout}s{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}[*] Configuración completada. Presiona Enter para comenzar...{Style.RESET_ALL}")
        input()
    
    def extract_emails(self, text):
        """Extrae emails del texto"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return set(re.findall(email_pattern, text))
    
    def extract_phones(self, text):
        """Extrae teléfonos del texto (múltiples formatos) con validación estricta"""
        # Patrones más específicos para teléfonos
        phone_patterns = [
            # Formato internacional con +
            r'\+\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,4}',
            # Formato con paréntesis (011) 1234-5678
            r'\(\d{2,4}\)[\s.-]?\d{3,4}[\s.-]?\d{3,4}',
            # Formato con guiones 011-1234-5678
            r'\d{2,4}[-.\s]\d{3,4}[-.\s]\d{3,4}',
            # Formato compacto con código de área
            r'\b\d{10,11}\b',
        ]
        
        # Palabras clave que indican contexto de teléfono (multiidioma)
        phone_context_keywords = [
            'tel', 'phone', 'teléfono', 'telefono', 'call', 'llamar', 'llame',
            'contacto', 'contact', 'celular', 'móvil', 'movil', 'mobile',
            'whatsapp', 'fax', 'línea', 'linea', 'atención', 'atencion'
        ]
        
        phones = set()
        
        # Dividir texto en líneas para análisis contextual
        lines = text.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Verificar si la línea tiene contexto de teléfono
            has_phone_context = any(keyword in line_lower for keyword in phone_context_keywords)
            
            for pattern in phone_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    # Extraer solo dígitos para validación
                    digits_only = re.sub(r'\D', '', match)
                    
                    # Validaciones estrictas
                    # 1. Longitud entre 8 y 15 dígitos
                    if not (8 <= len(digits_only) <= 15):
                        continue
                    
                    # 2. Filtrar años (1900-2099)
                    if digits_only.isdigit() and 1900 <= int(digits_only) <= 2099:
                        continue
                    
                    # 3. Filtrar si parece código postal (5 o 4 dígitos exactos sin separadores)
                    if len(digits_only) in [4, 5] and match.isdigit():
                        continue
                    
                    # 4. Filtrar si todos los dígitos son iguales (111111)
                    if len(set(digits_only)) <= 2:
                        continue
                    
                    # 5. Si no tiene contexto y es muy corto, descartar
                    if not has_phone_context and len(digits_only) < 10:
                        continue
                    
                    # 6. Si tiene formato internacional (+), más flexible
                    if match.strip().startswith('+'):
                        phones.add(match.strip())
                        continue
                    
                    # 7. Si tiene paréntesis o guiones bien formados
                    if '(' in match or match.count('-') >= 2 or match.count('.') >= 2:
                        phones.add(match.strip())
                        continue
                    
                    # 8. Si tiene contexto de teléfono y longitud válida
                    if has_phone_context and len(digits_only) >= 9:
                        phones.add(match.strip())
        
        return phones
    
    def extract_addresses(self, soup):
        """Extrae posibles direcciones físicas"""
        address_keywords = [
            'address', 'dirección', 'direccion', 'ubicación', 'ubicacion',
            'calle', 'avenida', 'street', 'avenue', 'location', 'office'
        ]
        addresses = set()
        
        # Buscar en elementos con atributos relacionados a direcciones
        for elem in soup.find_all(['p', 'div', 'span', 'address']):
            text = elem.get_text(strip=True)
            text_lower = text.lower()
            
            # Si contiene keywords de dirección y tiene cierta longitud
            if any(keyword in text_lower for keyword in address_keywords) and 20 < len(text) < 200:
                addresses.add(text)
        
        return addresses
    
    def detect_forms(self, soup, url):
        """Detecta formularios en la página"""
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                'url': url,
                'action': form.get('action', 'N/A'),
                'method': form.get('method', 'GET'),
                'fields': len(form.find_all(['input', 'textarea', 'select']))
            }
            self.forms.append(form_data)
    
    def detect_chatbots(self, soup, html_text):
        """Detecta chatbots y widgets de atención"""
        chatbot_indicators = [
            'intercom', 'tawk', 'drift', 'livechat', 'zendesk', 'crisp',
            'chat', 'messenger', 'whatsapp', 'telegram', 'widget',
            'live-support', 'customer-support', 'help-widget'
        ]
        
        # Buscar en scripts y divs
        for indicator in chatbot_indicators:
            if indicator in html_text.lower():
                self.chatbots.append({
                    'type': indicator,
                    'url': soup.find('base', href=True)['href'] if soup.find('base', href=True) else 'detected'
                })
                break
    
    def crawl_page(self, url, depth=0):
        """Crawlea una página específica"""
        global interrupted
        
        if interrupted:
            return []
        
        if url in self.visited_urls:
            return []
        
        if self.max_pages and self.pages_crawled >= self.max_pages:
            return []
        
        # Verificar que la URL pertenezca al dominio
        parsed = urlparse(url)
        if parsed.netloc != self.domain:
            return []
        
        self.visited_urls.add(url)
        self.pages_crawled += 1
        
        print(f"{Fore.CYAN}[{self.pages_crawled}] Crawleando: {Fore.WHITE}{url[:80]}...{Style.RESET_ALL}")
        
        try:
            headers = {'User-Agent': self.get_random_user_agent()}
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer información
            self.emails.update(self.extract_emails(response.text))
            self.phones.update(self.extract_phones(response.text))
            self.addresses.update(self.extract_addresses(soup))
            self.detect_forms(soup, url)
            self.detect_chatbots(soup, response.text)
            
            # Mostrar resumen en tiempo real
            print(f"{Fore.GREEN}  ✓ Emails: {len(self.emails)} | Teléfonos: {len(self.phones)} | Formularios: {len(self.forms)}{Style.RESET_ALL}")
            
            # Extraer links internos
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                parsed_link = urlparse(absolute_url)
                
                # Solo links del mismo dominio
                if parsed_link.netloc == self.domain:
                    # Remover fragmentos
                    clean_url = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                    if parsed_link.query:
                        clean_url += f"?{parsed_link.query}"
                    
                    if clean_url not in self.visited_urls:
                        links.append(clean_url)
            
            return links
            
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}  ✗ Timeout en {url}{Style.RESET_ALL}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}  ✗ Error: {str(e)[:50]}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}  ✗ Error inesperado: {str(e)[:50]}{Style.RESET_ALL}")
        
        return []
    
    def crawl(self):
        """Inicia el proceso de crawling"""
        global interrupted
        
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"[*] Iniciando crawling de: {Fore.WHITE}{self.base_url}")
        print(f"{Fore.YELLOW}[*] Presiona Ctrl+C en cualquier momento para generar el reporte")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        to_visit = [self.base_url]
        
        while to_visit and not interrupted:
            if self.max_pages and self.pages_crawled >= self.max_pages:
                print(f"\n{Fore.YELLOW}[!] Límite de páginas alcanzado{Style.RESET_ALL}")
                break
            
            current_url = to_visit.pop(0)
            new_links = self.crawl_page(current_url)
            
            # Agregar nuevos links, priorizando páginas con keywords de contacto
            priority_links = []
            normal_links = []
            
            for link in new_links:
                if any(keyword in link.lower() for keyword in self.contact_keywords):
                    priority_links.append(link)
                else:
                    normal_links.append(link)
            
            to_visit = priority_links + normal_links + to_visit
            
            time.sleep(0.5)  # Pequeña pausa para no sobrecargar el servidor
        
        self.generate_report()
    
    def generate_report(self):
        """Genera el reporte final"""
        print(f"\n\n{Fore.YELLOW}{'='*70}")
        print(f"{Fore.GREEN}[✓] CRAWLING COMPLETADO")
        print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
        
        report = []
        report.append("="*70)
        report.append(f"GEN - Reporte de Información de Contacto")
        report.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"URL Base: {self.base_url}")
        report.append(f"Páginas crawleadas: {self.pages_crawled}")
        report.append("="*70)
        report.append("")
        
        # Emails
        print(f"{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📧 EMAILS ENCONTRADOS ({len(self.emails)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n📧 EMAILS ENCONTRADOS ({len(self.emails)}):")
        report.append("-"*70)
        if self.emails:
            for email in sorted(self.emails):
                print(f"  • {email}")
                report.append(f"  • {email}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron emails{Style.RESET_ALL}")
            report.append("  No se encontraron emails")
        
        # Teléfonos
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📞 TELÉFONOS ENCONTRADOS ({len(self.phones)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n📞 TELÉFONOS ENCONTRADOS ({len(self.phones)}):")
        report.append("-"*70)
        if self.phones:
            for phone in sorted(self.phones):
                print(f"  • {phone}")
                report.append(f"  • {phone}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron teléfonos{Style.RESET_ALL}")
            report.append("  No se encontraron teléfonos")
        
        # Formularios
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📝 FORMULARIOS DETECTADOS ({len(self.forms)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n📝 FORMULARIOS DETECTADOS ({len(self.forms)}):")
        report.append("-"*70)
        if self.forms:
            for idx, form in enumerate(self.forms, 1):
                print(f"  {idx}. URL: {form['url']}")
                print(f"     Action: {form['action']} | Método: {form['method']} | Campos: {form['fields']}")
                report.append(f"  {idx}. URL: {form['url']}")
                report.append(f"     Action: {form['action']} | Método: {form['method']} | Campos: {form['fields']}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron formularios{Style.RESET_ALL}")
            report.append("  No se encontraron formularios")
        
        # Chatbots
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}💬 CHATBOTS/WIDGETS DE ATENCIÓN ({len(set(c['type'] for c in self.chatbots))}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n💬 CHATBOTS/WIDGETS DE ATENCIÓN ({len(set(c['type'] for c in self.chatbots))}):")
        report.append("-"*70)
        if self.chatbots:
            unique_chatbots = list(set(c['type'] for c in self.chatbots))
            for chatbot in unique_chatbots:
                print(f"  • {chatbot.upper()}")
                report.append(f"  • {chatbot.upper()}")
        else:
            print(f"{Fore.YELLOW}  No se detectaron chatbots{Style.RESET_ALL}")
            report.append("  No se detectaron chatbots")
        
        # Direcciones
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📍 DIRECCIONES FÍSICAS DETECTADAS ({len(self.addresses)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n📍 DIRECCIONES FÍSICAS DETECTADAS ({len(self.addresses)}):")
        report.append("-"*70)
        if self.addresses:
            for addr in list(self.addresses)[:10]:  # Limitar a 10 para no saturar
                print(f"  • {addr[:100]}...")
                report.append(f"  • {addr}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron direcciones{Style.RESET_ALL}")
            report.append("  No se encontraron direcciones")
        
        # Guardar reporte
        filename = f"gen_report_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            print(f"\n{Fore.GREEN}[✓] Reporte guardado en: {Fore.WHITE}{filename}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}[!] Error al guardar reporte: {e}{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")


def signal_handler(sig, frame):
    """Maneja la interrupción Ctrl+C"""
    global interrupted
    interrupted = True
    print(f"\n\n{Fore.YELLOW}[!] Interrupción detectada. Generando reporte con los datos encontrados...{Style.RESET_ALL}\n")


def main():
    global interrupted
    
    # Configurar handler para Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    gen = Gen()
    gen.show_banner()
    gen.configure()
    
    try:
        gen.crawl()
    except KeyboardInterrupt:
        pass
    
    if not interrupted:
        print(f"\n{Fore.GREEN}[✓] Proceso completado exitosamente{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
