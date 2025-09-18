import spacy
import re

class GolfAssistant:
    def __init__(self):
        # Cargar el modelo de español de Spacy
        try:
            self.nlp = spacy.load("es_core_news_sm")
        except OSError:
            # Si el modelo no está instalado, intentar instalarlo
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
            self.nlp = spacy.load("es_core_news_sm")
            
        # Definir rangos de distancia para cada palo (en yardas)
        self.club_ranges = {
            "Driver": (200, 280),
            "Madera 3": (180, 230),
            "Madera 5": (170, 220),
            "Hierro 3": (160, 210),
            "Hierro 4": (150, 200),
            "Hierro 5": (140, 180),
            "Hierro 6": (130, 170),
            "Hierro 7": (120, 160),
            "Hierro 8": (110, 150),
            "Hierro 9": (100, 140),
            "Pitching Wedge (PW)": (80, 120),
            "Sand Wedge (SW)": (60, 100),
            "Lob Wedge (LW)": (40, 80),
            "Putter": (0, 40)
        }
        
        # Diccionario de sinónimos para términos de golf
        self.terrain_synonyms = {
            "fairway": ["fairway", "calle", "callejón", "pista"],
            "rough": ["rough", "hierba", "maleza", "pasto", "césped alto"],
            "bunker": ["bunker", "trampa de arena", "arena", "arenero", "trampa"],
            "tee": ["tee", "salida", "punto de salida", "lanzamiento"],
            "green": ["green", "verde", "copa", "bandera", "hoyo"]
        }
        
        self.elevation_terms = {
            "subida": ["subir", "ascender", "arriba", "elevado", "cuesta arriba"],
            "bajada": ["bajar", "descender", "abajo", "hacia abajo", "cuesta abajo"],
            "plano": ["plano", "nivel", "igualado", "llano"]
        }

    def extract_distance(self, text):
        """
        Extrae la distancia del texto usando Spacy para mejor reconocimiento.
        Ejemplos:
        - "Estoy a 150 yardas" -> 150
        - "Quedan como doscientos metros" -> 200
        - "Aproximadamente 100m" -> 100
        """
        doc = self.nlp(text.lower())
        
        # Buscar números en el texto
        for token in doc:
            if token.like_num and token.i + 1 < len(doc):
                # Verificar si el token siguiente es una unidad de medida
                next_token = doc[token.i + 1]
                if any(unit in next_token.text for unit in ["yardas", "metros", "mts", "m", "y"]):
                    try:
                        # Convertir texto a número (maneja tanto dígitos como palabras)
                        if token.is_digit:
                            return int(token.text)
                        else:
                            # Para números escritos con palabras
                            return w2n.word_to_num(token.text)
                    except (ValueError, AttributeError):
                        continue
        
        # Si no se encontró con el método anterior, intentar con expresión regular
        match = re.search(r'(\d+)\s*(?:yardas|metros|mts?|y)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def extract_terrain(self, text):
        """
        Detecta el tipo de terreno usando Spacy para lematización y
        reconocimiento de sinónimos.
        """
        doc = self.nlp(text.lower())
        lemmas = [token.lemma_ for token in doc]
        
        # Buscar coincidencias con los términos de terreno
        for terrain, synonyms in self.terrain_synonyms.items():
            # Verificar si algún sinónimo está en los lemas
            if any(synonym in ' '.join(lemmas) for synonym in synonyms):
                return terrain
                
        # Si no se encontró, intentar con bigramas (combinaciones de dos palabras)
        bigrams = [' '.join(lemmas[i:i+2]) for i in range(len(lemmas)-1)]
        for terrain, synonyms in self.terrain_synonyms.items():
            if any(synonym in bigrams for synonym in synonyms):
                return terrain
                
        return "desconocido"

    def extract_elevation(self, text):
        """
        Detecta la elevación usando Spacy para un mejor reconocimiento de términos.
        Considera sinónimos y expresiones relacionadas con la elevación.
        """
        doc = self.nlp(text.lower())
        lemmas = [token.lemma_ for token in doc]
        
        # Buscar términos de elevación
        for elevation, terms in self.elevation_terms.items():
            # Verificar términos individuales
            if any(term in lemmas for term in terms):
                return elevation
                
            # Verificar bigramas para expresiones compuestas
            bigrams = [' '.join(lemmas[i:i+2]) for i in range(len(lemmas)-1)]
            if any(term in bigrams for term in terms):
                return elevation
        
        # Análisis de dependencias para frases como "está cuesta arriba"
        for token in doc:
            if token.dep_ == "advmod" and token.head.lemma_ in ["estar", "encontrar", "estar"]:
                if any(term in token.lemma_ for terms in self.elevation_terms.values() for term in terms):
                    for elevation, terms in self.elevation_terms.items():
                        if any(term in token.lemma_ for term in terms):
                            return elevation
        
        return "plano"  # Por defecto, asumir terreno plano

    def recommend_club(self, distance, terrain, elevation):
        # Ajustar distancia según la elevación
        if elevation == "subida":
            distance *= 1.1  # Aumentar distancia en un 10% para subidas
        elif elevation == "bajada":
            distance *= 0.9  # Reducir distancia en un 10% para bajadas

        # Recomendar palo basado en la distancia
        for club, (min_dist, max_dist) in self.club_ranges.items():
            if min_dist <= distance <= max_dist:
                # Ajustar recomendación según el terreno
                if terrain == "bunker" and "Wedge" not in club:
                    return "Sand Wedge (SW)", "Recomiendo el Sand Wedge para salir del bunker con facilidad."
                elif terrain == "rough" and distance > 150:
                    return "Hierro 5", "Un hierro 5 es una buena opción para salir del rough con distancia."
                elif terrain == "green" and distance <= 40:
                    return "Putter", "Usa el putter para rodar la pelota hacia el hoyo."
                elif terrain == "tee" and distance >= 200:
                    return "Driver", "El driver es ideal para el tee de salida en distancias largas."
                elif terrain == "fairway":
                    return club, f"El {club} es adecuado para esta distancia desde el fairway."
                else:
                    return club, f"Puedes usar el {club} para esta distancia."

        return "No se pudo determinar", "Lo siento, no pude determinar una recomendación adecuada."

    def is_golf_related(self, text):
        """
        Verifica si el texto está relacionado con golf.
        Devuelve True si es sobre golf, False si no lo es.
        """
        doc = self.nlp(text.lower())
        lemmas = [token.lemma_ for token in doc]
        
        # Términos relacionados con golf
        golf_terms = [
            'golf', 'hoyo', 'green', 'fairway', 'rough', 'bunker', 'tee', 'bandera',
            'palo', 'hierro', 'driver', 'putter', 'wedg', 'madera', 'hoyo', 'campo',
            'cancha', 'golfista', 'golfístico', 'golfístico', 'golfear', 'golfista'
        ]
        
        # Verificar si hay términos de golf en el texto
        if any(term in ' '.join(lemmas) for term in golf_terms):
            return True
            
        # Verificar si hay términos de compra o venta
        commerce_terms = [
            'comprar', 'vender', 'precio', 'costo', 'valor', 'pesos', 'dólar', 'euro',
            'compra', 'venta', 'tienda', 'comercio', 'factura', 'pagar', 'pago', 'dinero'
        ]
        
        if any(term in ' '.join(lemmas) for term in commerce_terms):
            return False
            
        # Si no es claramente de compra ni de golf, asumir que es de golf
        # para mantener la funcionalidad principal
        return True

    def process_input(self, text):
        """
        Procesa la entrada del usuario y genera una recomendación de palo de golf.
        Si el mensaje no está relacionado con golf, devuelve un mensaje apropiado.
        """
        # Primero verificar si el mensaje está relacionado con golf
        if not self.is_golf_related(text):
            return "Lo siento, solo puedo ayudarte con recomendaciones de golf. " \
                  "Puedes preguntarme sobre qué palo usar en cierta distancia o situación en el campo de golf."
        
        # Si es sobre golf, proceder con el procesamiento normal
        distance = self.extract_distance(text)
        if distance is None:
            return "Por favor, indícame la distancia al hoyo (por ejemplo, 'Estoy a 150 yardas')."

        terrain = self.extract_terrain(text)
        elevation = self.extract_elevation(text)

        club, reason = self.recommend_club(distance, terrain, elevation)
        return f"Recomendación: {club}\n\nRazón: {reason}"
