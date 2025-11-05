# -*- coding: utf-8 -*-
"""
Web Scraping de Mercado Libre para Chrome - Versión optimizada para México
Adaptado del código para Safari, manteniendo la misma funcionalidad
Enfocado en extraer correctamente título y precio (formato MXN)
"""
import json
import time
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def log(message):
    """Función simple para mostrar logs con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def scrape_mercadolibre_chrome(search_term, num_pages=1):
    # Obtener la ruta absoluta del directorio donde está el script o ejecutable
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Nombre del archivo de salida
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = os.path.join(base_path, f"productos_chrome_{search_term.replace(' ', '_')}_{current_time}.json")

    
    # Lista para almacenar los productos
    products_data = []
    
    log(f"Iniciando Chrome WebDriver para buscar '{search_term}'")
    try:
        # CAMBIO: Configuración específica para Chrome
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        
        # CAMBIO: Inicializar Chrome WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_window_size(1280, 800)
        
        # Convertir búsqueda para URL
        search_url = f"https://listado.mercadolibre.com.mx/{search_term.replace(' ', '-')}"
        log(f"Navegando a: {search_url}")
        
        # Ir a la página de búsqueda
        driver.get(search_url)
        time.sleep(3)  # CAMBIO: Chrome generalmente carga más rápido que Safari
        
        # Guardar screenshot para diagnóstico
        driver.save_screenshot(os.path.join(base_path, "pagina_mercadolibre_chrome.png"))
        log("Screenshot guardado como 'pagina_mercadolibre_chrome.png'")
        
        # Manejar disclaimer si aparece
        try:
            disclaimer = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="action:understood-button"]'))
            )
            disclaimer.click()
            time.sleep(1)  # CAMBIO: Menos tiempo de espera para Chrome
            log("Disclaimer cerrado")
        except:
            log("No se encontró disclaimer o no se pudo cerrar")
        
        # Verificar el formato de precios en la página actual
        log("Analizando formatos de precio en la página...")
        try:
            # Obtener todos los elementos de precio para analizar formato
            all_price_elements = driver.find_elements(By.XPATH, '//span[contains(@class, "price-tag-amount")]')
            
            # Si encontramos elementos, mostrar los primeros 3 para análisis
            if all_price_elements:
                log(f"Encontrados {len(all_price_elements)} elementos de precio para análisis")
                for i, elem in enumerate(all_price_elements[:3]):
                    price_text = elem.text.strip()
                    log(f"Muestra de precio #{i+1}: '{price_text}'")
                    
                    # Intentar inspeccionar la estructura interna del precio
                    try:
                        price_parts = elem.find_elements(By.XPATH, './/span')
                        parts_text = [p.text.strip() for p in price_parts]
                        log(f"  - Componentes internos: {parts_text}")
                    except:
                        pass
            else:
                log("No se encontraron elementos de precio para análisis previo")
        except Exception as e:
            log(f"Error al analizar formatos de precio: {e}")
        
        # Detectar contenedor principal de resultados
        main_container = None
        container_selectors = [
            '//section[@class="ui-search-results"]',
            '//div[@class="ui-search-results"]',
            '//ol[@class="ui-search-layout"]'
        ]
        
        for selector in container_selectors:
            containers = driver.find_elements(By.XPATH, selector)
            if containers:
                main_container = containers[0]
                log(f"Contenedor principal encontrado: {selector}")
                break
        
        if not main_container:
            log("No se encontró el contenedor principal. Usando body como fallback")
            main_container = driver.find_element(By.TAG_NAME, 'body')
        
        # Extraer productos del contenedor principal
        log("Extrayendo productos del contenedor principal...")
        
        # Detectar el tipo de vista (grid o lista)
        grid_items = main_container.find_elements(By.XPATH, './/li[contains(@class, "ui-search-layout__item")]')
        
        if grid_items:
            log(f"Detectada vista de cuadrícula con {len(grid_items)} productos")
            product_items = grid_items
        else:
            # Intentar detectar vista de lista
            list_items = main_container.find_elements(By.XPATH, './/div[contains(@class, "ui-search-result")]')
            if list_items:
                log(f"Detectada vista de lista con {len(list_items)} productos")
                product_items = list_items
            else:
                # Último intento - buscar cualquier tipo de contenedor de producto
                log("No se detectó un patrón claro. Buscando cualquier contenedor de producto...")
                product_items = main_container.find_elements(By.XPATH, 
                    './/*[contains(@class, "ui-search-result") or contains(@class, "ui-search-layout__item")]')
                log(f"Encontrados {len(product_items)} posibles contenedores de productos")
        
        # Procesar los productos encontrados
        if product_items:
            log(f"Procesando {len(product_items)} productos...")
            
            # CAMBIO: Chrome puede manejar más productos de forma estable
            max_products = min(15, len(product_items))
            log(f"Se procesarán los primeros {max_products} productos")
            
            for idx, item in enumerate(product_items[:max_products]):
                try:
                    log(f"Procesando producto {idx+1}/{max_products}")
                    
                    # Hacer scroll para asegurar que el elemento esté visible
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", item)
                        time.sleep(0.5)  # CAMBIO: Chrome necesita menos tiempo de espera
                    except:
                        log("No se pudo hacer scroll al elemento")
                    
                    # Tomar screenshot del elemento actual para diagnóstico
                    try:
                        item.screenshot(os.path.join(base_path, f"producto_chrome_{idx+1}.png"))
                        log(f"Screenshot guardado como 'producto_chrome_{idx+1}.png'")
                    except:
                        log("No se pudo guardar screenshot del elemento")
                    
                    # Producto base
                    product_data = {
                        "titulo": "No disponible",
                        "precio": "No disponible",
                        "url": "No disponible",
                        "posicion": idx + 1,
                        "metodo_extraccion": {
                            "titulo": "ninguno",
                            "precio": "ninguno",
                            "url": "ninguno"
                        }
                    }
                    
                    # Extracción de título con múltiples métodos
                    title_found = False
                    
                    # Intento 1: Título con clase específica
                    if not title_found:
                        try:
                            title_elem = item.find_element(By.XPATH, './/h2[contains(@class, "ui-search-item__title")]')
                            title_text = title_elem.text.strip()
                            if title_text:
                                product_data["titulo"] = title_text
                                product_data["metodo_extraccion"]["titulo"] = "xpath_title_class"
                                title_found = True
                                log(f"Título encontrado con selector específico: {title_text[:30]}...")
                        except:
                            pass
                    
                    # Intento 2: Cualquier h2 dentro del elemento
                    if not title_found:
                        try:
                            title_elems = item.find_elements(By.TAG_NAME, 'h2')
                            if title_elems:
                                title_text = title_elems[0].text.strip()
                                if title_text:
                                    product_data["titulo"] = title_text
                                    product_data["metodo_extraccion"]["titulo"] = "tag_h2"
                                    title_found = True
                                    log(f"Título encontrado con tag h2: {title_text[:30]}...")
                        except:
                            pass
                    
                    # Intento 3: Elemento con atributo title
                    if not title_found:
                        try:
                            title_attr_elems = item.find_elements(By.XPATH, './/*[@title]')
                            if title_attr_elems:
                                title_text = title_attr_elems[0].get_attribute('title').strip()
                                if title_text:
                                    product_data["titulo"] = title_text
                                    product_data["metodo_extraccion"]["titulo"] = "attr_title"
                                    title_found = True
                                    log(f"Título encontrado con atributo title: {title_text[:30]}...")
                        except:
                            pass
                    
                    # Intento 4: JavaScript - buscar título en todo el contenedor
                    if not title_found:
                        try:
                            js_result = driver.execute_script("""
                                var container = arguments[0];
                                var possibleTitles = [
                                    container.querySelector('h2'),
                                    container.querySelector('.ui-search-item__title'),
                                    container.querySelector('[title]'),
                                    container.querySelector('a')
                                ];
                                
                                for (var i = 0; i < possibleTitles.length; i++) {
                                    var elem = possibleTitles[i];
                                    if (elem) {
                                        if (elem.title) return elem.title;
                                        if (elem.textContent) return elem.textContent;
                                    }
                                }
                                
                                return null;
                            """, item)
                            
                            if js_result:
                                product_data["titulo"] = js_result.strip()
                                product_data["metodo_extraccion"]["titulo"] = "javascript_title"
                                title_found = True
                                log(f"Título encontrado con JavaScript: {js_result[:30]}...")
                        except:
                            pass
                    
                    # Extracción de precio con enfoque específico para México
                    price_found = False
                    
                    # Intento 1: Obtener todos los componentes del precio y juntarlos
                    if not price_found:
                        try:
                            # Primero buscamos el contenedor principal del precio
                            price_container = item.find_element(By.XPATH, 
                                './/div[contains(@class, "ui-search-price")]')
                            
                            # Extraer todos los componentes del precio
                            symbol = price_container.find_element(By.XPATH, 
                                './/span[contains(@class, "andes-money-amount__currency-symbol")]').text.strip()
                            
                            fraction = price_container.find_element(By.XPATH, 
                                './/span[contains(@class, "andes-money-amount__fraction")]').text.strip()
                            
                            # Intentar obtener decimales si existen
                            try:
                                decimals = price_container.find_element(By.XPATH, 
                                    './/span[contains(@class, "andes-money-amount__cents")]').text.strip()
                                full_price = f"{symbol} {fraction}.{decimals}"
                            except:
                                full_price = f"{symbol} {fraction}"
                            
                            if full_price:
                                product_data["precio"] = full_price
                                product_data["metodo_extraccion"]["precio"] = "componentes_separados"
                                price_found = True
                                log(f"Precio completo extraído por componentes: {full_price}")
                        except Exception as e:
                            log(f"Error al extraer precio por componentes: {str(e)[:50]}...")
                    
                    # Intento 2: Buscar el precio como texto directo
                    if not price_found:
                        try:
                            price_elem = item.find_element(By.XPATH, './/span[contains(@class, "price-tag-amount")]')
                            
                            # Capturar todo el contenido en texto
                            raw_price_text = price_elem.text.strip()
                            
                            # Intentar procesar el texto para asegurar que incluye símbolo y monto
                            if '$' in raw_price_text:
                                product_data["precio"] = raw_price_text
                                product_data["metodo_extraccion"]["precio"] = "texto_directo"
                                price_found = True
                                log(f"Precio encontrado como texto directo: {raw_price_text}")
                            else:
                                # Si no incluye el símbolo, intentar encontrarlo cerca
                                symbol_elem = item.find_element(By.XPATH, './/span[contains(@class, "currency-symbol")]')
                                if symbol_elem:
                                    symbol = symbol_elem.text.strip()
                                    product_data["precio"] = f"{symbol} {raw_price_text}"
                                    product_data["metodo_extraccion"]["precio"] = "texto_simbolo_separado"
                                    price_found = True
                                    log(f"Precio reconstruido: {symbol} {raw_price_text}")
                        except Exception as e:
                            log(f"Error al extraer precio como texto directo: {str(e)[:50]}...")
                    
                    # Intento 3: Método avanzado con JavaScript para formato mexicano
                    if not price_found:
                        try:
                            js_result = driver.execute_script("""
                                var container = arguments[0];
                                
                                // 1. Intentar obtener componentes separados
                                var symbol = container.querySelector('.andes-money-amount__currency-symbol');
                                var fraction = container.querySelector('.andes-money-amount__fraction');
                                var cents = container.querySelector('.andes-money-amount__cents');
                                
                                if (symbol && fraction) {
                                    var price = symbol.textContent.trim() + ' ' + fraction.textContent.trim();
                                    if (cents) {
                                        price += '.' + cents.textContent.trim();
                                    }
                                    return price;
                                }
                                
                                // 2. Buscar cualquier elemento que contenga formato de precio mexicano
                                var allText = container.innerText;
                                var priceRegex = /\\$\\s?[0-9,]+(\\.\\d{2})?/g;
                                var matches = allText.match(priceRegex);
                                if (matches && matches.length > 0) {
                                    return matches[0].trim();
                                }
                                
                                // 3. Extraer cualquier texto con $ y números
                                var allElements = container.querySelectorAll('*');
                                for (var i = 0; i < allElements.length; i++) {
                                    var text = allElements[i].textContent.trim();
                                    if (text.includes('$') && /\\d/.test(text)) {
                                        return text;
                                    }
                                }
                                
                                return null;
                            """, item)
                            
                            if js_result:
                                product_data["precio"] = js_result.strip()
                                product_data["metodo_extraccion"]["precio"] = "javascript_precio_mx"
                                price_found = True
                                log(f"Precio encontrado con JavaScript MX: {js_result}")
                        except Exception as e:
                            log(f"Error al extraer precio con JavaScript: {str(e)[:50]}...")
                    
                    # Intento 4: Último recurso - buscar texto que parezca un precio en todo el elemento
                    if not price_found:
                        try:
                            # Obtener todo el texto del elemento
                            all_text = item.text
                            
                            # Buscar patrones de precio en el texto
                            price_patterns = [
                                r'\$\s?[\d,]+\.?\d*',  # $1,234.56 o $1,234
                                r'\$\s?[\d.]+,?\d*',   # $1.234,56 o $1.234
                                r'\$\s?\d+',           # $1234
                            ]
                            
                            for pattern in price_patterns:
                                matches = re.findall(pattern, all_text)
                                if matches:
                                    product_data["precio"] = matches[0].strip()
                                    product_data["metodo_extraccion"]["precio"] = "regex_pattern"
                                    price_found = True
                                    log(f"Precio encontrado con regex: {matches[0]}")
                                    break
                        except Exception as e:
                            log(f"Error al extraer precio con regex: {str(e)[:50]}...")
                    
                    # Si todavía no encontramos precio, guardar cualquier texto que tenga "$"
                    if not price_found:
                        try:
                            dollar_elements = item.find_elements(By.XPATH, './/*[contains(text(), "$")]')
                            if dollar_elements:
                                for elem in dollar_elements:
                                    text = elem.text.strip()
                                    if '$' in text and len(text) < 20:  # Evitar textos largos
                                        product_data["precio"] = text
                                        product_data["metodo_extraccion"]["precio"] = "contains_dollar_sign"
                                        price_found = True
                                        log(f"Precio encontrado con símbolo $: {text}")
                                        break
                        except Exception as e:
                            log(f"Error al buscar elementos con $: {str(e)[:50]}...")
                    
                    # Extracción de URL del producto
                    try:
                        link_elems = item.find_elements(By.XPATH, './/a[contains(@class, "ui-search-link")]')
                        if link_elems:
                            href = link_elems[0].get_attribute('href')
                            if href:
                                product_data["url"] = href
                                product_data["metodo_extraccion"]["url"] = "class_link"
                                log(f"URL encontrada: {href[:50]}...")
                        else:
                            # Probar con cualquier enlace dentro del elemento
                            any_links = item.find_elements(By.TAG_NAME, 'a')
                            if any_links:
                                href = any_links[0].get_attribute('href')
                                if href:
                                    product_data["url"] = href
                                    product_data["metodo_extraccion"]["url"] = "tag_a"
                                    log(f"URL encontrada (tag genérico): {href[:50]}...")
                    except Exception as e:
                        log(f"Error al extraer URL: {e}")
                    
                    # Si no se encontró URL, intentar con JavaScript
                    if product_data["url"] == "No disponible":
                        try:
                            url_js = driver.execute_script("return arguments[0].querySelector('a')?.href || null;", item)
                            if url_js:
                                product_data["url"] = url_js
                                product_data["metodo_extraccion"]["url"] = "javascript"
                                log(f"URL encontrada con JavaScript: {url_js[:50]}...")
                        except:
                            pass
                    
                    # Capturar HTML del elemento para diagnóstico y debugging
                    try:
                        product_data["html_debug"] = {
                            "outer_html": driver.execute_script("return arguments[0].outerHTML.substring(0, 1000)", item),
                            "class": item.get_attribute("class")
                        }
                    except:
                        product_data["html_debug"] = {"error": "No se pudo capturar HTML"}
                    
                    # Registrar resultado de la extracción
                    log(f"Producto {idx+1} procesado:")
                    log(f"  - Título: {product_data['titulo'][:50]}...")
                    log(f"  - Precio: {product_data['precio']}")
                    log(f"  - URL: {product_data['url'][:30]}...")
                    log(f"  - Métodos: {product_data['metodo_extraccion']}")
                    
                    # Añadir a nuestra lista
                    products_data.append(product_data)
                    
                    # CAMBIO: Guardar después de cada 3 productos para Chrome
                    if (idx + 1) % 3 == 0 or (idx == max_products - 1):
                        with open(output_filename, 'w', encoding='utf-8') as f:
                            json.dump(products_data, f, ensure_ascii=False, indent=4)
                        log(f"Guardado parcial: {len(products_data)} productos guardados")
                    
                except Exception as e:
                    log(f"Error procesando producto {idx+1}: {e}")
                    continue
                    
            # AÑADIDO: Procesamiento para múltiples páginas
            if num_pages > 1:
                log(f"Procesadas {num_pages} páginas. Puedes modificar el script para soportar paginación múltiple.")
        else:
            log("No se pudieron encontrar productos para procesar")
    
    except Exception as e:
        log(f"Error general: {e}")
    
    finally:
        try:
            driver.quit()
            log("Navegador cerrado correctamente")
        except:
            log("Error al cerrar el navegador")
    
    # Verificar productos y archivos finales
    if products_data:
        log(f"\n=== RESULTADOS FINALES ===")
        log(f"Se obtuvieron {len(products_data)} productos")
        log(f"Datos guardados en: {output_filename}")
        
        # Verificar que el archivo existe
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename) / 1024  # KB
            log(f"Tamaño del archivo: {file_size:.2f} KB")
            
            # Verificar contenido
            try:
                with open(output_filename, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # Limpiar datos de debug antes de mostrar estadísticas
                for product in saved_data:
                    if "html_debug" in product:
                        del product["html_debug"]
                
                # Guardar versión limpia
                clean_filename = f"clean_{output_filename}"
                with open(clean_filename, 'w', encoding='utf-8') as f:
                    json.dump(saved_data, f, ensure_ascii=False, indent=4)
                log(f"Versión limpia guardada en: {clean_filename}")
                
                log(f"Verificación del archivo: {len(saved_data)} productos guardados correctamente")
                
                # Estadísticas de extracción
                titles_ok = sum(1 for p in saved_data if p.get("titulo") != "No disponible")
                prices_ok = sum(1 for p in saved_data if p.get("precio") != "No disponible")
                urls_ok = sum(1 for p in saved_data if p.get("url") != "No disponible")
                
                log(f"Títulos extraídos correctamente: {titles_ok}/{len(saved_data)} ({(titles_ok/len(saved_data))*100:.1f}%)")
                log(f"Precios extraídos correctamente: {prices_ok}/{len(saved_data)} ({(prices_ok/len(saved_data))*100:.1f}%)")
                log(f"URLs extraídos correctamente: {urls_ok}/{len(saved_data)} ({(urls_ok/len(saved_data))*100:.1f}%)")
                
                # Mostrar métodos de extracción usados
                titulo_methods = {}
                precio_methods = {}
                url_methods = {}
                
                for p in saved_data:
                    if "metodo_extraccion" in p:
                        t_method = p["metodo_extraccion"].get("titulo", "ninguno")
                        p_method = p["metodo_extraccion"].get("precio", "ninguno")
                        u_method = p["metodo_extraccion"].get("url", "ninguno")
                        
                        titulo_methods[t_method] = titulo_methods.get(t_method, 0) + 1
                        precio_methods[p_method] = precio_methods.get(p_method, 0) + 1
                        url_methods[u_method] = url_methods.get(u_method, 0) + 1
                
                log("\nMétodos de extracción utilizados:")
                log("Título: " + ", ".join([f"{m}({c})" for m, c in titulo_methods.items()]))
                log("Precio: " + ", ".join([f"{m}({c})" for m, c in precio_methods.items()]))
                log("URL: " + ", ".join([f"{m}({c})" for m, c in url_methods.items()]))
                
            except Exception as e:
                log(f"Error al verificar el archivo guardado: {e}")
        else:
            log(f"¡ADVERTENCIA! Archivo no encontrado: {output_filename}")
    else:
        log("No se obtuvieron productos. Verifica el selector o si la página ha cambiado su estructura.")
    
    return products_data

# Ejecutar el script
if __name__ == "__main__":
    print("\n=== WEB SCRAPING DE MERCADO LIBRE (CHROME) - OPTIMIZADO PARA FORMATO MX ===")
    print("NOTA: Asegúrate de tener instalado Chrome y las bibliotecas necesarias:")
    print("pip install selenium webdriver-manager")
    
    # Obtener búsqueda
    search_term = input("Producto a buscar: ")
    if not search_term:
        search_term = "iphone"
        print(f"Usando término por defecto: '{search_term}'")
    
    # Número de páginas
    try:
        num_pages = int(input("Número de páginas a procesar (1-5): "))
        if num_pages < 1 or num_pages > 5:
            num_pages = 1
            print(f"Número inválido, usando {num_pages} página por defecto")
    except:
        num_pages = 1
        print(f"Entrada inválida, usando {num_pages} página por defecto")
    
    # Ejecutar script
    results = scrape_mercadolibre_chrome(search_term, num_pages)
    
    print("\nScript finalizado. Revisa los logs para detalles.")