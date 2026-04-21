"""
Exemplo de Ray Tracer
Renderiza uma cena com esferas, luzes e sombras
"""

from geometry import Vec3, Sphere
from materials import (
    Color, Material, RED, GREEN, BLUE, WHITE, GRAY,
    SHINY_RED, METAL, PLASTIC, MATTE_WHITE, RGB
)
from scene import Scene, Light
from raytracer import Camera, RayTracer


def create_demo_scene() -> Scene:
    """Cria cena de demonstração com esferas e luzes"""
    
    scene = Scene(ambient_light=Color(0.3, 0.3, 0.3))

    # ===== OBJETOS =====
    
    # Esfera vermelha brilhante (esquerda)
    red_sphere = Sphere(
        center=Vec3(-2.5, 0, -8),
        radius=1.5,
        material=SHINY_RED
    )
    scene.add_sphere(red_sphere)

    # Esfera metálica (centro)
    metal_sphere = Sphere(
        center=Vec3(0, 0, -8),
        radius=1.5,
        material=METAL
    )
    scene.add_sphere(metal_sphere)

    # Esfera plástica azul (direita)
    blue_plastic = Material(
        color=BLUE,
        ambient=0.1,
        diffuse=0.7,
        specular=0.3,
        shininess=32.0,
        reflectivity=0.05
    )
    plastic_sphere = Sphere(
        center=Vec3(2.5, 0, -8),
        radius=1.5,
        material=blue_plastic
    )
    scene.add_sphere(plastic_sphere)

    # Esfera pequena (frente, para teste de sombra)
    small_sphere = Sphere(
        center=Vec3(-1, -1.5, -5),
        radius=0.5,
        material=Material(
            color=RGB(255, 255, 0),  # Amarelo
            ambient=0.1,
            diffuse=0.8,
            specular=0.2,
            shininess=16.0,
            reflectivity=0.1
        )
    )
    scene.add_sphere(small_sphere)

    # Esfera grande no fundo (branca fosca)
    bg_sphere = Sphere(
        center=Vec3(0, -3, -12),
        radius=2,
        material=MATTE_WHITE
    )
    scene.add_sphere(bg_sphere)

    # ===== LUZES =====
    
    # Luz branca forte (frontal superior)
    light1 = Light(
        position=Vec3(5, 5, 0),
        color=WHITE,
        intensity=1.0
    )
    scene.add_light(light1)

    # Luz vermelha (lateral esquerda)
    light2 = Light(
        position=Vec3(-5, 3, 5),
        color=RED,
        intensity=0.6
    )
    scene.add_light(light2)

    # Luz azul (lateral direita)
    light3 = Light(
        position=Vec3(5, 2, 5),
        color=BLUE,
        intensity=0.5
    )
    scene.add_light(light3)

    return scene


def create_glossy_scene() -> Scene:
    """Cena alternativa com esferas mais reflexivas"""
    
    scene = Scene(ambient_light=Color(0.2, 0.2, 0.25))

    # Esferas com diferentes níveis de reflexão
    for i in range(-2, 3):
        reflectivity = (i + 2) / 4.0  # 0 a 1
        
        sphere = Sphere(
            center=Vec3(i * 2, 0, -8),
            radius=1.0,
            material=Material(
                color=RGB(200, 100, 50),  # Laranja
                ambient=0.05,
                diffuse=0.5,
                specular=0.4,
                shininess=128.0,
                reflectivity=reflectivity
            )
        )
        scene.add_sphere(sphere)

    # Luz principal
    light1 = Light(
        position=Vec3(0, 5, 2),
        color=WHITE,
        intensity=1.2
    )
    scene.add_light(light1)

    # Luz de preenchimento
    light2 = Light(
        position=Vec3(-4, 2, 0),
        color=Color(0.7, 0.7, 1.0),  # Azulado
        intensity=0.5
    )
    scene.add_light(light2)

    return scene


def main():
    """Renderiza e salva demonstração"""
    
    print("=" * 60)
    print("RAY TRACER - Renderizador de Esferas com Ray Tracing")
    print("=" * 60)
    print()

    # Cria câmera
    camera = Camera(
        position=Vec3(0, 1, 2),
        look_at=Vec3(0, 0, -8),
        up=Vec3(0, 1, 0),
        fov=50,
        aspect_ratio=16/9
    )

    print("Câmera:")
    print(f"  Posição: {camera.position}")
    print(f"  Alvo: {camera.look_at}")
    print(f"  FOV: 50°")
    print()

    # ===== Renderização 1: Cena Principal =====
    print("CENA 1: Demonstração Principal")
    print("-" * 60)
    
    scene1 = create_demo_scene()
    print(f"Objetos: {len(scene1.objects)}")
    print(f"Luzes: {len(scene1.lights)}")
    print()

    tracer1 = RayTracer(
        width=1200,
        height=900,
        samples=4  # 4 amostras por pixel para anti-aliasing
    )

    print("Iniciando renderização...")
    tracer1.render(scene1, camera)
    
    # Salva em PPM (sempre funciona)
    output1_ppm = "output_scene1.ppm"
    tracer1.save_ppm(output1_ppm)
    
    # Tenta salvar em PNG
    try:
        output1_png = "output_scene1.png"
        tracer1.save_png(output1_png)
    except Exception as e:
        print(f"Aviso: Não foi possível salvar PNG: {e}")
    
    print()

    # ===== Renderização 2: Cena Glossy =====
    print("CENA 2: Esferas Reflexivas")
    print("-" * 60)

    camera2 = Camera(
        position=Vec3(0, 1, 4),
        look_at=Vec3(0, 0, -6),
        up=Vec3(0, 1, 0),
        fov=45,
        aspect_ratio=16/9
    )

    scene2 = create_glossy_scene()
    print(f"Objetos: {len(scene2.objects)}")
    print(f"Luzes: {len(scene2.lights)}")
    print()

    tracer2 = RayTracer(
        width=1200,
        height=900,
        samples=4
    )

    print("Iniciando renderização...")
    tracer2.render(scene2, camera2)

    output2_ppm = "output_scene2.ppm"
    tracer2.save_ppm(output2_ppm)

    try:
        output2_png = "output_scene2.png"
        tracer2.save_png(output2_png)
    except Exception as e:
        print(f"Aviso: Não foi possível salvar PNG: {e}")

    print()
    print("=" * 60)
    print("Renderização concluída!")
    print("=" * 60)
    print()
    print("Explicação da implementação:")
    print()
    print("1. GEOMETRIA (geometry.py)")
    print("   - Vec3: Operações vetoriais (dot, cross, normalize)")
    print("   - Ray: Raio = origem + direção*t")
    print("   - Sphere: Intersecção raio-esfera via equação quadrática")
    print()
    print("2. MATERIAIS (materials.py)")
    print("   - Cores RGB com valores 0-1")
    print("   - Propriedades: ambiente, difusa, especular, reflexão")
    print()
    print("3. ILUMINAÇÃO (scene.py)")
    print("   - Modelo Phong: ambiente + difusa + especular")
    print("   - Raios de sombra para detectar oclusões")
    print("   - Reflexão recursiva com limite de profundidade")
    print()
    print("4. RENDERIZAÇÃO (raytracer.py)")
    print("   - Câmera com FOV e aspect ratio")
    print("   - Geração de raios primários")
    print("   - Anti-aliasing com múltiplas amostras")
    print()


if __name__ == "__main__":
    main()
