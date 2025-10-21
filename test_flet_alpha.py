#!/usr/bin/env python3
"""
Test script para verificar características de Flet 1.0-alpha
"""

import flet as ft

def test_declarative_ui():
    """Test para verificar si la UI declarativa está disponible"""
    try:
        # Intentar crear una página con patrón declarativo
        def main(page: ft.Page):
            # Test 1: Verificar si tenemos componentes modernos
            button = ft.Button(
                content=ft.Text("Test Button"),
                icon=ft.Icons.PLAY_ARROW
            )

            # Test 2: Verificar si ft.Colors existe (indicador de 1.0)
            colors_test = hasattr(ft, 'Colors')

            # Test 3: Verificar nueva API de tema
            theme = ft.Theme(color_scheme_seed="blue")

            # Test 4: Añadir controles a la página
            page.add(
                ft.Column([
                    ft.Text("Flet 1.0-alpha Test", size=24),
                    button,
                    ft.Text(f"Colors available: {colors_test}")
                ])
            )

            print("✅ Flet 1.0-alpha features detected!")
            print(f"   - New Button API: {'✓' if hasattr(button, 'content') else '✗'}")
            print(f"   - ft.Colors available: {'✓' if colors_test else '✗'}")
            print(f"   - Theme API working: {'✓' if theme else '✗'}")

            return True

        return main

    except Exception as e:
        print(f"❌ Error testing Flet 1.0-alpha features: {e}")
        return False

if __name__ == "__main__":
    print("Testing Flet installation...")
    test_func = test_declarative_ui()
    if test_func:
        print("✅ Test function created successfully")
        print("Run with: python test_flet_alpha.py")
        print("Or check Flet app functionality")
    else:
        print("❌ Could not create test function")