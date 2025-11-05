# Web Scraping de MercadoLibre México

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Selenium-4.0+-green.svg" alt="Selenium Version">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

Este proyecto contiene scripts automatizados de web scraping para extraer información detallada de productos de **MercadoLibre México** usando Selenium con diferentes navegadores. Diseñado específicamente para el formato de precios mexicanos (MXN) y con múltiples métodos de extracción robustos.

## Estructura del Proyecto

```
web-scraping/
├── 📄 Scraping-Selenium-chrome.py     # Script optimizado para Chrome
├── 📄 scraping-Selenium-safari.py     # Script optimizado para Safari
├── 📂 output-chrome/                  # Resultados de Chrome
│   ├── productos_chrome_*.json        # Datos extraídos en JSON
│   ├── clean_productos_chrome_*.json  # Versión limpia sin debug
│   ├── pagina_mercadolibre_chrome.png # Screenshot de la página
│   └── producto_chrome_*.png          # Screenshots individuales
├── 📂 output-safari/                  # Resultados de Safari
│   ├── productos_safari_*.json        # Datos extraídos en JSON
│   ├── clean_productos_safari_*.json  # Versión limpia sin debug
│   ├── pagina_mercadolibre_safari.png # Screenshot de la página
│   ├── source_safari.html             # HTML de la página
│   └── producto_safari_*.png          # Screenshots individuales
└── 📖 README.md                       # Este archivo
```

## Características Principales

| Característica | Descripción |
|----------------|-------------|
| **Extracción completa** | Títulos, precios (MXN) y URLs con múltiples métodos de respaldo |
| **Multi-navegador** | Soporte para Chrome y Safari |
| **Formato mexicano** | Optimizado para precios en pesos mexicanos |
| **Debug visual** | Screenshots automáticos para análisis |
| **Datos estructurados** | Exportación en JSON con metadatos de extracción |
| **Versiones limpias** | Archivos sin datos de debugging |
| **Organización** | Resultados separados por navegador |
| **Métodos de Respaldo** | Múltiples estrategias de extracción |

## Requisitos del sistema

### Python y Dependencias
```bash
# Python 3.8 o superior
python --version

# Instalar dependencias para Chrome
pip install selenium webdriver-manager

# Instalar dependencias para Safari (solo macOS)
pip install selenium
```

### Configuración de navegadores

#### Chrome
- Instalación automática del ChromeDriver mediante `webdriver-manager`
- No requiere configuración adicional

#### Safari (solo macOS)
1. Abrir Safari
2. Ir a **Menú Safari** → **Preferencias** → **Avanzado**
3. Marcar "Mostrar el menú Desarrollo en la barra de menús"
4. Ir a **Menú Desarrollo** → **Permitir automatización remota**

## Uso del sistema

### Ejecución rápida

#### Para Chrome:
```bash
cd web-scraping
python Scraping-Selenium-chrome.py
```

#### Para Safari:
```bash
cd web-scraping
python scraping-Selenium-safari.py
```

### Ejemplo de sesión interactiva
```
=== WEB SCRAPING DE MERCADO LIBRE (CHROME) - OPTIMIZADO PARA FORMATO MX ===
Producto a buscar: iPhone 15
Número de páginas a procesar (1-5): 2

[11:30:15] Iniciando Chrome WebDriver para buscar 'iPhone 15'
[11:30:18] Navegando a: https://listado.mercadolibre.com.mx/iPhone-15
[11:30:22] Procesando 15 productos...
[11:30:45] Se obtuvieron 15 productos
[11:30:45] Datos guardados en: output-chrome/productos_chrome_iPhone_15_20251105_113045.json
```

## Archivos de salida

### Tipos de Archivos Generados

| Archivo | Descripción | Ejemplo |
|---------|-------------|---------|
| **productos_[navegador]_[término]_[timestamp].json** | Datos completos con información de debug | `productos_chrome_iPhone_15_20251105_113045.json` |
| **clean_productos_[navegador]_[término]_[timestamp].json** | Versión limpia para producción | `clean_productos_chrome_iPhone_15_20251105_113045.json` |
| **pagina_mercadolibre_[navegador].png** | Screenshot de la página completa | `pagina_mercadolibre_chrome.png` |
| **producto_[navegador]_[N].png** | Screenshots individuales | `producto_chrome_1.png` |
| **source_[navegador].html** | HTML completo (solo Safari) | `source_safari.html` |

### Estructura de Datos JSON

```json
{
  "titulo": "iPhone 15 128GB Azul",
  "precio": "$ 19,999",
  "url": "https://articulo.mercadolibre.com.mx/...",
  "posicion": 1,
  "metodo_extraccion": {
    "titulo": "xpath_title_class",
    "precio": "componentes_separados",
    "url": "class_link"
  }
}
```

## Características técnicas

### Métodos de extracción implementados

#### **Títulos**
1. `xpath_title_class` - Selector específico de MercadoLibre
2. `tag_h2` - Elementos H2 genéricos
3. `attr_title` - Atributo title de elementos
4. `javascript_title` - Extracción con JavaScript

#### **Precios**
1. `componentes_separados` - Símbolo + fracción + decimales
2. `texto_directo` - Texto completo del precio
3. `javascript_precio_mx` - JavaScript para formato mexicano
4. `regex_pattern` - Patrones de expresiones regulares
5. `contains_dollar_sign` - Elementos que contengan "$"

#### **URLs**
1. `class_link` - Enlaces con clase específica
2. `tag_a` - Enlaces genéricos
3. `javascript` - Extracción con JavaScript

### Configuraciones de navegador

#### Chrome
```python
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0...")
chrome_options.add_argument("--disable-search-engine-choice-screen")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-popup-blocking")
```

#### Safari
```python
driver = webdriver.Safari()
driver.set_window_size(1280, 800)
# Configuración automática para macOS
```

## Estadísticas y monitoreo

El sistema proporciona estadísticas detalladas de extracción:

```
=== RESULTADOS FINALES ===
Se obtuvieron 15 productos
Títulos extraídos correctamente: 15/15 (100.0%)
Precios extraídos correctamente: 14/15 (93.3%)
URLs extraídas correctamente: 15/15 (100.0%)

Métodos de extracción utilizados:
Título: xpath_title_class(12), tag_h2(3)
Precio: componentes_separados(10), texto_directo(4), regex_pattern(1)
URL: class_link(13), tag_a(2)
```

## Solución de problemas

### Problemas comunes

#### Chrome no se inicia
```bash
# Verificar instalación
which google-chrome
# Reinstalar webdriver-manager
pip uninstall webdriver-manager
pip install webdriver-manager
```

#### Safari no responde (macOS)
1. Verificar que la automatización remota esté habilitada
2. Reiniciar Safari completamente
3. Verificar permisos del sistema

#### No se extraen precios
- Los selectores pueden haber cambiado
- Verificar screenshots generados
- Revisar el archivo HTML de debug (Safari)

### Logs de debug

El sistema genera logs detallados con timestamps:
```
[11:30:15] Iniciando Chrome WebDriver para buscar 'iPhone 15'
[11:30:18] Navegando a: https://listado.mercadolibre.com.mx/iPhone-15
[11:30:20] Contenedor principal encontrado: //section[@class="ui-search-results"]
[11:30:22] Detectada vista de cuadrícula con 60 productos
[11:30:23] Procesando producto 1/15
[11:30:24] Título encontrado con selector específico: iPhone 15 128GB...
[11:30:24] Precio completo extraído por componentes: $ 19,999
```

## Versionado y Actualizaciones

- **v1.0** - Versión inicial con soporte básico
- **v1.1** - Añadido soporte para Safari
- **v1.2** - Organización por carpetas de navegador
- **v1.3** - Múltiples métodos de extracción
- **v1.4** - Optimización para formato mexicano

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Descargo de responsabilidad

Este proyecto es solo para fines educativos. Asegúrate de cumplir con los términos de servicio de MercadoLibre y las leyes locales sobre web scraping.

---

<p align="center">
  <strong>Hecho con ❤️ para automatizar la extracción de datos de MercadoLibre México</strong>
</p>