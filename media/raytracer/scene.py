"""
Módulo de Iluminação para Ray Tracer
Implementa modelo de iluminação Phong com sombras
"""

from dataclasses import dataclass
from typing import List
from geometry import Vec3, Ray, HitRecord, Sphere
from materials import Color, Material


@dataclass
class Light:
    """Fonte de luz (puntual)"""
    position: Vec3
    color: Color
    intensity: float = 1.0

    def get_direction_to(self, point: Vec3) -> Vec3:
        """Retorna direção normalizada da luz até o ponto"""
        return (self.position - point).normalize()

    def get_distance_to(self, point: Vec3) -> float:
        """Retorna distância da luz até o ponto"""
        return (self.position - point).length()


class Scene:
    """Gerenciador de cena com objetos e luzes"""
    
    def __init__(self, ambient_light: Color = None):
        self.objects: List[Sphere] = []
        self.lights: List[Light] = []
        self.ambient_light = ambient_light or Color(0.2, 0.2, 0.2)

    def add_sphere(self, sphere: Sphere):
        """Adiciona esfera à cena"""
        self.objects.append(sphere)

    def add_light(self, light: Light):
        """Adiciona luz à cena"""
        self.lights.append(light)

    def trace_ray(self, ray: Ray, max_depth: int = 5) -> Color:
        """
        Traça um raio na cena e retorna a cor.
        Implementa recursão para reflexões.
        """
        if max_depth <= 0:
            return Color(0, 0, 0)

        # Encontra intersecção mais próxima
        closest_hit = None
        min_t = float('inf')

        for obj in self.objects:
            hit = obj.intersect(ray)
            if hit.hit and hit.t < min_t:
                min_t = hit.t
                closest_hit = hit

        # Se não acertou nada, retorna cor de fundo
        if closest_hit is None:
            return self._background_color(ray)

        # Calcula iluminação no ponto de intersecção
        return self._calculate_lighting(ray, closest_hit, max_depth)

    def _calculate_lighting(self, incident_ray: Ray, hit: HitRecord, max_depth: int) -> Color:
        """
        Calcula iluminação usando modelo Phong com sombras.
        """
        material = hit.material
        final_color = Color(0, 0, 0)

        # Iluminação ambiente
        ambient = self.ambient_light
        final_color = Color(
            material.color.r * ambient.r * material.ambient,
            material.color.g * ambient.g * material.ambient,
            material.color.b * ambient.b * material.ambient
        )

        # Para cada luz na cena
        for light in self.lights:
            # Direção da luz
            light_dir = light.get_direction_to(hit.point)
            
            # Testa se há sombra
            shadow_ray = Ray(hit.point, light_dir)
            shadow = self._is_in_shadow(shadow_ray, light)

            if not shadow:
                # Iluminação difusa (Lei de Lambert)
                diffuse_intensity = max(0, hit.normal.dot(light_dir))
                diffuse = light.intensity * diffuse_intensity * material.diffuse
                
                diffuse_color = Color(
                    material.color.r * diffuse,
                    material.color.g * diffuse,
                    material.color.b * diffuse
                )

                # Iluminação especular (Phong)
                view_dir = (-incident_ray.direction).normalize()
                reflect_dir = self._reflect(light_dir, hit.normal)
                specular_intensity = max(0, view_dir.dot(reflect_dir))
                specular_intensity = specular_intensity ** material.shininess
                specular = light.intensity * specular_intensity * material.specular

                specular_color = light.color * specular

                # Combina
                final_color = final_color + diffuse_color + specular_color

        # Reflexão recursiva
        if material.reflectivity > 0:
            reflect_dir = self._reflect(incident_ray.direction, hit.normal)
            reflect_ray = Ray(hit.point, reflect_dir)
            reflect_color = self.trace_ray(reflect_ray, max_depth - 1)
            
            final_color = Color(
                min(1.0, final_color.r + reflect_color.r * material.reflectivity),
                min(1.0, final_color.g + reflect_color.g * material.reflectivity),
                min(1.0, final_color.b + reflect_color.b * material.reflectivity)
            )

        return final_color

    def _is_in_shadow(self, shadow_ray: Ray, light: Light) -> bool:
        """Verifica se o ponto está em sombra"""
        light_distance = light.get_distance_to(shadow_ray.origin)

        for obj in self.objects:
            hit = obj.intersect(shadow_ray, t_min=0.001, t_max=light_distance)
            if hit.hit:
                return True

        return False

    def _reflect(self, incident: Vec3, normal: Vec3) -> Vec3:
        """
        Calcula vetor refletido.
        R = I - 2(I·N)N
        """
        return (incident - normal * (2 * incident.dot(normal))).normalize()

    def _background_color(self, ray: Ray) -> Color:
        """Cor de fundo gradiente simples"""
        # Gradiente azul baseado na direção Y do raio
        t = 0.5 * (ray.direction.y + 1.0)
        return Color(1.0, 1.0, 1.0) * (1.0 - t) + Color(0.5, 0.7, 1.0) * t
