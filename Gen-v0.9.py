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
import dns.resolver
import socket
from collections import Counter

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
        self.company_name = None
        self.timeout = 10
        self.max_pages = None
        self.pages_crawled = 0
        self.use_dorking = False
        
        # Datos encontrados por dorking
        self.dork_emails = set()
        self.dork_phones = set()
        self.dork_social_media = []
        self.dork_linkedin = None
        
        # Análisis de inteligencia
        self.email_intelligence = {}
        self.phone_intelligence = []
        self.attack_vectors = []
        self.security_profile = {}
        
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
        
        # Nombre de la empresa
        company = input(f"{Fore.GREEN}[?] Nombre de la empresa (para búsquedas avanzadas): {Style.RESET_ALL}").strip()
        if company:
            self.company_name = company
            print(f"{Fore.CYAN}[+] Empresa: {self.company_name}{Style.RESET_ALL}")
        
        # Dorking
        dork_choice = input(f"{Fore.GREEN}[?] ¿Usar búsqueda avanzada en múltiples buscadores? (s/n): {Style.RESET_ALL}").strip().lower()
        if dork_choice in ['s', 'si', 'y', 'yes']:
            self.use_dorking = True
            print(f"{Fore.CYAN}[+] Dorking activado (Google, Yandex, DuckDuckGo, Baidu, Bing, Brave, Startpage){Style.RESET_ALL}")
        
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
    
    def dork_search(self):
        """Realiza búsquedas con dorks en múltiples buscadores"""
        if not self.use_dorking:
            return
        
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"[*] Iniciando búsqueda avanzada en múltiples buscadores...")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Definir buscadores y sus URLs
        search_engines = {
            'Google': 'https://www.google.com/search?q={}',
            'Yandex': 'https://yandex.com/search/?text={}',
            'DuckDuckGo': 'https://html.duckduckgo.com/html/?q={}',
            'Baidu': 'https://www.baidu.com/s?wd={}',
            'Bing': 'https://www.bing.com/search?q={}',
            'Brave': 'https://search.brave.com/search?q={}',
            'Startpage': 'https://www.startpage.com/do/search?q={}'
        }
        
        # Crear dorks específicos
        dorks = []
        
        # Dorks básicos del sitio
        dorks.append(f'site:{self.domain} contact')
        dorks.append(f'site:{self.domain} email')
        dorks.append(f'site:{self.domain} (phone OR telephone OR teléfono OR telefono)')
        dorks.append(f'site:{self.domain} "@{self.domain}"')
        
        if self.company_name:
            # Dorks con nombre de empresa
            dorks.append(f'"{self.company_name}" email')
            dorks.append(f'"{self.company_name}" contact')
            dorks.append(f'"{self.company_name}" LinkedIn')
            dorks.append(f'"{self.company_name}" (phone OR telephone)')
            dorks.append(f'"{self.company_name}" site:linkedin.com')
            dorks.append(f'"{self.company_name}" site:facebook.com')
            dorks.append(f'"{self.company_name}" site:twitter.com')
            dorks.append(f'"{self.company_name}" site:instagram.com')
            dorks.append(f'"{self.company_name}" "@"')
        
        total_searches = len(search_engines) * min(5, len(dorks))  # Limitar a 5 dorks por buscador
        search_count = 0
        
        for engine_name, engine_url in search_engines.items():
            print(f"{Fore.CYAN}[*] Buscando en {engine_name}...{Style.RESET_ALL}")
            
            # Usar los primeros 5 dorks más relevantes para cada buscador
            for dork in dorks[:5]:
                search_count += 1
                try:
                    # Construir URL de búsqueda
                    import urllib.parse
                    query = urllib.parse.quote(dork)
                    search_url = engine_url.format(query)
                    
                    headers = {
                        'User-Agent': self.get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }
                    
                    response = requests.get(search_url, headers=headers, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        
                        # Extraer texto de resultados
                        text_content = soup.get_text()
                        
                        # Buscar emails
                        found_emails = self.extract_emails(text_content)
                        # Filtrar solo emails del dominio objetivo o relacionados
                        for email in found_emails:
                            if self.domain in email or (self.company_name and self.company_name.lower().replace(' ', '') in email.lower()):
                                self.dork_emails.add(email)
                        
                        # Buscar teléfonos
                        found_phones = self.extract_phones(text_content)
                        self.dork_phones.update(found_phones)
                        
                        # Buscar LinkedIn
                        if 'linkedin.com' in dork.lower():
                            linkedin_links = soup.find_all('a', href=True)
                            for link in linkedin_links:
                                href = link.get('href', '')
                                if 'linkedin.com/company' in href or 'linkedin.com/in' in href:
                                    if not self.dork_linkedin:
                                        self.dork_linkedin = href
                                        print(f"{Fore.GREEN}  ✓ LinkedIn encontrado: {href[:60]}...{Style.RESET_ALL}")
                        
                        # Buscar redes sociales
                        social_patterns = {
                            'Facebook': r'facebook\.com/[\w.-]+',
                            'Twitter': r'twitter\.com/[\w.-]+',
                            'Instagram': r'instagram\.com/[\w.-]+',
                            'YouTube': r'youtube\.com/(c/|channel/|user/)[\w.-]+',
                        }
                        
                        for platform, pattern in social_patterns.items():
                            matches = re.findall(pattern, text_content)
                            for match in matches:
                                full_url = f"https://{match}"
                                if full_url not in [s['url'] for s in self.dork_social_media]:
                                    self.dork_social_media.append({
                                        'platform': platform,
                                        'url': full_url
                                    })
                        
                        print(f"{Fore.GREEN}  ✓ [{search_count}/{total_searches}] Procesado: {dork[:50]}...{Style.RESET_ALL}")
                    
                    # Pausa entre búsquedas para no ser bloqueado
                    time.sleep(random.uniform(2, 4))
                    
                except requests.exceptions.RequestException as e:
                    print(f"{Fore.YELLOW}  ⚠ Error en {engine_name}: {str(e)[:40]}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}  ✗ Error inesperado: {str(e)[:40]}{Style.RESET_ALL}")
        
        # Resumen de dorking
        print(f"\n{Fore.GREEN}[✓] Dorking completado:{Style.RESET_ALL}")
        print(f"  • Emails encontrados: {len(self.dork_emails)}")
        print(f"  • Teléfonos encontrados: {len(self.dork_phones)}")
        print(f"  • Redes sociales: {len(self.dork_social_media)}")
        print(f"  • LinkedIn: {'Sí' if self.dork_linkedin else 'No'}\n")
    
    
    def extract_addresses(self, soup):
        """Extrae posibles direcciones físicas con validación estricta"""
        addresses = set()
        
        # Patrones de direcciones más específicos
        address_patterns = [
            # Calle/Avenida + número
            r'(?:calle|c/|av\.|avenida|boulevard|blvd|paseo|plaza)\s+[a-záéíóúñ\s]+\s*,?\s*n[°º]?\s*\d+',
            # Número + nombre de calle
            r'\d+\s+(?:calle|street|avenue|road|av\.)\s+[a-záéíóúñ\s]+',
            # Formato con código postal
            r'[a-záéíóúñ\s]+\d+\s*,\s*(?:cp|c\.p\.|código postal)?\s*\d{4,5}',
        ]
        
        # Keywords más específicas
        address_keywords = ['dirección', 'direccion', 'ubicación', 'ubicacion', 'address', 'location']
        
        # Buscar en elementos específicos más propensos a tener direcciones
        for elem in soup.find_all(['address', 'p', 'div', 'span']):
            text = elem.get_text(strip=True)
            text_lower = text.lower()
            
            # Validaciones estrictas
            # 1. Longitud razonable (entre 20 y 150 caracteres)
            if not (20 <= len(text) <= 150):
                continue
            
            # 2. Debe contener al menos un número
            if not re.search(r'\d', text):
                continue
            
            # 3. Verificar si coincide con algún patrón de dirección
            matches_pattern = any(re.search(pattern, text_lower) for pattern in address_patterns)
            
            # 4. O contiene keywords de dirección Y tiene formato apropiado
            has_keyword = any(keyword in text_lower for keyword in address_keywords)
            has_commas = text.count(',') >= 1
            
            # 5. No debe ser texto promocional (filtrar frases típicas de marketing)
            promotional_phrases = [
                'ahora podés', 'llevar un registro', 'optimizar', 'experiencia',
                'te traemos', 'consejos', 'continuar con', 'prevención',
                'estrategia', 'app', 'home office', 'licencia', 'maternidad'
            ]
            is_promotional = any(phrase in text_lower for phrase in promotional_phrases)
            
            if is_promotional:
                continue
            
            # 6. Debe tener estructura de dirección real
            if (matches_pattern or (has_keyword and has_commas)):
                # Verificar que no sea una frase larga/párrafo
                sentence_count = text.count('.') + text.count('?') + text.count('!')
                if sentence_count <= 1:  # Máximo una oración
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
        """Deteca chatbots y widgets de atención con URLs específicas"""
        
        # Detectar WhatsApp
        whatsapp_patterns = [
            r'wa\.me/(\d+)',
            r'api\.whatsapp\.com/send\?phone=(\d+)',
            r'web\.whatsapp\.com/send\?phone=(\d+)',
            r'whatsapp://send\?phone=(\d+)'
        ]
        
        for pattern in whatsapp_patterns:
            matches = re.findall(pattern, html_text)
            for match in matches:
                wa_url = f"https://wa.me/{match}"
                if not any(c['type'] == 'whatsapp' and c['url'] == wa_url for c in self.chatbots):
                    self.chatbots.append({
                        'type': 'whatsapp',
                        'url': wa_url,
                        'phone': match
                    })
        
        # Detectar otros chatbots con sus URLs/IDs
        chatbot_patterns = {
            'intercom': r'intercom\.com|app_id["\']?\s*:\s*["\']([^"\']+)',
            'tawk': r'tawk\.to/([a-z0-9]+)',
            'drift': r'drift\.com|drift\.load\(["\']([^"\']+)',
            'livechat': r'livechat(?:inc)?\.com',
            'zendesk': r'zendesk\.com|zdassets\.com',
            'crisp': r'crisp\.chat|crisp\.im',
            'tidio': r'tidio\.co|tidiochat',
            'messenger': r'facebook\.com/messages|fb\.com/msg|m\.me/([^/\s"\']+)',
            'telegram': r't\.me/([a-zA-Z0-9_]+)',
        }
        
        html_lower = html_text.lower()
        
        for bot_type, pattern in chatbot_patterns.items():
            if re.search(pattern, html_lower):
                # Intentar extraer URL o ID específico
                match = re.search(pattern, html_text, re.IGNORECASE)
                
                bot_data = {'type': bot_type, 'url': 'detected'}
                
                if match and match.groups():
                    identifier = match.group(1)
                    
                    if bot_type == 'tawk':
                        bot_data['url'] = f"https://tawk.to/{identifier}"
                    elif bot_type == 'messenger':
                        bot_data['url'] = f"https://m.me/{identifier}"
                    elif bot_type == 'telegram':
                        bot_data['url'] = f"https://t.me/{identifier}"
                    else:
                        bot_data['url'] = identifier
                
                # Evitar duplicados
                if not any(c['type'] == bot_type for c in self.chatbots):
                    self.chatbots.append(bot_data)
    
    def analyze_email_intelligence(self):
        """Analiza la infraestructura de email y obtiene inteligencia"""
        print(f"\n{Fore.YELLOW}[*] Analizando infraestructura de email...{Style.RESET_ALL}")
        
        all_emails = self.emails | self.dork_emails
        
        if not all_emails:
            return
        
        # Análisis de proveedores
        providers = {
            'gmail.com': 'Gmail/Google Workspace',
            'googlemail.com': 'Gmail/Google Workspace',
            'outlook.com': 'Outlook.com',
            'hotmail.com': 'Hotmail/Outlook',
            'live.com': 'Microsoft Live',
            'yahoo.com': 'Yahoo Mail',
            'protonmail.com': 'ProtonMail (Seguro)',
            'proton.me': 'ProtonMail (Seguro)',
        }
        
        email_domains = {}
        for email in all_emails:
            domain = email.split('@')[-1]
            if domain not in email_domains:
                email_domains[domain] = []
            email_domains[domain].append(email)
        
        # Analizar cada dominio
        for domain, emails in email_domains.items():
            domain_info = {
                'domain': domain,
                'email_count': len(emails),
                'provider': providers.get(domain, 'Dominio propio'),
                'mx_records': [],
                'mail_server': 'Desconocido',
                'security': {}
            }
            
            # Obtener registros MX
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                for mx in mx_records:
                    mx_host = str(mx.exchange).lower()
                    domain_info['mx_records'].append(mx_host)
                    
                    # Identificar proveedor por MX
                    if 'google' in mx_host or 'gmail' in mx_host:
                        domain_info['mail_server'] = 'Google Workspace'
                    elif 'outlook' in mx_host or 'microsoft' in mx_host:
                        domain_info['mail_server'] = 'Microsoft 365'
                    elif 'zoho' in mx_host:
                        domain_info['mail_server'] = 'Zoho Mail'
                    elif 'mail.protection' in mx_host:
                        domain_info['mail_server'] = 'Microsoft Exchange Online'
                    else:
                        domain_info['mail_server'] = 'Servidor propio/Hosting'
                
                print(f"{Fore.GREEN}  ✓ {domain}: {domain_info['mail_server']}{Style.RESET_ALL}")
                
            except Exception:
                domain_info['mail_server'] = 'No se pudo determinar'
            
            # Verificar registros de seguridad (SPF, DMARC)
            try:
                # SPF
                txt_records = dns.resolver.resolve(domain, 'TXT')
                for txt in txt_records:
                    txt_str = str(txt)
                    if 'v=spf1' in txt_str:
                        domain_info['security']['spf'] = 'Configurado'
                
                # DMARC
                dmarc_records = dns.resolver.resolve(f'_dmarc.{domain}', 'TXT')
                for dmarc in dmarc_records:
                    if 'v=DMARC1' in str(dmarc):
                        domain_info['security']['dmarc'] = 'Configurado'
            except Exception:
                pass
            
            if not domain_info['security'].get('spf'):
                domain_info['security']['spf'] = 'No configurado'
            if not domain_info['security'].get('dmarc'):
                domain_info['security']['dmarc'] = 'No configurado'
            
            self.email_intelligence[domain] = domain_info
    
    def analyze_phone_intelligence(self):
        """Analiza los teléfonos y obtiene información geográfica"""
        print(f"\n{Fore.YELLOW}[*] Analizando teléfonos...{Style.RESET_ALL}")
        
        all_phones = self.phones | self.dork_phones
        
        if not all_phones:
            return
        
        # Códigos de país más comunes
        country_codes = {
            '+1': 'Estados Unidos/Canadá',
            '+7': 'Rusia/Kazajistán',
            '+20': 'Egipto',
            '+27': 'Sudáfrica',
            '+30': 'Grecia',
            '+31': 'Países Bajos',
            '+32': 'Bélgica',
            '+33': 'Francia',
            '+34': 'España',
            '+39': 'Italia',
            '+40': 'Rumania',
            '+41': 'Suiza',
            '+43': 'Austria',
            '+44': 'Reino Unido',
            '+45': 'Dinamarca',
            '+46': 'Suecia',
            '+47': 'Noruega',
            '+48': 'Polonia',
            '+49': 'Alemania',
            '+51': 'Perú',
            '+52': 'México',
            '+53': 'Cuba',
            '+54': 'Argentina',
            '+55': 'Brasil',
            '+56': 'Chile',
            '+57': 'Colombia',
            '+58': 'Venezuela',
            '+60': 'Malasia',
            '+61': 'Australia',
            '+62': 'Indonesia',
            '+63': 'Filipinas',
            '+64': 'Nueva Zelanda',
            '+65': 'Singapur',
            '+66': 'Tailandia',
            '+81': 'Japón',
            '+82': 'Corea del Sur',
            '+84': 'Vietnam',
            '+86': 'China',
            '+90': 'Turquía',
            '+91': 'India',
            '+92': 'Pakistán',
            '+93': 'Afganistán',
            '+94': 'Sri Lanka',
            '+95': 'Myanmar',
            '+98': 'Irán',
            '+212': 'Marruecos',
            '+213': 'Argelia',
            '+234': 'Nigeria',
            '+351': 'Portugal',
            '+352': 'Luxemburgo',
            '+353': 'Irlanda',
            '+354': 'Islandia',
            '+355': 'Albania',
            '+356': 'Malta',
            '+357': 'Chipre',
            '+358': 'Finlandia',
            '+420': 'República Checa',
            '+421': 'Eslovaquia',
            '+506': 'Costa Rica',
            '+507': 'Panamá',
            '+593': 'Ecuador',
            '+598': 'Uruguay',
        }
        
        # Códigos de área Argentina (ejemplo expandido)
        argentina_areas = {
            '011': 'Buenos Aires (CABA)',
            '0221': 'La Plata',
            '0223': 'Mar del Plata',
            '0261': 'Mendoza',
            '0341': 'Rosario',
            '0351': 'Córdoba',
            '0381': 'Tucumán',
            '0387': 'Salta',
        }
        
        for phone in all_phones:
            phone_info = {
                'number': phone,
                'country': 'Desconocido',
                'type': 'Desconocido',
                'area': None,
                'carrier': 'Desconocido'
            }
            
            # Limpiar número
            clean_number = re.sub(r'\D', '', phone)
            
            # Detectar país por código
            for code, country in country_codes.items():
                if phone.startswith(code) or clean_number.startswith(code.replace('+', '')):
                    phone_info['country'] = country
                    
                    # Si es Argentina, detectar área
                    if code == '+54':
                        for area_code, area_name in argentina_areas.items():
                            if area_code.replace('0', '') in clean_number[:4]:
                                phone_info['area'] = area_name
                        
                        # Determinar si es móvil o fijo (Argentina)
                        # Móviles empiezan con 11, 15, etc después del código de país
                        if len(clean_number) >= 12 and clean_number[2:4] in ['11', '15']:
                            phone_info['type'] = 'Móvil'
                        elif len(clean_number) >= 10:
                            phone_info['type'] = 'Fijo'
                    
                    break
            
            # Si no tiene código internacional explícito, asumir local
            if phone_info['country'] == 'Desconocido':
                if len(clean_number) >= 10:
                    # Verificar si parece argentino
                    if clean_number.startswith('011') or clean_number.startswith('11'):
                        phone_info['country'] = 'Argentina (asumido)'
                        phone_info['type'] = 'Móvil' if '15' in clean_number[:4] else 'Fijo'
            
            self.phone_intelligence.append(phone_info)
            print(f"{Fore.GREEN}  ✓ {phone}: {phone_info['country']} ({phone_info['type']}){Style.RESET_ALL}")
    
    def generate_attack_vectors(self):
        """Genera vectores de ataque basados en la inteligencia recopilada"""
        print(f"\n{Fore.YELLOW}[*] Generando vectores de ataque...{Style.RESET_ALL}")
        
        vectors = []
        
        # Análisis de superficie de ataque
        attack_surface = []
        
        # Vector 1: Email-based attacks
        if self.emails or self.dork_emails:
            all_emails = self.emails | self.dork_emails
            
            # Calcular nivel de exposición
            exposure_level = 'Baja' if len(all_emails) <= 2 else ('Media' if len(all_emails) <= 5 else 'Alta')
            
            vector = {
                'type': 'Email Phishing',
                'probability': 'Alta' if len(all_emails) > 3 else 'Media',
                'description': f'{len(all_emails)} emails expuestos públicamente',
                'techniques': []
            }
            
            # Analizar seguridad del dominio
            weak_security = False
            for domain, info in self.email_intelligence.items():
                if info['security'].get('dmarc') == 'No configurado':
                    vector['techniques'].append('Spoofing de dominio (sin DMARC)')
                    weak_security = True
                if info['security'].get('spf') == 'No configurado':
                    vector['techniques'].append('Envío desde servidores no autorizados (sin SPF)')
                    weak_security = True
            
            if weak_security:
                vector['probability'] = 'Muy Alta'
            
            vector['techniques'].extend([
                'Spear phishing personalizado',
                'Ingeniería social vía correo',
                'Credential harvesting'
            ])
            
            vectors.append(vector)
            attack_surface.append(f"Exposición de emails: {exposure_level}")
        
        # Vector 2: Phone-based attacks (Vishing)
        if self.phones or self.dork_phones:
            all_phones = self.phones | self.dork_phones
            mobile_count = sum(1 for p in self.phone_intelligence if p['type'] == 'Móvil')
            
            vector = {
                'type': 'Vishing (Voice Phishing)',
                'probability': 'Alta' if mobile_count > 0 else 'Media',
                'description': f'{len(all_phones)} números telefónicos identificados',
                'techniques': [
                    'Pretexto de soporte técnico',
                    'Suplantación de proveedor de servicios',
                    'Urgencia falsa (seguridad/facturas)',
                ]
            }
            
            if mobile_count > 0:
                vector['techniques'].append('SMS phishing (Smishing)')
            
            vectors.append(vector)
            attack_surface.append(f"Teléfonos expuestos: {len(all_phones)} ({mobile_count} móviles)")
        
        # Vector 3: WhatsApp/Chatbot exploitation
        whatsapp_bots = [c for c in self.chatbots if c['type'] == 'whatsapp']
        if whatsapp_bots:
            vector = {
                'type': 'WhatsApp Social Engineering',
                'probability': 'Alta',
                'description': f'{len(whatsapp_bots)} línea(s) de WhatsApp expuesta(s)',
                'techniques': [
                    'Contacto directo vía WhatsApp',
                    'Pretexto de cliente/proveedor',
                    'Compartir archivos maliciosos',
                    'Ingeniería social conversacional'
                ]
            }
            vectors.append(vector)
            attack_surface.append(f"WhatsApp Business expuesto")
        
        # Vector 4: Web Forms exploitation
        if self.forms:
            forms_without_protection = [f for f in self.forms if 'captcha' not in str(f).lower()]
            
            vector = {
                'type': 'Formularios Web',
                'probability': 'Media',
                'description': f'{len(self.forms)} formularios detectados',
                'techniques': [
                    'Spam automatizado',
                    'Inyección de datos maliciosos',
                    'Recopilación de información'
                ]
            }
            
            if len(forms_without_protection) > 0:
                vector['techniques'].append(f'{len(forms_without_protection)} sin CAPTCHA visible')
                vector['probability'] = 'Alta'
            
            vectors.append(vector)
            attack_surface.append(f"Formularios web: {len(self.forms)}")
        
        # Vector 5: Social Media reconnaissance
        if self.dork_social_media or self.dork_linkedin:
            vector = {
                'type': 'OSINT en Redes Sociales',
                'probability': 'Media',
                'description': 'Perfiles sociales identificados',
                'techniques': [
                    'Reconocimiento de empleados (LinkedIn)',
                    'Mapeo de estructura organizacional',
                    'Identificación de objetivos clave',
                    'Ingeniería social basada en información pública'
                ]
            }
            vectors.append(vector)
        
        self.attack_vectors = vectors
        
        # Generar perfil de seguridad
        self.security_profile = {
            'exposure_level': 'Alta' if len(attack_surface) >= 4 else ('Media' if len(attack_surface) >= 2 else 'Baja'),
            'attack_surface': attack_surface,
            'primary_vectors': [v['type'] for v in vectors if v['probability'] in ['Alta', 'Muy Alta']],
            'recommendations': self.generate_security_recommendations()
        }
        
        print(f"{Fore.GREEN}  ✓ {len(vectors)} vectores de ataque identificados{Style.RESET_ALL}")
    
    def generate_security_recommendations(self):
        """Genera recomendaciones de seguridad basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones basadas en emails
        for domain, info in self.email_intelligence.items():
            if info['security'].get('dmarc') == 'No configurado':
                recommendations.append(f'Configurar DMARC para {domain} contra spoofing')
            if info['security'].get('spf') == 'No configurado':
                recommendations.append(f'Implementar SPF para {domain}')
        
        # Recomendaciones generales
        if len(self.emails | self.dork_emails) > 5:
            recommendations.append('Reducir exposición pública de emails corporativos')
        
        if any(c['type'] == 'whatsapp' for c in self.chatbots):
            recommendations.append('Capacitar personal de WhatsApp en detección de ingeniería social')
        
        if self.forms:
            recommendations.append('Implementar CAPTCHA en todos los formularios públicos')
        
        recommendations.append('Programa de awareness en phishing y vishing')
        recommendations.append('Autenticación multifactor (MFA) en todos los servicios')
        
        return recommendations
    
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
        
        # Primero ejecutar dorking si está activado
        if self.use_dorking:
            try:
                self.dork_search()
            except Exception as e:
                print(f"{Fore.RED}[!] Error en dorking: {e}{Style.RESET_ALL}")
        
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
        
        # Ejecutar análisis de inteligencia
        print(f"\n{Fore.YELLOW}{'='*70}")
        print(f"[*] Iniciando análisis de inteligencia...")
        print(f"{'='*70}{Style.RESET_ALL}")
        
        try:
            self.analyze_email_intelligence()
            self.analyze_phone_intelligence()
            self.generate_attack_vectors()
        except Exception as e:
            print(f"{Fore.RED}[!] Error en análisis de inteligencia: {e}{Style.RESET_ALL}")
        
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
        if self.company_name:
            report.append(f"Empresa: {self.company_name}")
        report.append(f"Páginas crawleadas: {self.pages_crawled}")
        if self.use_dorking:
            report.append(f"Dorking: ACTIVADO (7 buscadores)")
        report.append("="*70)
        report.append("")
        
        # Combinar resultados de crawling y dorking
        all_emails = self.emails | self.dork_emails
        all_phones = self.phones | self.dork_phones
        
        # Emails
        print(f"{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📧 EMAILS ENCONTRADOS ({len(all_emails)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n📧 EMAILS ENCONTRADOS ({len(all_emails)}):")
        report.append("-"*70)
        if all_emails:
            # Separar por fuente
            crawl_only = self.emails - self.dork_emails
            dork_only = self.dork_emails - self.emails
            both = self.emails & self.dork_emails
            
            if both:
                print(f"\n{Fore.YELLOW}  [Encontrados en ambas fuentes]:{Style.RESET_ALL}")
                report.append("\n  [Encontrados en ambas fuentes]:")
                for email in sorted(both):
                    print(f"  • {email}")
                    report.append(f"  • {email}")
            
            if crawl_only:
                print(f"\n{Fore.CYAN}  [Solo en sitio web]:{Style.RESET_ALL}")
                report.append("\n  [Solo en sitio web]:")
                for email in sorted(crawl_only):
                    print(f"  • {email}")
                    report.append(f"  • {email}")
            
            if dork_only:
                print(f"\n{Fore.MAGENTA}  [Solo en buscadores]:{Style.RESET_ALL}")
                report.append("\n  [Solo en buscadores]:")
                for email in sorted(dork_only):
                    print(f"  • {email}")
                    report.append(f"  • {email}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron emails{Style.RESET_ALL}")
            report.append("  No se encontraron emails")
        
        # Teléfonos
        print(f"\n{Fore.CYAN}{'─'*70}")
        print(f"{Fore.GREEN}📞 TELÉFONOS ENCONTRADOS ({len(all_phones)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n📞 TELÉFONOS ENCONTRADOS ({len(all_phones)}):")
        report.append("-"*70)
        if all_phones:
            for phone in sorted(all_phones):
                source = ""
                if phone in self.phones and phone in self.dork_phones:
                    source = " [Web + Buscadores]"
                elif phone in self.dork_phones:
                    source = " [Buscadores]"
                else:
                    source = " [Web]"
                print(f"  • {phone}{Fore.CYAN}{source}{Style.RESET_ALL}")
                report.append(f"  • {phone}{source}")
        else:
            print(f"{Fore.YELLOW}  No se encontraron teléfonos{Style.RESET_ALL}")
            report.append("  No se encontraron teléfonos")
        
        # LinkedIn y Redes Sociales
        if self.use_dorking:
            print(f"\n{Fore.CYAN}{'─'*70}")
            print(f"{Fore.GREEN}🔗 LINKEDIN Y REDES SOCIALES:")
            print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
            report.append(f"\n\n🔗 LINKEDIN Y REDES SOCIALES:")
            report.append("-"*70)
            
            if self.dork_linkedin:
                print(f"  LinkedIn: {self.dork_linkedin}")
                report.append(f"  LinkedIn: {self.dork_linkedin}")
            
            if self.dork_social_media:
                unique_social = {}
                for social in self.dork_social_media:
                    if social['platform'] not in unique_social:
                        unique_social[social['platform']] = social['url']
                
                for platform, url in unique_social.items():
                    print(f"  {platform}: {url}")
                    report.append(f"  {platform}: {url}")
            
            if not self.dork_linkedin and not self.dork_social_media:
                print(f"{Fore.YELLOW}  No se encontraron perfiles sociales{Style.RESET_ALL}")
                report.append("  No se encontraron perfiles sociales")
        
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
        print(f"{Fore.GREEN}💬 CHATBOTS/WIDGETS DE ATENCIÓN ({len(self.chatbots)}):")
        print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        report.append(f"\n\n💬 CHATBOTS/WIDGETS DE ATENCIÓN ({len(self.chatbots)}):")
        report.append("-"*70)
        if self.chatbots:
            for idx, chatbot in enumerate(self.chatbots, 1):
                bot_type = chatbot['type'].upper()
                bot_url = chatbot.get('url', 'N/A')
                
                # Formato especial para WhatsApp
                if chatbot['type'] == 'whatsapp':
                    phone = chatbot.get('phone', '')
                    print(f"  {idx}. {bot_type}")
                    print(f"     Teléfono: {phone}")
                    print(f"     Link: {bot_url}")
                    report.append(f"  {idx}. {bot_type}")
                    report.append(f"     Teléfono: {phone}")
                    report.append(f"     Link: {bot_url}")
                else:
                    print(f"  {idx}. {bot_type}")
                    if bot_url != 'detected':
                        print(f"     URL/ID: {bot_url}")
                        report.append(f"  {idx}. {bot_type}")
                        report.append(f"     URL/ID: {bot_url}")
                    else:
                        print(f"     Status: Detectado (sin URL específica)")
                        report.append(f"  {idx}. {bot_type}")
                        report.append(f"     Status: Detectado (sin URL específica)")
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
        
        # === SECCIÓN DE INTELIGENCIA ===
        if self.email_intelligence or self.phone_intelligence or self.attack_vectors:
            print(f"\n\n{Fore.YELLOW}{'='*70}")
            print(f"{Fore.CYAN}🧠 ANÁLISIS DE INTELIGENCIA Y VECTORES DE ATAQUE")
            print(f"{Fore.YELLOW}{'='*70}{Style.RESET_ALL}\n")
            
            intel_report = []
            intel_report.append("\n\n" + "="*70)
            intel_report.append("🧠 ANÁLISIS DE INTELIGENCIA Y VECTORES DE ATAQUE")
            intel_report.append("="*70)
            
            # Infraestructura de Email
            if self.email_intelligence:
                print(f"{Fore.CYAN}{'─'*70}")
                print(f"{Fore.GREEN}📧 INFRAESTRUCTURA DE EMAIL:")
                print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
                intel_report.append("\n📧 INFRAESTRUCTURA DE EMAIL:")
                intel_report.append("-"*70)
                
                for domain, info in self.email_intelligence.items():
                    print(f"\n  Dominio: {Fore.YELLOW}{domain}{Style.RESET_ALL}")
                    print(f"  Emails encontrados: {info['email_count']}")
                    print(f"  Proveedor: {info['provider']}")
                    print(f"  Servidor de correo: {info['mail_server']}")
                    
                    intel_report.append(f"\n  Dominio: {domain}")
                    intel_report.append(f"  Emails encontrados: {info['email_count']}")
                    intel_report.append(f"  Proveedor: {info['provider']}")
                    intel_report.append(f"  Servidor de correo: {info['mail_server']}")
                    
                    if info['mx_records']:
                        print(f"  Registros MX: {', '.join(info['mx_records'][:2])}")
                        intel_report.append(f"  Registros MX: {', '.join(info['mx_records'][:2])}")
                    
                    # Seguridad
                    spf_status = info['security'].get('spf', 'No configurado')
                    dmarc_status = info['security'].get('dmarc', 'No configurado')
                    
                    spf_color = Fore.GREEN if spf_status == 'Configurado' else Fore.RED
                    dmarc_color = Fore.GREEN if dmarc_status == 'Configurado' else Fore.RED
                    
                    print(f"  Seguridad:")
                    print(f"    SPF: {spf_color}{spf_status}{Style.RESET_ALL}")
                    print(f"    DMARC: {dmarc_color}{dmarc_status}{Style.RESET_ALL}")
                    
                    intel_report.append(f"  Seguridad:")
                    intel_report.append(f"    SPF: {spf_status}")
                    intel_report.append(f"    DMARC: {dmarc_status}")
                    
                    # Nivel de seguridad
                    if spf_status == 'Configurado' and dmarc_status == 'Configurado':
                        security_level = 'Alto'
                        color = Fore.GREEN
                    elif spf_status == 'Configurado' or dmarc_status == 'Configurado':
                        security_level = 'Medio'
                        color = Fore.YELLOW
                    else:
                        security_level = 'Bajo'
                        color = Fore.RED
                    
                    print(f"  Nivel de seguridad: {color}{security_level}{Style.RESET_ALL}")
                    intel_report.append(f"  Nivel de seguridad: {security_level}")
            
            # Análisis Telefónico
            if self.phone_intelligence:
                print(f"\n{Fore.CYAN}{'─'*70}")
                print(f"{Fore.GREEN}📞 ANÁLISIS TELEFÓNICO:")
                print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
                intel_report.append("\n\n📞 ANÁLISIS TELEFÓNICO:")
                intel_report.append("-"*70)
                
                # Agrupar por país
                countries = Counter([p['country'] for p in self.phone_intelligence])
                types = Counter([p['type'] for p in self.phone_intelligence])
                
                print(f"\n  Distribución geográfica:")
                intel_report.append("\n  Distribución geográfica:")
                for country, count in countries.most_common():
                    print(f"    • {country}: {count} número(s)")
                    intel_report.append(f"    • {country}: {count} número(s)")
                
                print(f"\n  Tipos de línea:")
                intel_report.append("\n  Tipos de línea:")
                for phone_type, count in types.most_common():
                    print(f"    • {phone_type}: {count}")
                    intel_report.append(f"    • {phone_type}: {count}")
                
                # Detalles individuales
                print(f"\n  Detalle de números:")
                intel_report.append("\n  Detalle de números:")
                for phone in self.phone_intelligence[:10]:  # Limitar a 10
                    area_info = f" - {phone['area']}" if phone['area'] else ""
                    print(f"    • {phone['number']}: {phone['country']} ({phone['type']}){area_info}")
                    intel_report.append(f"    • {phone['number']}: {phone['country']} ({phone['type']}){area_info}")
            
            # Vectores de Ataque
            if self.attack_vectors:
                print(f"\n{Fore.CYAN}{'─'*70}")
                print(f"{Fore.GREEN}🎯 VECTORES DE ATAQUE IDENTIFICADOS:")
                print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
                intel_report.append("\n\n🎯 VECTORES DE ATAQUE IDENTIFICADOS:")
                intel_report.append("-"*70)
                
                for idx, vector in enumerate(self.attack_vectors, 1):
                    prob_color = Fore.RED if vector['probability'] in ['Alta', 'Muy Alta'] else (Fore.YELLOW if vector['probability'] == 'Media' else Fore.GREEN)
                    
                    print(f"\n  {idx}. {Fore.CYAN}{vector['type']}{Style.RESET_ALL}")
                    print(f"     Probabilidad: {prob_color}{vector['probability']}{Style.RESET_ALL}")
                    print(f"     Descripción: {vector['description']}")
                    print(f"     Técnicas sugeridas:")
                    
                    intel_report.append(f"\n  {idx}. {vector['type']}")
                    intel_report.append(f"     Probabilidad: {vector['probability']}")
                    intel_report.append(f"     Descripción: {vector['description']}")
                    intel_report.append(f"     Técnicas sugeridas:")
                    
                    for technique in vector['techniques']:
                        print(f"       • {technique}")
                        intel_report.append(f"       • {technique}")
            
            # Perfil de Seguridad
            if self.security_profile:
                print(f"\n{Fore.CYAN}{'─'*70}")
                print(f"{Fore.GREEN}⚠️  SUPERFICIE DE ATAQUE:")
                print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
                intel_report.append("\n\n⚠️  SUPERFICIE DE ATAQUE:")
                intel_report.append("-"*70)
                
                exposure_color = Fore.RED if self.security_profile['exposure_level'] == 'Alta' else (Fore.YELLOW if self.security_profile['exposure_level'] == 'Media' else Fore.GREEN)
                
                print(f"\n  Nivel de exposición: {exposure_color}{self.security_profile['exposure_level']}{Style.RESET_ALL}")
                intel_report.append(f"\n  Nivel de exposición: {self.security_profile['exposure_level']}")
                
                print(f"\n  Elementos expuestos:")
                intel_report.append("\n  Elementos expuestos:")
                for surface in self.security_profile['attack_surface']:
                    print(f"    • {surface}")
                    intel_report.append(f"    • {surface}")
                
                if self.security_profile['primary_vectors']:
                    print(f"\n  Vectores primarios:")
                    intel_report.append("\n  Vectores primarios:")
                    for vector in self.security_profile['primary_vectors']:
                        print(f"    • {Fore.RED}{vector}{Style.RESET_ALL}")
                        intel_report.append(f"    • {vector}")
                
                # Recomendaciones
                print(f"\n{Fore.CYAN}{'─'*70}")
                print(f"{Fore.GREEN}🛡️  RECOMENDACIONES DE SEGURIDAD:")
                print(f"{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
                intel_report.append("\n\n🛡️  RECOMENDACIONES DE SEGURIDAD:")
                intel_report.append("-"*70)
                
                for idx, rec in enumerate(self.security_profile['recommendations'], 1):
                    print(f"  {idx}. {rec}")
                    intel_report.append(f"  {idx}. {rec}")
            
            # Guardar reporte de inteligencia
            intel_filename = f"gen_intelligence_{self.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            try:
                with open(intel_filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(intel_report))
                print(f"\n{Fore.GREEN}[✓] Reporte de inteligencia guardado en: {Fore.WHITE}{intel_filename}{Style.RESET_ALL}")
            except Exception as e:
                print(f"\n{Fore.RED}[!] Error al guardar reporte de inteligencia: {e}{Style.RESET_ALL}")
        
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
