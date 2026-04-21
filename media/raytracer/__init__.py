"""
Ray Tracer - Renderizador de raios de luz implementado do zero em Python

Módulos:
- geometry: Vetores, raios e geometria (esferas)
- materials: Cores e propriedades de materiais
- scene: Gerenciamento de cena, luzes e cálculos de iluminação
- raytracer: Motor de renderização e câmera
- example: Scripts de demonstração

Exemplo de uso:
    from geometry import Vec3, Sphere
    from materials import Material, RED
    from scene import Scene, Light
    from raytracer import Camera, RayTracer

    # Cria cena
    scene = Scene()
    scene.add_sphere(Sphere(Vec3(0, 0, -5), 1.0, Material(RED)))
    scene.add_light(Light(Vec3(5, 5, 0), Color(1, 1, 1)))

    # Renderiza
    camera = Camera(Vec3(0, 0, 0), Vec3(0, 0, -5))
    tracer = RayTracer(800, 600)
    tracer.render(scene, camera)
    tracer.save_ppm("output.ppm")
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"

from .geometry import Vec3, Ray, Sphere, HitRecord
from .materials import Color, Material
from .scene import Scene, Light
from .raytracer import Camera, RayTracer

__all__ = [
    'Vec3', 'Ray', 'Sphere', 'HitRecord',
    'Color', 'Material',
    'Scene', 'Light',
    'Camera', 'RayTracer'
]
