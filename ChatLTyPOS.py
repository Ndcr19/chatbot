import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    import spacy
except ImportError as e:
    print("❌ Error al importar dependencias:", str(e))
    print("📦 Por favor instala las dependencias con:")
    print("   pip install nltk spacy")
    print("   python -m spacy download es_core_news_sm")
    sys.exit(1)

def configurar_nltk():
    """Configura los recursos necesarios de NLTK"""
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
    except Exception as e:
        print(f"⚠️ Error al configurar NLTK: {e}")

def inicializar_modelos():
    """Inicializa los modelos de procesamiento de texto"""
    configurar_nltk()
    try:
        return WordNetLemmatizer(), spacy.load("es_core_news_sm")
    except OSError:
        print("⚠️ Modelo de spaCy no encontrado. Ejecuta:")
        print("   python -m spacy download es_core_news_sm")
        return WordNetLemmatizer(), None

def tokenizar_nltk(texto):

    ## Tokeniza un texto usando NLTK

    try:
        return word_tokenize(texto.lower())
    except Exception as e:
        print(f"Error en tokenización: {e}")
        return []

def lematizar_nltk(texto, lemmatizer):
    
    ## Lematiza un texto usando NLTK
    
    try:
        tokens = word_tokenize(texto.lower())
        return [lemmatizer.lemmatize(token) for token in tokens]
    except Exception as e:
        print(f"Error en lematización NLTK: {e}")
        return []

def lematizar_spacy(texto, pln):
    
    ## Lematiza un texto usando spaCy con información morfológica
    
    try:
        if pln is None:
            return [("Error: spaCy no disponible", "", "")]
        
        doc = pln(texto)
        return [(token.text, token.lemma_, token.pos_) for token in doc]
    except Exception as e:
        print(f"Error en lematización spaCy: {e}")
        return []


# CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA

class ChatNicoGUI:
    """
    Clase principal que maneja la interfaz gráfica de ChatNico
    """
    
    def __init__(self):
        """Inicializar la aplicación"""
        # Variables de estado del chat
        self.saludado = False
        self.esperando_frase = None
        
        # Inicializar modelos de procesamiento
        self.lemmatizer, self.pln = inicializar_modelos()
        
        # Configurar ventana principal
        self.root = tk.Tk()
        self.root.title("🤖 ChatNico - Procesador de Lenguaje Natural")
        self.root.geometry("950x750")
        self.root.minsize(800, 600)
        
        # Definir paleta de colores
        self.colores = {
            'bg_principal': '#f5f5dc',        # Beige claro
            'verde_pastel': '#81c784',        # Verde pastel mejorado
            'verde_oscuro': '#4caf50',        # Verde más vibrante
            'cafe_claro': '#d7ccc8',          # Café claro
            'beige_oscuro': '#e8dcc6',        # Beige más oscuro
            'texto_oscuro': '#3e2723',        # Café muy oscuro
            'blanco': '#ffffff',
            'gris_claro': '#f9f9f9'
        }
        
        # Configurar estilos y crear interfaz
        self.configurar_estilos()
        self.crear_interfaz()
        self.mostrar_mensaje_inicial()
        
        # Configurar el comportamiento al cerrar
        self.root.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
    
    def configurar_estilos(self):
        """Configurar estilos personalizados para ttk"""
        style = ttk.Style()
        
        # Usar un tema base
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Estilo para botones principales
        style.configure('Verde.TButton',
                       background=self.colores['verde_pastel'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       focuscolor='none',
                       borderwidth=1,
                       relief='raised')
        
        # Comportamiento al hacer hover
        style.map('Verde.TButton',
                 background=[('active', self.colores['verde_oscuro']),
                            ('pressed', self.colores['verde_oscuro'])],
                 relief=[('pressed', 'sunken')])
    
    def crear_interfaz(self):
        """Crear todos los componentes de la interfaz"""
        
        # ===== ENCABEZADO =====
        self.crear_encabezado()
        
        # ===== ÁREA PRINCIPAL DE CHAT =====
        self.crear_area_chat()
        
        # ===== ÁREA DE ENTRADA =====
        self.crear_area_entrada()
        
        # ===== BARRA DE ESTADO =====
        self.crear_barra_estado()
    
    def crear_encabezado(self):
        """Crear el encabezado de la aplicación"""
        header_frame = tk.Frame(self.root, bg=self.colores['verde_pastel'], height=90)
        header_frame.pack(fill='x', padx=15, pady=(15,0))
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = tk.Label(
            header_frame,
            text="🤖 ChatNico",
            font=('Segoe UI', 26, 'bold'),
            bg=self.colores['verde_pastel'],
            fg='white'
        )
        title_label.pack(pady=(15,5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Procesamiento de Lenguaje Natural con NLTK y spaCy",
            font=('Segoe UI', 12),
            bg=self.colores['verde_pastel'],
            fg='white'
        )
        subtitle_label.pack(pady=(0,10))
    
    def crear_area_chat(self):
        """Crear el área donde se muestran los mensajes"""
        chat_frame = tk.Frame(self.root, bg=self.colores['bg_principal'])
        chat_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Área de texto con scroll para mostrar conversación
        self.chat_area = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=80,
            height=28,
            font=('Segoe UI', 11),
            bg=self.colores['blanco'],
            fg=self.colores['texto_oscuro'],
            relief='solid',
            borderwidth=1,
            state=tk.DISABLED,
            cursor='arrow',
            selectbackground=self.colores['verde_pastel']
        )
        self.chat_area.pack(fill='both', expand=True, pady=(0,15))
        
        # Configurar estilos para diferentes tipos de mensajes
        self.configurar_estilos_chat()
    
    def crear_area_entrada(self):
        """Crear el área donde el usuario escribe mensajes"""
        input_frame = tk.Frame(self.chat_area.master, bg=self.colores['bg_principal'])
        input_frame.pack(fill='x', pady=(0,15))
        
        # Campo de texto para entrada
        self.entrada = tk.Entry(
            input_frame,
            font=('Segoe UI', 12),
            bg=self.colores['blanco'],
            fg=self.colores['texto_oscuro'],
            relief='solid',
            borderwidth=2,
            insertbackground=self.colores['verde_oscuro']
        )
        self.entrada.pack(side='left', fill='x', expand=True, padx=(0,10), ipady=10)
        
        # Botón para enviar mensaje
        self.btn_enviar = ttk.Button(
            input_frame,
            text="📤 Enviar",
            style='Verde.TButton',
            command=self.enviar_mensaje
        )
        self.btn_enviar.pack(side='right', ipadx=20, ipady=8)
        
        # Permitir enviar con Enter
        self.entrada.bind('<Return>', lambda e: self.enviar_mensaje())
        self.entrada.focus_set()
    
    def crear_barra_estado(self):
        """Crear la barra de estado en la parte inferior"""
        self.status_frame = tk.Frame(self.root, bg=self.colores['verde_pastel'], height=35)
        self.status_frame.pack(fill='x', side='bottom')
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="🟢 ChatNico listo para procesar texto",
            font=('Segoe UI', 10),
            bg=self.colores['verde_pastel'],
            fg='white'
        )
        self.status_label.pack(pady=8)
    
    def configurar_estilos_chat(self):
        """Configurar estilos para los mensajes en el chat"""
        
        # Estilo para mensajes del usuario (lado derecho)
        self.chat_area.tag_configure('user_message',
                                    justify='right',
                                    background=self.colores['verde_pastel'],
                                    foreground='white',
                                    font=('Segoe UI', 11, 'bold'),
                                    rmargin=25,
                                    spacing1=8,
                                    spacing3=8,
                                    relief='raised',
                                    borderwidth=1)
        
        # Estilo para mensajes del bot (lado izquierdo)
        self.chat_area.tag_configure('bot_message',
                                    justify='left',
                                    background=self.colores['beige_oscuro'],
                                    foreground=self.colores['texto_oscuro'],
                                    font=('Segoe UI', 11),
                                    lmargin1=25,
                                    spacing1=8,
                                    spacing3=8,
                                    relief='raised',
                                    borderwidth=1)
        
        # Estilo para mostrar resultados de procesamiento
        self.chat_area.tag_configure('resultado',
                                    background=self.colores['gris_claro'],
                                    foreground=self.colores['texto_oscuro'],
                                    font=('Consolas', 10),
                                    lmargin1=40,
                                    lmargin2=40,
                                    spacing1=5,
                                    relief='groove',
                                    borderwidth=1)
        
        # Estilo para títulos de resultados
        self.chat_area.tag_configure('titulo_resultado',
                                    font=('Segoe UI', 11, 'bold'),
                                    foreground=self.colores['verde_oscuro'])
    
    def agregar_mensaje(self, mensaje, tipo='bot', resultados=None):
        """
        Agregar un mensaje al área de chat
        Args:
            mensaje (str): Mensaje a mostrar
            tipo (str): 'user' o 'bot'
            resultados (list): Lista de resultados a mostrar
        """
        self.chat_area.config(state=tk.NORMAL)
        
        # Agregar timestamp
        timestamp = time.strftime("%H:%M")
        
        if tipo == 'user':
            # Mensaje del usuario
            self.chat_area.insert(tk.END, f"[{timestamp}] Tú: {mensaje}\n", 'user_message')
        else:
            # Mensaje del bot
            self.chat_area.insert(tk.END, f"[{timestamp}] 🤖 ChatNico: {mensaje}\n", 'bot_message')
            
            # Si hay resultados, mostrarlos
            if resultados:
                self.chat_area.insert(tk.END, "\n📊 Resultados del procesamiento:\n", 'titulo_resultado')
                for i, resultado in enumerate(resultados, 1):
                    self.chat_area.insert(tk.END, f"   {i:2d}. {resultado}\n", 'resultado')
        
        # Agregar separación entre mensajes
        self.chat_area.insert(tk.END, "\n")
        self.chat_area.config(state=tk.DISABLED)
        
        # Hacer scroll hacia abajo
        self.chat_area.see(tk.END)
    
    def mostrar_mensaje_inicial(self):
        """Mostrar el mensaje de bienvenida"""
        mensaje = """¡Bienvenido a ChatNico! 👋

Soy tu asistente para procesamiento de lenguaje natural. Para comenzar, salúdame primero.

Después podrás usar estos comandos:
• 'tokeniza con nltk' - Separar texto en tokens individuales
• 'lematiza con nltk' - Encontrar la raíz de las palabras (NLTK)
• 'lematiza con spacy' - Análisis morfológico completo (spaCy)

Escribe 'salir', 'adiós' o 'chao' cuando quieras terminar."""
        
        self.agregar_mensaje(mensaje)
    
    def actualizar_status(self, texto):
        """Actualizar el mensaje en la barra de estado"""
        self.status_label.config(text=texto)
        self.root.update_idletasks()
    
    def enviar_mensaje(self):
        """Procesar el envío de un mensaje"""
        mensaje = self.entrada.get().strip()
        
        # Validar que hay contenido
        if not mensaje:
            return
        
        # Limpiar el campo de entrada
        self.entrada.delete(0, tk.END)
        
        # Mostrar el mensaje del usuario
        self.agregar_mensaje(mensaje, 'user')
        
        # Procesar el mensaje en un hilo separado para no bloquear la UI
        thread = threading.Thread(target=self.procesar_mensaje, args=(mensaje.lower(),))
        thread.daemon = True
        thread.start()
    
    def procesar_mensaje(self, mensaje):
        """
        Procesar el mensaje del usuario y generar respuesta
        Args:
            mensaje (str): Mensaje del usuario en minúsculas
        """
        
        # Mostrar que estamos procesando
        self.actualizar_status("🔄 ChatNico está procesando...")
        time.sleep(0.8)  # Simular tiempo de procesamiento
        
        # Comandos para salir
        comandos_salir = ["salir", "adiós", "adios", "chao", "exit", "quit", "bye"]
        if any(cmd in mensaje for cmd in comandos_salir):
            self.agregar_mensaje("¡Hasta luego! 👋 Gracias por usar ChatNico. La aplicación se cerrará en 3 segundos.")
            self.actualizar_status("❌ Cerrando aplicación...")
            self.root.after(3000, self.cerrar_aplicacion)
            return
        
        # Si estamos esperando una frase para procesar
        if self.esperando_frase:
            self.procesar_texto_usuario(mensaje)
            return
        
        # Verificar si ya saludó
        if not self.saludado:
            saludos = ["hola", "buenas", "qué tal", "que tal", "hey", "buenos días", "buenos dias", 
                      "buenas tardes", "buenas noches", "saludos"]
            
            if any(saludo in mensaje for saludo in saludos):
                self.agregar_mensaje("¡Hola! ¿Cómo estás? 😊 Ahora ya puedes usar mis funciones de procesamiento de texto.")
                self.saludado = True
            else:
                self.agregar_mensaje("¡Hey! Primero salúdame y después podremos trabajar juntos. 😊")
            
            self.actualizar_status("🟢 ChatNico listo para procesar texto")
            return
        
        # Detectar qué tipo de procesamiento quiere el usuario
        if "tokeniza con nltk" in mensaje or "tokenizar nltk" in mensaje:
            self.esperando_frase = 'tokenize_nltk'
            self.agregar_mensaje("Perfecto! 🔤 Dame la oración o texto que quieres tokenizar:")
            
        elif "lematiza con nltk" in mensaje or "lematizar nltk" in mensaje:
            self.esperando_frase = 'lemmatize_nltk'
            self.agregar_mensaje("Excelente! 🌿 Dame la oración que quieres lematizar usando NLTK:")
            
        elif "lematiza con spacy" in mensaje or "lematizar spacy" in mensaje:
            if self.pln is None:
                self.agregar_mensaje("❌ Lo siento, spaCy no está disponible. Instala el modelo con:\npython -m spacy download es_core_news_sm")
            else:
                self.esperando_frase = 'lemmatize_spacy'
                self.agregar_mensaje("Genial! 🔬 Dame la oración para análisis morfológico con spaCy:")
                
        else:
            # Mensaje de ayuda
            ayuda = """No entendí tu solicitud. 🤔 
            
Los comandos disponibles son:
• 'tokeniza con nltk' - Para separar texto en tokens
• 'lematiza con nltk' - Para lematización básica  
• 'lematiza con spacy' - Para análisis morfológico completo

¿Cuál te gustaría probar?"""
            self.agregar_mensaje(ayuda)
        
        self.actualizar_status("🟢 ChatNico listo para procesar texto")
    
    def procesar_texto_usuario(self, texto):
        """
        Procesar el texto que el usuario quiere analizar
        Args:
            texto (str): Texto a procesar
        """
        
        self.actualizar_status("⚙️ Procesando texto...")
        time.sleep(1.2)  # Simular procesamiento
        
        try:
            if self.esperando_frase == 'tokenize_nltk':
                # Tokenización con NLTK
                tokens = tokenizar_nltk(texto)
                if tokens:
                    resultados = [f"{token:15} (posición {i+1})" for i, token in enumerate(tokens)]
                    self.agregar_mensaje(
                        f"✅ Tokenización completada para: '{texto}'",
                        resultados=resultados
                    )
                else:
                    self.agregar_mensaje("❌ No se pudieron obtener tokens del texto.")
                    
            elif self.esperando_frase == 'lemmatize_nltk':
                # Lematización con NLTK
                lemas = lematizar_nltk(texto, self.lemmatizer)
                if lemas:
                    resultados = [f"{lema:15} (forma base)" for lema in lemas]
                    self.agregar_mensaje(
                        f"✅ Lematización NLTK completada para: '{texto}'",
                        resultados=resultados
                    )
                else:
                    self.agregar_mensaje("❌ No se pudieron obtener lemas del texto.")
                    
            elif self.esperando_frase == 'lemmatize_spacy':
                # Lematización con spaCy
                analisis = lematizar_spacy(texto, self.pln)
                if analisis and analisis[0][0] != "Error: spaCy no disponible":
                    resultados = [f"{palabra:12} → {lema:12} [{pos}]" 
                                for palabra, lema, pos in analisis]
                    self.agregar_mensaje(
                        f"✅ Análisis morfológico spaCy completado para: '{texto}'",
                        resultados=resultados
                    )
                else:
                    self.agregar_mensaje("❌ Error en el análisis con spaCy.")
        
        except Exception as e:
            self.agregar_mensaje(f"❌ Error inesperado: {str(e)}")
            print(f"Error en procesamiento: {e}")  # Para debug
        
        # Resetear estado
        self.esperando_frase = None
        self.actualizar_status("🟢 ChatNico listo para procesar texto")
    
    def cerrar_aplicacion(self):
        """Cerrar la aplicación de forma segura"""
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
    
    def iniciar(self):
        """Iniciar la aplicación GUI"""
        try:
            print("🚀 Iniciando ChatNico...")
            
            # Verificar que los modelos se cargaron correctamente
            if self.lemmatizer is None:
                messagebox.showwarning("Advertencia", 
                                     "NLTK no está completamente configurado.\nAlgunas funciones podrían no funcionar.")
            
            if self.pln is None:
                messagebox.showinfo("Información", 
                                  "spaCy no está disponible.\nSolo funcionará NLTK.\n\nPara habilitar spaCy:\npython -m spacy download es_core_news_sm")
            
            # Iniciar el loop principal
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\n👋 Cerrando ChatNico...")
            self.cerrar_aplicacion()
        except Exception as e:
            print(f"❌ Error crítico: {e}")
            messagebox.showerror("Error", f"Error crítico en la aplicación:\n{str(e)}")

# ============================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================
def main():
    """Función principal para ejecutar ChatNico"""
    print("=" * 50)
    print("🤖 ChatNico - Procesador de Lenguaje Natural")
    print("=" * 50)
    
    try:
        # Crear e iniciar la aplicación
        app = ChatNicoGUI()
        app.iniciar()
        
    except Exception as e:
        print(f"❌ Error al inicializar la aplicación: {e}")
        input("Presiona Enter para salir...")

# Ejecutar solo si es el archivo principal
if __name__ == "__main__":
    main()