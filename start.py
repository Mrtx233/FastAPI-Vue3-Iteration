"""
健身管理系统 - 一键启动脚本
同时启动 FastAPI 后端 (:8001) 和 Vue3 前端 (:5173)
"""
import sys
import subprocess
import signal
import time
from pathlib import Path

# 项目根目录（脚本所在位置）
ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

BACKEND_PORT = 8001
FRONTEND_PORT = 5173

# 后端 Python 解释器（按优先级查找虚拟环境）
VENV_CANDIDATES = [
    BACKEND_DIR / ".venv" / "Scripts" / "python.exe", # backend/.venv（后端依赖在此）
    ROOT / ".venv" / "Scripts" / "python.exe",       # 项目根目录 .venv
]
SYSTEM_PYTHON = sys.executable

# Windows 上 npm 是 .cmd，需要 shell=True
USE_SHELL = sys.platform == "win32"


def get_python_executable():
    """获取后端使用的 Python 解释器"""
    for venv in VENV_CANDIDATES:
        if venv.exists():
            return str(venv)
    print("[WARN] 未找到虚拟环境，使用系统 Python")
    return SYSTEM_PYTHON


def kill_on_exit(processes):
    """退出时清理所有子进程"""
    def handler(sig=None, frame=None):
        print("\n正在停止所有服务...")
        for name, proc in processes:
            if proc.poll() is None:
                proc.terminate()
                print(f"  已停止 {name}")
        sys.exit(0)
    return handler


def main():
    python = get_python_executable()

    # ---------- 启动后端 ----------
    print(f"[1/2] 启动后端  http://localhost:{BACKEND_PORT}")
    backend = subprocess.Popen(
        [python, "-m", "uvicorn", "main:app",
         "--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--reload"],
        cwd=BACKEND_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
    )

    # ---------- 启动前端 ----------
    print(f"[2/2] 启动前端  http://localhost:{FRONTEND_PORT}")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=USE_SHELL,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0,
    )

    # ---------- 注册退出清理 ----------
    processes = [("后端", backend), ("前端", frontend)]
    signal.signal(signal.SIGINT, kill_on_exit(processes))
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, kill_on_exit(processes))

    print(f"\n后端: http://localhost:{BACKEND_PORT}/docs")
    print(f"前端: http://localhost:{FRONTEND_PORT}")
    print("按 Ctrl+C 停止所有服务\n")

    # ---------- 监控子进程 ----------
    exited = set()
    try:
        while True:
            for name, proc in processes:
                if proc.poll() is not None and name not in exited:
                    exited.add(name)
                    print(f"[WARN] {name} 已退出 (code={proc.returncode})")
            if len(exited) == len(processes):
                print("\n所有服务已停止，按回车退出...")
                input()
                break
            time.sleep(3)
    except KeyboardInterrupt:
        kill_on_exit(processes)()


if __name__ == "__main__":
    main()
# powershell -Command "Get-NetTCPConnection -LocalPort 8001 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"