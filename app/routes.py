from flask import Blueprint, request, jsonify
from .scheduler import algoritmo_genetico

import re

# Función para convertir camelCase a snake_case
def camel_to_snake(camel_str):
    # Convierte la cadena camelCase a snake_case
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', camel_str).lower()

def snake_to_camel(snake_str):
    components = snake_str.split('_')
    # El primer componente lo dejamos en minúsculas, y los demás los ponemos con la primera letra en mayúsculas
    return components[0] + ''.join(x.title() for x in components[1:])

def convert_keys_to_camel_case(d):
    if isinstance(d, dict):
        return {snake_to_camel(k): convert_keys_to_camel_case(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_camel_case(item) for item in d]
    else:
        return d
    

# Función para convertir todas las claves de un diccionario de camelCase a snake_case
def convert_keys_to_snake_case(d):
    if isinstance(d, dict):
        return {camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [convert_keys_to_snake_case(item) for item in d]
    else:
        return d

api = Blueprint('api', __name__)
@api.route('/generate-schedule', methods=['POST'])
def generar_horario():
    # Obtener los datos JSON enviados en la solicitud POST
    data = request.get_json()

    # Convertir las claves de camelCase a snake_case
    data = convert_keys_to_snake_case(data)

    # Obtener las asignaciones y preferencias del JSON convertido
    assignments = data.get("assignments", [])
    preferences = data.get("preferences", {})

    # Llamar a la función de algoritmo genético con los datos convertidos
    resultado = algoritmo_genetico(assignments, preferences)

    # Convertir las claves del resultado de snake_case a camelCase
    resultado = convert_keys_to_camel_case(resultado)

    print("Resultado:", resultado)
    return jsonify(resultado)

@api.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World"})