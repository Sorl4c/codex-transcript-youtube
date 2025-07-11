#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo para procesar transcripciones de texto y generar resúmenes.

Este script tiene un doble propósito:
1. Como herramienta de línea de comandos (CLI) para analizar un archivo de texto
   o una entrada manual y generar un resumen utilizando un LLM local.
2. Como módulo importable que proporciona la función `process_transcript` para
   ser utilizada por otras partes de la aplicación (ej. la GUI de Streamlit),
   permitiendo el uso de diferentes backends de IA como Gemini.
"""

import argparse
import sys
import requests
from pathlib import Path
import os
from ia.gemini_api import summarize_text_gemini

# Configuración para la API local (WSL2)
API_URL = "http://172.31.126.236:8000/v1/chat/completions"
MODEL_NAME = "local-model"  # Cambia esto si tu backend usa otro nombre
MODEL_PATH = "/mnt/c/local/modelos/qwen2-7b-instruct-q6_k.gguf"  # Opcional, solo informativo

PROMPT = """
Tu tarea:
Eres un analista experto que lee una transcripción completa y produce un resumen claro, concreto y libre de marketing. Sigue estos pasos internos antes de responder:

────────────────────────────────────────────────────────────────────
## ASSISTANT SCRATCHPAD (razona aquí, NO lo incluyas en la respuesta)

1. LEE todo el texto y detecta:
   – Ideas clave (tesis, conclusiones, datos numéricos).
   – Frases de “marketing”/CTAs (descartarlas).
   – Ejemplos o anécdotas secundarias (marcarlas como paja).
2. AGRUPA capítulos similares; fusiónalos si comparten >50% de contenido.
3. PRIORIZA:
   a) Datos prácticos (series, reps, frecuencia).  
   b) Principios explicativos.  
   c) Ejemplos solo si aportan valor.
4. ESCRIBE **TL;DR** (≤ 35 palabras) con la idea central y beneficio.
5. CREA **Recomendaciones rápidas**:
   – Siempre 3–4 bullets.
   – Cada bullet ≤ 15 palabras.
   – Incluir datos numéricos (p.ej. “12 series/semana”).
6. HAZ **Chapters**:
   – Entre 4 y 7 entradas; fusiona solapamientos.
   – Cada entrada: **Título (≤ 5 palabras)** + descripción (≤ 20 palabras).
   – Asegúrate de incluir, si el texto lo menciona:  
     • Programación/Volumen  
     • Práctica deliberada  
7. VERIFICA:
   – Longitud total ≤ 250 palabras.
   – Cero CTAs o marketing.
   – Sin repeticiones literales.
8. ENTREGA solo estas secciones, sin exponer tu razonamiento.

────────────────────────────────────────────────────────────────────
## FORMATO DE RESPUESTA

**TL;DR**  
…

**Recomendaciones rápidas**  
– …  
– …  
– …  

**Chapters**  
1. Título – descripción breve.  
2. …  
3. …  
4. …  
5. …  

────────────────────────────────────────────────────────────────────
TEXTO A ANALIZAR:  
{transcripcion}
"""





def input_multiline(prompt="Pega la transcripción (presiona Enter dos veces para finalizar):"):
    """Captura texto multilínea desde la entrada estándar del usuario.

    Utilizado por la interfaz de línea de comandos (CLI) para permitir pegar
    texto directamente en la terminal.

    Args:
        prompt (str): El mensaje a mostrar al usuario.

    Returns:
        str: El texto completo introducido por el usuario.
    """
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                if lines:  # Permite salir con doble Enter
                    break
                continue
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def process_transcript(transcripcion: str, temperature: float = 0.3, max_tokens: int = 2048, pipeline_type: str = 'native') -> tuple:
    """Procesa una transcripción utilizando un pipeline de IA específico.

    Orquesta el proceso de enviar una transcripción a un backend de IA
    (un LLM local o la API de Gemini) y devuelve el resultado estructurado.

    Args:
        transcripcion (str): El texto completo de la transcripción a analizar.
        temperature (float): La temperatura para la generación del modelo.
        max_tokens (int): El número máximo de tokens para la respuesta.
        pipeline_type (str): El backend a utilizar ('native' para local, 'gemini' para la API de Google).

    Returns:
        tuple: El contenido de la tupla depende del `pipeline_type`:
            - Si es 'gemini': (summary_text, key_ideas_text, suggested_title)
            - Si es 'native': (texto_del_resumen, prompt_completo, payload_enviado)
    """
    if pipeline_type == 'gemini':
        print("[INFO] Usando el pipeline de Gemini API.")
        # Para Gemini, usamos un prompt más directo y general.
        prompt_template = """
Tu tarea:
Escribe un resumen claro y conciso del siguiente texto. Estructura la respuesta con las siguientes secciones:
- **TL;DR**: Un resumen muy corto (1-2 frases).
- **Recomendaciones rápidas**: Una lista de 3-4 puntos clave o acciones.
- **Capítulos**: Un desglose de 4-7 temas principales tratados en el texto.

TEXTO A ANALIZAR:
{text}
"""
        try:
            result_dict = summarize_text_gemini(
                text_content=transcripcion,
                prompt_template=prompt_template
            )
            summary_text = result_dict.get("summary_text", "[Error al generar resumen con Gemini]")
            # Para compatibilidad de retorno, creamos un 'payload' y 'prompt_text' simulados
            prompt_text_display = prompt_template.format(text=transcripcion[:500] + "...")
            return summary_text, prompt_text_display, result_dict
        except Exception as e:
            print(f"[ERROR] Falla catastrófica en el pipeline de Gemini: {e}")
            return f"Error en pipeline Gemini: {e}", "", {}

    # --- Pipeline nativo (default) ---
    print("[INFO] Usando el pipeline nativo (microservicio local).")
    prompt_text = PROMPT.format(transcripcion=transcripcion)
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Eres un asistente experto en resumir videos y estructurar contenido en español."},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": max(0.1, min(1.0, temperature)),
        "max_tokens": max(100, min(4096, max_tokens)),
        "stream": False
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        response.raise_for_status()
        summary = response.json()["choices"][0]["message"]["content"]
        print(f"[DEBUG] Resumen recibido de la API. Longitud: {len(summary)} caracteres")
        return summary, prompt_text, payload
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error en la solicitud a la API LLM: {e}")
        return f"Error de conexión con el servicio LLM local: {e}", prompt_text, payload
    except (KeyError, IndexError) as e:
        print(f"❌ Error en la respuesta de la API: {e}", file=sys.stderr)
        return f"Respuesta inesperada de la API local: {e}", prompt_text, payload

def print_config_summary(args, prompt_text, payload):
    """Imprime un resumen de la configuración utilizada en el modo CLI.

    Muestra los parámetros de la ejecución (modelo, temperatura, etc.) y una
    vista previa del prompt enviado al modelo para facilitar la depuración.

    Args:
        args: Los argumentos parseados de la línea de comandos.
        prompt_text (str): El prompt completo que se envió al modelo.
        payload (dict): El diccionario de datos enviado en la petición a la API.
    """
    print("\n" + "="*70)
    print("    RESUMEN DE PARÁMETROS Y PROMPT DEL MODELO")
    print("="*70)
    print(f"API_URL        : {API_URL}")
    print(f"MODEL_NAME     : {payload['model']}")
    print(f"MODEL_PATH     : {MODEL_PATH}")
    print(f"TEMPERATURE    : {payload['temperature']}")
    print(f"MAX_TOKENS     : {payload['max_tokens']}")
    print(f"CTX_SIZE       : 10000 (definido en config, cambia según modelo)")
    print("-"*70)
    print("PROMPT ENVIADO:")
    prompt_preview = prompt_text if len(prompt_text) < 1500 else prompt_text[:1400] + "\n[...truncado]\n"
    print(prompt_preview)
    print("-"*70 + "\n")

def main():
    """Punto de entrada para la ejecución del script desde la línea de comandos.

    Parsea los argumentos, lee la transcripción desde un archivo o la entrada
    estándar, llama a la función de procesamiento y gestiona la salida del
    resultado (imprimiendo en consola o guardando en un archivo).
    """
    parser = argparse.ArgumentParser(
        description='Procesa transcripciones con un modelo LLM local',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-i', '--input', type=str, help='Archivo de entrada con la transcripción (opcional)')
    parser.add_argument('-o', '--output', type=str, help='Archivo de salida (opcional)')
    parser.add_argument('--temperature', type=float, default=0.3, help='Temperatura para la generación (0.1-1.0)')
    parser.add_argument('--max-tokens', type=int, default=2048, help='Número máximo de tokens a generar (100-4096)')

    args = parser.parse_args()

    # Validar parámetros
    if args.temperature < 0.1 or args.temperature > 1.0:
        print("❌ Error: La temperatura debe estar entre 0.1 y 1.0", file=sys.stderr)
        sys.exit(1)
    if args.max_tokens < 100 or args.max_tokens > 4096:
        print("❌ Error: max-tokens debe estar entre 100 y 4096", file=sys.stderr)
        sys.exit(1)

    # Leer la transcripción
    if args.input:
        try:
            input_path = Path(args.input)
            if not input_path.exists():
                print(f"❌ El archivo de entrada no existe: {args.input}", file=sys.stderr)
                sys.exit(1)
            with input_path.open('r', encoding='utf-8') as f:
                transcripcion = f.read()
            if not transcripcion.strip():
                print("❌ El archivo de entrada está vacío", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error al leer el archivo de entrada: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\n" + "="*50)
        print("  RESUMEN DE TRANSCRIPCIÓN CON LLM LOCAL")
        print("="*50 + "\n")
        transcripcion = input_multiline()
        if not transcripcion.strip():
            print("❌ No se proporcionó ninguna transcripción", file=sys.stderr)
            sys.exit(1)

    print("\n🔄 Procesando la transcripción... (esto puede tomar unos momentos)\n")

    try:
        resultado, prompt_text, payload = process_transcript(
            transcripcion,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )
        # Imprime el resumen de configuración y prompt
        print_config_summary(args, prompt_text, payload)

        # Mostrar y/o guardar el resultado
        if args.output:
            try:
                output_path = Path(args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with output_path.open('w', encoding='utf-8') as f:
                    f.write(resultado)
                print(f"✅ Resultado guardado en: {output_path.absolute()}")
                # Vista previa
                print("\n--- VISTA PREVIA ---")
                print("\n".join(resultado.split("\n")[:10]))
                if len(resultado.split("\n")) > 10:
                    print("... (más en el archivo)")
                print("-" * 20)
            except Exception as e:
                print(f"❌ Error al guardar el archivo: {e}", file=sys.stderr)
                print("\n--- RESULTADO ---")
                print(resultado)
                print("-----------------")
        else:
            print("\n" + "="*50)
            print("  RESULTADO DEL ANÁLISIS")
            print("="*50 + "\n")
            print(resultado)
            print("\n" + "="*50 + "\n")
    except KeyboardInterrupt:
        print("\n🛑 Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error al procesar la transcripción: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
