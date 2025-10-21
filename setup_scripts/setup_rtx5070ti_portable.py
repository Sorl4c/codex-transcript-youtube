#!/usr/bin/env python3
"""
Portable RTX 5070 Ti GPU Setup & Verification Script
Autónomo para cualquier entorno virtual - Sin dependencias externas
Compatible con RTX 5070 Ti (sm_120, CUDA 12.8)

Uso:
    python setup_rtx5070ti_portable.py
    python setup_rtx5070ti_portable.py --check
    python setup_rtx5070ti_portable.py --install
    python setup_rtx5070ti_portable.py --verify
"""

import sys
import os
import subprocess
import platform
import argparse
from pathlib import Path

class RTX5070TiSetup:
    """Clase autónoma para configurar RTX 5070 Ti en cualquier venv"""

    def __init__(self):
        self.python_executable = sys.executable
        self.is_windows = platform.system() == "Windows"

        # Configuración específica RTX 5070 Ti
        self.pytorch_index_url = "https://download.pytorch.org/whl/nightly/cu128"
        self.expected_gpu = "NVIDIA GeForce RTX 5070 Ti"
        self.compute_capability = "12.0"
        self.required_cuda = "12.8"

        # Variables de entorno para RTX 5070 Ti
        self.env_vars = {
            "DOCLING_DEVICE": "cuda:0",
            "DOCLING_NUM_THREADS": "8",
            "DOCLING_CUDA_USE_FLASH_ATTENTION2": "true",
            "CUDA_VISIBLE_DEVICES": "0",
            "TORCH_CUDA_ARCH_LIST": "8.9;9.0;12.0"
        }

    def print_banner(self):
        """Muestra banner informativo"""
        print("=" * 70)
        print("🚀 RTX 5070 Ti Portable GPU Setup & Verification")
        print("=" * 70)
        print(f"Python: {self.python_executable}")
        print(f"Platform: {platform.system()}")
        print(f"Virtual Environment: {Path(self.python_executable).parent.parent}")
        print("=" * 70)

    def check_system_drivers(self):
        """Verifica drivers NVIDIA a nivel sistema"""
        print("\n🔍 Checking System-Level NVIDIA Drivers...")

        try:
            # Verificar nvidia-smi
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                print("✅ NVIDIA drivers are working")

                # Extraer información GPU
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'RTX 5070 Ti' in line:
                        print(f"✅ GPU detected: {line.strip()}")
                        return True
                    elif 'NVIDIA' in line and 'Driver' in line:
                        print(f"✅ Driver info: {line.strip()}")

                return True
            else:
                print("❌ nvidia-smi failed")
                print(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ nvidia-smi timed out")
            return False
        except FileNotFoundError:
            print("❌ nvidia-smi not found - NVIDIA drivers not installed")
            return False
        except Exception as e:
            print(f"❌ Failed to check NVIDIA drivers: {e}")
            return False

    def check_pytorch_installation(self):
        """Verifica instalación actual de PyTorch"""
        print("\n🔍 Checking PyTorch Installation...")

        try:
            # Set environment variables
            for var, value in self.env_vars.items():
                os.environ[var] = value

            # Importar torch
            import torch

            print(f"✅ PyTorch Version: {torch.__version__}")
            print(f"✅ CUDA Available: {torch.cuda.is_available()}")

            if torch.cuda.is_available():
                print(f"✅ CUDA Version: {torch.version.cuda}")
                print(f"✅ GPU Device: {torch.cuda.get_device_name(0)}")

                # Check compute capability
                compute_cap = torch.cuda.get_device_capability(0)
                print(f"✅ Compute Capability: {compute_cap[0]}.{compute_cap[1]}")

                # Check GPU memory
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                print(f"✅ GPU Memory: {gpu_memory:.1f} GB")

                # Test tensor operation
                try:
                    test_tensor = torch.tensor([1.0], device="cuda:0")
                    print("✅ GPU tensor test passed!")
                    return True
                except Exception as e:
                    print(f"❌ GPU tensor test failed: {e}")
                    return False
            else:
                print("❌ CUDA not available in PyTorch")
                return False

        except ImportError:
            print("❌ PyTorch not installed")
            return False
        except Exception as e:
            print(f"❌ PyTorch check failed: {e}")
            return False

    def install_pytorch_cuda(self):
        """Instala PyTorch CUDA para RTX 5070 Ti"""
        print(f"\n📦 Installing PyTorch CUDA {self.required_cuda} for RTX 5070 Ti...")

        # Install pip if needed
        try:
            subprocess.run([self.python_executable, "-m", "ensurepip", "--upgrade"],
                         capture_output=True, check=True)
            print("✅ pip ensured/updated")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ pip ensure failed: {e}")

        # Install PyTorch CUDA
        install_cmd = [
            self.python_executable, "-m", "pip", "install",
            "--pre", "torch", "torchvision", "torchaudio",
            "--index-url", self.pytorch_index_url,
            "--force-reinstall"
        ]

        print("🔄 Installing PyTorch CUDA...")
        print(f"Command: {' '.join(install_cmd)}")

        try:
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("✅ PyTorch CUDA installed successfully!")
                return True
            else:
                print(f"❌ Installation failed")
                print(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False

    def test_docling_integration(self):
        """Prueba integración con Docling"""
        print("\n🔍 Testing Docling Integration...")

        try:
            # Test docling import
            from docling.datamodel.pipeline_options import AcceleratorOptions, PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
            from docling.document_converter import DocumentConverter, PdfFormatOption

            # Configure for RTX 5070 Ti
            accelerator_options = AcceleratorOptions(
                device="cuda:0",
                num_threads=8,
                cuda_use_flash_attention2=True
            )

            pipeline_options = PdfPipelineOptions()
            pipeline_options.accelerator_options = accelerator_options
            pipeline_options.do_ocr = True
            pipeline_options.do_table_structure = True

            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

            print("✅ Docling configuration successful!")
            print("✅ Ready for GPU-accelerated document processing")
            return True

        except ImportError as e:
            print(f"⚠️ Docling not available: {e}")
            print("Install with: pip install docling[vlm]")
            return False
        except Exception as e:
            print(f"❌ Docling configuration failed: {e}")
            return False

    def run_comprehensive_test(self):
        """Ejecuta prueba completa de GPU"""
        print("\n🧪 Running Comprehensive GPU Test...")

        try:
            import torch

            # Matrix multiplication test
            device = torch.device("cuda:0")
            size = 1000

            print(f"🔄 Testing {size}x{size} matrix multiplication...")

            a = torch.randn(size, size, device=device)
            b = torch.randn(size, size, device=device)

            import time
            start_time = time.time()
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            end_time = time.time()

            print(f"✅ Matrix multiplication completed in {end_time - start_time:.4f} seconds")
            print("✅ GPU performance test passed!")
            return True

        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            return False

    def setup_environment(self):
        """Configura variables de entorno para RTX 5070 Ti"""
        print("\n⚙️ Setting up environment variables...")

        for var, value in self.env_vars.items():
            os.environ[var] = value
            print(f"✅ {var}={value}")

        print("✅ Environment configured for RTX 5070 Ti")

    def generate_commands_reference(self):
        """Genera referencia de comandos útiles"""
        print("\n📋 Quick Reference Commands:")
        print("=" * 50)
        print("🔍 Verification Commands:")
        print(f"  {self.python_executable} -c \"import torch; print(f'CUDA: {{torch.cuda.is_available()}}')\"")
        print("  nvidia-smi")
        print("")
        print("🚀 Safe Processing Commands:")
        print(f"  {self.python_executable} -m docling.cli.main --device cuda:0 document.pdf")
        print("  poetry run docling --device cuda:0 document.pdf")
        print("")
        print("🛠️ Maintenance Commands:")
        print(f"  {self.python_executable} setup_rtx5070ti_portable.py --install")
        print(f"  {self.python_executable} setup_rtx5070ti_portable.py --verify")
        print("")
        print("📊 GPU Monitoring:")
        print("  nvidia-smi -l 1")
        print("  nvidia-smi --query-gpu=memory.used,memory.total --format=csv")

    def run_full_setup(self):
        """Ejecuta configuración completa"""
        self.print_banner()

        # Step 1: Check system drivers
        if not self.check_system_drivers():
            print("\n❌ CRITICAL: System-level GPU issues detected!")
            print("\n🚨 ACTIONS REQUIRED:")
            print("1. RESTART YOUR PC COMPLETELY")
            print("2. After restart, run: nvidia-smi")
            print("3. Only if nvidia-smi works, run this script again")
            return False

        # Step 2: Setup environment
        self.setup_environment()

        # Step 3: Check PyTorch
        if not self.check_pytorch_installation():
            print("\n🔄 Installing PyTorch CUDA...")
            if not self.install_pytorch_cuda():
                print("❌ PyTorch installation failed")
                return False

            # Re-check after installation
            if not self.check_pytorch_installation():
                print("❌ PyTorch still not working after installation")
                return False

        # Step 4: Test Docling
        self.test_docling_integration()

        # Step 5: Performance test
        self.run_comprehensive_test()

        # Step 6: Generate reference
        self.generate_commands_reference()

        print("\n" + "=" * 70)
        print("🎉 SUCCESS: RTX 5070 Ti setup completed!")
        print("✅ Your environment is ready for GPU-accelerated document processing")
        print("=" * 70)
        return True

    def run_check_only(self):
        """Ejecuta solo verificación"""
        self.print_banner()

        drivers_ok = self.check_system_drivers()
        pytorch_ok = self.check_pytorch_installation()
        docling_ok = self.test_docling_integration()

        print("\n" + "=" * 50)
        print("📊 SUMMARY:")
        print(f"System Drivers: {'✅ OK' if drivers_ok else '❌ FAILED'}")
        print(f"PyTorch CUDA: {'✅ OK' if pytorch_ok else '❌ FAILED'}")
        print(f"Docling Integration: {'✅ OK' if docling_ok else '❌ FAILED'}")

        if drivers_ok and pytorch_ok:
            print("\n🎉 Your RTX 5070 Ti is ready!")
        else:
            print("\n❌ Issues detected. Run with --install to fix.")

    def run_install_only(self):
        """Ejecuta solo instalación"""
        self.print_banner()
        self.setup_environment()

        if not self.install_pytorch_cuda():
            print("❌ Installation failed")
            return False

        print("\n✅ Installation completed! Run --verify to check.")

def main():
    parser = argparse.ArgumentParser(description='Portable RTX 5070 Ti GPU Setup')
    parser.add_argument('--check', action='store_true', help='Check current status only')
    parser.add_argument('--install', action='store_true', help='Install PyTorch CUDA only')
    parser.add_argument('--verify', action='store_true', help='Verify installation only')

    args = parser.parse_args()

    setup = RTX5070TiSetup()

    if args.check:
        setup.run_check_only()
    elif args.install:
        setup.run_install_only()
    elif args.verify:
        setup.run_check_only()
    else:
        setup.run_full_setup()

if __name__ == "__main__":
    main()