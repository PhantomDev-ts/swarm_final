"""
Módulo de Geometria para Ray Tracer
Classes e operações matemáticas vetoriais para ray tracing
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class Vec3:
    """Vetor 3D - estrutura fundamental para geometria"""
    x: float
    y: float
    z: float

    def __add__(self, other: 'Vec3') -> 'Vec3':
        """Adição de vetores"""
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vec3') -> 'Vec3':
        """Subtração de vetores"""
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> 'Vec3':
        """Multiplicação por escalar"""
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> 'Vec3':
        """Multiplicação por escalar (comutativa)"""
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> 'Vec3':
        """Divisão por escalar"""
        if scalar == 0:
            raise ValueError("Divisão por zero")
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other: 'Vec3') -> float:
        """Produto escalar (dot product)"""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vec3') -> 'Vec3':
        """Produto vetorial (cross product)"""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def length(self) -> float:
        """Comprimento (magnitude) do vetor"""
        return math.sqrt(self.dot(self))

    def normalize(self) -> 'Vec3':
        """Vetor normalizado (comprimento = 1)"""
        len_val = self.length()
        if len_val == 0:
            raise ValueError("Não é possível normalizar vetor zero")
        return self / len_val

    def __neg__(self) -> 'Vec3':
        """Negação do vetor"""
        return Vec3(-self.x, -self.y, -self.z)

    def __str__(self) -> str:
        return f"Vec3({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"


@dataclass
class Ray:
    """Raio: origem + direção"""
    origin: Vec3
    direction: Vec3  # Deve estar normalizado

    def point_at(self, t: float) -> Vec3:
        """Retorna o ponto no raio na distância t"""
        return self.origin + self.direction * t


class HitRecord:
    """Registro de intersecção raio-objeto"""
    
    def __init__(self):
        self.t: Optional[float] = None  # Distância do raio
        self.point: Optional[Vec3] = None  # Ponto de intersecção
        self.normal: Optional[Vec3] = None  # Normal na superfície
        self.material: Optional['Material'] = None  # Material do objeto
        self.hit: bool = False  # Se houve intersecção


class Sphere:
    """Esfera definida por centro e raio"""
    
    def __init__(self, center: Vec3, radius: float, material: 'Material'):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, ray: Ray, t_min: float = 0.001, t_max: float = float('inf')) -> HitRecord:
        """
        Calcula intersecção entre raio e esfera usando equação quadrática.
        
        Equação: (P - C) · (P - C) = r²
        onde P = O + t*D (ponto no raio)
        
        Resulta em: a*t² + b*t + c = 0
        """
        record = HitRecord()
        
        # Vetor do centro da esfera à origem do raio
        oc = ray.origin - self.center
        
        # Coeficientes da equação quadrática
        a = ray.direction.dot(ray.direction)
        b = 2.0 * oc.dot(ray.direction)
        c = oc.dot(oc) - self.radius * self.radius
        
        # Discriminante
        discriminant = b * b - 4 * a * c
        
        if discriminant < 0:
            return record
        
        # Raízes da equação quadrática
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)
        
        # Pega a intersecção mais próxima dentro do intervalo
        t = None
        if t_min < t1 < t_max:
            t = t1
        elif t_min < t2 < t_max:
            t = t2
        
        if t is None:
            return record
        
        # Calcula ponto e normal
        record.t = t
        record.point = ray.point_at(t)
        record.normal = (record.point - self.center).normalize()
        record.material = self.material
        record.hit = True
        
        return record
