"""
Motor Principal do Ray Tracer
Renderiza a cena e gera imagens
"""

import math
from geometry import Vec3, Ray
from scene import Scene, Light
from materials import Color
from typing import Tuple


class Camera:
    """Câmera de renderização"""
    
    def __init__(self, 
                 position: Vec3,
                 look_at: Vec3,
                 up: Vec3 = Vec3(0, 1, 0),
                 fov: float = 60.0,
                 aspect_ratio: float = 16/9):
        """
        Inicializa câmera.
        
        Args:
            position: Posição da câmera
            look_at: Ponto para onde a câmera aponta
            up: Vetor "cima" da câmera
            fov: Field of view em graus (vertical)
            aspect_ratio: Proporção largura/altura
        """
        self.position = position
        self.look_at = look_at
        self.up = up.normalize()
        self.fov = fov
        self.aspect_ratio = aspect_ratio

        # Constrói base ortonormal da câmera
        self.forward = (look_at - position).normalize()
        self.right = self.forward.cross(up).normalize()
        self.up = self.right.cross(self.forward).normalize()

        # Calcula dimensões do plano de visão
        fov_rad = math.radians(fov / 2)
        self.viewport_height = 2.0 * math.tan(fov_rad)
        self.viewport_width = self.viewport_height * aspect_ratio

    def get_ray(self, x: float, y: float) -> Ray:
        """
        Retorna raio para pixel (x, y).
        x, y devem estar normalizados [0, 1]
        """
        # Coordenadas do plano de visão normalizadas [-0.5, 0.5]
        viewport_x = (x - 0.5) * self.viewport_width
        viewport_y = (0.5 - y) * self.viewport_height  # Y invertido (de cima para baixo)

        # Direção do raio
        direction = (
            self.forward +
            self.right * viewport_x +
            self.up * viewport_y
        ).normalize()

        return Ray(self.position, direction)


class RayTracer:
    """Motor de ray tracing"""
    
    def __init__(self, width: int = 800, height: int = 600, samples: int = 4):
        """
        Inicializa ray tracer.
        
        Args:
            width: Largura em pixels
            height: Altura em pixels
            samples: Amostras por pixel (para anti-aliasing)
        """
        self.width = width
        self.height = height
        self.samples = samples
        self.image = []

    def render(self, scene: Scene, camera: Camera) -> list:
        """
        Renderiza a cena.
        
        Returns:
            Lista 2D de cores RGB [altura][largura]
        """
        print(f"Renderizando {self.width}x{self.height}...")
        self.image = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Anti-aliasing: múltiplas amostras por pixel
                color = Color(0, 0, 0)
                
                for _ in range(self.samples):
                    # Pequena perturbação aleatória
                    import random
                    px = (x + random.random()) / self.width
                    py = (y + random.random()) / self.height

                    ray = camera.get_ray(px, py)
                    color = color + scene.trace_ray(ray)

                # Média das amostras
                color = color * (1.0 / self.samples)
                row.append(color)

            self.image.append(row)
            
            # Progresso
            if (y + 1) % max(1, self.height // 10) == 0:
                print(f"  {(y + 1) / self.height * 100:.0f}% concluído")

        print("Renderização concluída!")
        return self.image

    def save_ppm(self, filename: str):
        """Salva imagem em formato PPM (P3)"""
        if not self.image:
            raise RuntimeError("Nenhuma imagem foi renderizada")

        with open(filename, 'w') as f:
            # Header PPM
            f.write(f"P3\n")
            f.write(f"{self.width} {self.height}\n")
            f.write(f"255\n")

            # Pixels
            for row in self.image:
                for color in row:
                    r, g, b = color.to_rgb()
                    f.write(f"{r} {g} {b} ")
                f.write("\n")

        print(f"Imagem salva em: {filename}")

    def save_png(self, filename: str):
        """Salva imagem em formato PNG (requer PIL)"""
        try:
            from PIL import Image
        except ImportError:
            print("PIL não instalado. Use: pip install Pillow")
            return

        if not self.image:
            raise RuntimeError("Nenhuma imagem foi renderizada")

        # Cria imagem PIL
        img = Image.new('RGB', (self.width, self.height))
        pixels = img.load()

        for y in range(self.height):
            for x in range(self.width):
                color = self.image[y][x]
                pixels[x, y] = color.to_rgb()

        img.save(filename)
        print(f"Imagem salva em: {filename}")
