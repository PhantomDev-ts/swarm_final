"""
Módulo de Materiais para Ray Tracer
Define cores, propriedades de reflexão e iluminação
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Color:
    """Cor RGB (valores 0-1)"""
    r: float
    g: float
    b: float

    def __add__(self, other: 'Color') -> 'Color':
        """Adição de cores"""
        return Color(
            min(1.0, self.r + other.r),
            min(1.0, self.g + other.g),
            min(1.0, self.b + other.b)
        )

    def __mul__(self, scalar: float) -> 'Color':
        """Multiplicação por escalar (intensidade)"""
        return Color(
            min(1.0, self.r * scalar),
            min(1.0, self.g * scalar),
            min(1.0, self.b * scalar)
        )

    def __rmul__(self, scalar: float) -> 'Color':
        return self.__mul__(scalar)

    def to_rgb(self) -> Tuple[int, int, int]:
        """Converte para RGB 8-bit (0-255)"""
        return (
            int(self.r * 255),
            int(self.g * 255),
            int(self.b * 255)
        )

    def __str__(self) -> str:
        return f"Color({self.r:.3f}, {self.g:.3f}, {self.b:.3f})"


@dataclass
class Material:
    """Material de uma superfície"""
    color: Color
    ambient: float = 0.1  # Iluminação ambiente
    diffuse: float = 0.7  # Reflexão difusa (Lambert)
    specular: float = 0.2  # Reflexão especular
    shininess: float = 32.0  # Expoente para especular (Phong)
    reflectivity: float = 0.0  # Quanto reflete (0-1)


# Cores pré-definidas
def RGB(r: float, g: float, b: float) -> Color:
    """Cria cor a partir de valores 0-255"""
    return Color(r / 255, g / 255, b / 255)


# Paleta de cores
RED = Color(1.0, 0.0, 0.0)
GREEN = Color(0.0, 1.0, 0.0)
BLUE = Color(0.0, 0.0, 1.0)
WHITE = Color(1.0, 1.0, 1.0)
BLACK = Color(0.0, 0.0, 0.0)
GRAY = Color(0.5, 0.5, 0.5)
YELLOW = Color(1.0, 1.0, 0.0)
CYAN = Color(0.0, 1.0, 1.0)
MAGENTA = Color(1.0, 0.0, 1.0)
ORANGE = RGB(255, 165, 0)
PURPLE = RGB(128, 0, 128)


# Materiais pré-definidos
MATTE_WHITE = Material(
    color=WHITE,
    ambient=0.2,
    diffuse=0.8,
    specular=0.0,
    shininess=1.0,
    reflectivity=0.0
)

SHINY_RED = Material(
    color=RED,
    ambient=0.1,
    diffuse=0.6,
    specular=0.3,
    shininess=64.0,
    reflectivity=0.2
)

METAL = Material(
    color=RGB(200, 200, 200),
    ambient=0.05,
    diffuse=0.3,
    specular=0.7,
    shininess=128.0,
    reflectivity=0.8
)

PLASTIC = Material(
    color=BLUE,
    ambient=0.1,
    diffuse=0.7,
    specular=0.2,
    shininess=32.0,
    reflectivity=0.1
)
