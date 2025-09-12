class GolfAssistant:
    def __init__(self):
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

    def extract_distance(self, text):
        # Extraer la distancia del texto (como alguna de estas : "Estoy a 150 yardas" -> 150)
        import re
        match = re.search(r'(\d+)\s*(?:yardas|metros|mts?|y)', text, re.IGNORECASE)
        return int(match.group(1)) if match else None

    def extract_terrain(self, text):
        # Detectar el tipo de terreno
        text = text.lower()
        if "fairway" in text or "calle" in text:
            return "fairway"
        elif "rough" in text or "hierba" in text or "hierba alta" in text:
            return "rough"
        elif "bunker" in text or "arena" in text:
            return "bunker"
        elif "tee" in text or "salida" in text:
            return "tee"
        elif "green" in text:
            return "green"
        return "desconocido"

    def extract_elevation(self, text):
        # Detectar elevación
        text = text.lower()
        if "subid" in text or "más alto" in text or "arriba" in text:
            return "subida"
        elif "bajad" in text or "más bajo" in text or "abajo" in text:
            return "bajada"
        return "plano"

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

    def process_input(self, text):
        # Procesar la entrada del usuario y generar una recomendación
        distance = self.extract_distance(text)
        if distance is None:
            return "Por favor, indícame la distancia al hoyo (por ejemplo, 'Estoy a 150 yardas')."

        terrain = self.extract_terrain(text)
        elevation = self.extract_elevation(text)

        club, reason = self.recommend_club(distance, terrain, elevation)
        return f"Recomendación: {club}\n\nRazón: {reason}"
