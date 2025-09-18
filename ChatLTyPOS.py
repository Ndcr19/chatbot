import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
from golf_assistant import GolfAssistant

# ============================================
# CLASE PRINCIPAL DE LA INTERFAZ GRÁFICA
# ============================================

class ChatNicoGUI:
    """
    Clase principal que maneja la interfaz gráfica del Asistente de Golf
    """
    
    def __init__(self):
        """Inicializar la aplicación"""
        # Variables de estado del chat
        self.saludado = False
        
        # Inicializar el asistente de golf
        self.assistant = GolfAssistant()
        
        # Configurar ventana principal
        self.root = tk.Tk()
        self.root.title("🏌️ Asistente de Golf para Principiantes")
        self.root.geometry("950x750")
        self.root.minsize(800, 600)
        
        # Definir paleta de colores
        self.colores = {
            'bg_principal': '#e8f5e9',        # Verde muy claro
            'verde_pastel': '#81c800',        # Verde pastel mejorado
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
            text=" <:-)> ChatNico <:-)> ",
            font=('Segoe UI', 26, 'bold'),
            bg=self.colores['verde_pastel'],
            fg='white'
        )
        title_label.pack(pady=(15,5))
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="________________________________",
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
        """Mostrar el mensaje de bienvenida del asistente de golf"""
        mensaje = """🏌️‍♂️ ¡Bienvenido a tu Asistente de Golf Personal! ⛳

Estoy aquí para ayudarte a elegir el palo adecuado para tu siguiente golpe. 

Puedes contarme tu situación de juego de forma natural, por ejemplo:
• "Estoy a 150 yardas en el fairway"
• "Tengo 90 yardas hasta el green con viento en contra"
• "Estoy en el rough a 120 yardas"
• "Estoy en el bunker a 60 yardas"
• "El green está más alto que mi posición actual"

¡Simplemente salúdame para comenzar! 😊"""
        
        self.agregar_mensaje(mensaje, 'sistema')
    
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
        Procesar el mensaje del usuario y generar una recomendación de golf
        Args:
            mensaje (str): Mensaje del usuario
        """
        # Actualizar estado
        self.actualizar_status("⛳ Analizando tu situación de juego...")
        
        try:
            # Comandos de salida
            saludos_despedida = ['salir', 'adiós', 'adios', 'chao', 'hasta luego', 'gracias', 'bye']
            if any(saludo in mensaje.lower() for saludo in saludos_despedida):
                self.agregar_mensaje("¡Hasta luego! Que tengas un excelente juego. ¡Swing fácil! 🏌️‍♂️")
                if 'salir' in mensaje.lower() or 'chao' in mensaje.lower() or 'bye' in mensaje.lower():
                    self.root.after(1000, self.cerrar_aplicacion)
                return
                
            # Si es un saludo inicial
            if not self.saludado:
                if any(palabra in mensaje.lower() for palabra in ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'hey', 'holi']):
                    self.saludado = True
                    self.agregar_mensaje("¡Hola! Soy tu asistente de golf personal. Estoy aquí para ayudarte a elegir el palo adecuado para tu siguiente golpe.\n\nPuedes decirme cosas como:\n• 'Estoy a 150 yardas del hoyo en el fairway'\n• 'Tengo 90 yardas hasta el green con viento en contra'\n• 'Estoy en el rough a 120 yardas'")
                else:
                    self.agregar_mensaje("¡Hola! Soy tu asistente de golf. Por favor, saludame y cuentame que necesitas. 😊")
                return
                
            # Procesar la entrada con el asistente de golf
            respuesta = self.assistant.process_input(mensaje)
            self.agregar_mensaje(respuesta)
                
        except Exception as e:
            self.agregar_mensaje(f"❌ Lo siento, hubo un error al procesar tu consulta. Asegúrate de incluir la distancia y el terreno.\n\nEjemplo: 'Estoy a 150 yardas en el fairway'")
            print(f"Error: {str(e)}")
            
        finally:
            self.actualizar_status("🟢 Listo para ayudarte")
    
    def procesar_texto_usuario(self, texto):
        """
        Procesar la entrada del usuario para recomendaciones de golf
        Args:
            texto (str): Texto a procesar
        """
        self.actualizar_status("⛳ Analizando tu situación de juego...")
        time.sleep(0.5)  # Pequeña pausa para feedback visual
        
        try:
            # Procesar la entrada con el asistente de golf
            respuesta = self.assistant.process_input(texto)
            self.agregar_mensaje(respuesta)
        
        except Exception as e:
            self.agregar_mensaje(f"❌ Error inesperado: {str(e)}")
            print(f"Error en procesamiento: {e}")  # Para debug
        
        # Resetear estado
        self.esperando_frase = None
        self.actualizar_status("🟢 Asistente de Golf listo para ayudarte")
    
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
            print("🚀 Iniciando Asistente de Golf...")
            print("✅ Interfaz gráfica lista")
            print("\n🟢 ¡El Asistente de Golf está listo para ayudarte!")
            print("   Escribe 'salir' para terminar el programa.\n")
            
            # Iniciar el bucle principal
            self.root.mainloop()
            
        except Exception as e:
            print(f"❌ Error crítico: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")
        finally:
            print("\n👋 ¡Hasta luego! Que tengas un excelente juego. ⛳")
            if hasattr(self, 'root'):
                self.root.destroy()

# ============================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================
def main():
    """Función principal para ejecutar Asistente de Golf"""
    print("=" * 50)
    print("🏌️  Asistente de Golf para Principiantes")
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