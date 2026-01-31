"""
Запустить приложение для плоттера
"""
from pathlib import Path

from application.vart import VARTApplication


def _launch():
    _home_path = r"/home/kiraflux/Repos/Vart/Code/Vart-Studio"
    app = VARTApplication(Path(_home_path))

    app.run("VART-Studio", (1280, 720))


if __name__ == '__main__':
    _launch()
