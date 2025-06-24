#!/usr/bin/env python3
"""
Скрипт завдання Ray для тренування YOLO
Цей скрипт запускається як завдання Ray на кластері
"""

import os
import sys
import subprocess
from pathlib import Path

def run_subprocess_with_streaming(cmd, shell=False, check=False, text=True, env=None):
    """Run a subprocess and stream stdout and stderr in real time."""
    process = subprocess.Popen(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=text,
        bufsize=1,
        env=env
    )
    output = []
    for line in process.stdout:
        print(line, end='')
        output.append(line)
    process.stdout.close()
    return_code = process.wait()
    if check and return_code != 0:
        raise subprocess.CalledProcessError(return_code, cmd, ''.join(output))
    return return_code

def install_system_dependencies():
    """Встановлює системні залежності, необхідні для OpenCV"""
    print("🔧 Installing system dependencies...")
    try:
        # Перевіряємо, чи маємо доступ sudo та чи доступний apt
        result = run_subprocess_with_streaming(["which", "apt"], check=False)
        if result != 0:
            print("⚠️  apt not found, skipping system dependencies")
            return True
        # Встановлюємо libgl1 та інші залежності OpenCV
        run_subprocess_with_streaming(
            "sudo apt update && sudo apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1",
            shell=True, check=True
        )
        print("✅ System dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Failed to install system dependencies: {e}")
        print("   This might cause OpenCV issues, but continuing...")
        print(f"   STDERR: {e.output if hasattr(e, 'output') else ''}")
        return True  # Продовжуємо в будь-якому випадку, оскільки це може бути не критично
    except Exception as e:
        print(f"⚠️  Error installing system dependencies: {e}")
        return True  # Продовжуємо в будь-якому випадку

def install_requirements():
    """Встановлює Python вимоги на воркері"""
    print("📦 Installing Python requirements...")
    try:
        run_subprocess_with_streaming([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Python requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python requirements: {e}")
        print(f"STDERR: {e.output if hasattr(e, 'output') else ''}")
        return False

def setup_environment():
    """Налаштовує змінні середовища на воркері"""
    wandb_key = os.getenv('WANDB_API_KEY')
    if wandb_key:
        print("✅ WANDB_API_KEY found in environment")
    else:
        print("⚠️  WANDB_API_KEY not found - W&B logging may not work")
    
    # Створюємо .env файл для скрипта тренування
    with open('.env', 'w') as f:
        f.write(f"WANDB_API_KEY={wandb_key or ''}")
    print("✅ Environment file created")
    return True

def run_yolo_training():
    """Запускає тренування YOLO на воркері"""
    print("🚀 Starting YOLO training...")
    try:
        return_code = run_subprocess_with_streaming([
            sys.executable, "train.py"
        ], check=False)
        if return_code == 0:
            print("✅ Training completed successfully")
            return True
        else:
            print(f"❌ Training failed with return code: {return_code}")
            return False
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

def main():
    """Головна функція - запускається як завдання Ray"""
    print("=" * 50)
    print("🤖 Ray Job: YOLO Training")
    print("=" * 50)
    
    # Перелічуємо файли в робочій директорії
    print("📁 Files in working directory:")
    for file in sorted(Path('.').iterdir()):
        if file.is_file():
            print(f"  - {file.name}")
    
    # Крок 1: Встановлюємо системні залежності
    print("\n🔧 Step 1: Installing system dependencies...")
    if not install_system_dependencies():
        print("❌ Failed to install system dependencies")
        sys.exit(1)
    
    # Крок 2: Встановлюємо Python залежності
    print("\n🔧 Step 2: Installing Python requirements...")
    if not install_requirements():
        print("❌ Failed to install Python requirements")
        sys.exit(1)
    
    # Крок 3: Налаштовуємо середовище
    print("\n🔧 Step 3: Setting up environment...")
    if not setup_environment():
        print("❌ Failed to setup environment")
        sys.exit(1)
    
    # Крок 4: Запускаємо тренування
    print("\n🔧 Step 4: Running YOLO training...")
    if not run_yolo_training():
        print("❌ Training failed")
        sys.exit(1)
    
    print("🎉 All tasks completed successfully!")

if __name__ == "__main__":
    main() 