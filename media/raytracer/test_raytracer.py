"""
Testes Unitários para Ray Tracer

Verifica funcionamento de todos os módulos com testes simples
"""

import math
import sys
from geometry import Vec3, Ray, Sphere
from materials import Color, Material, RED, BLUE
from scene import Scene, Light
from raytracer import Camera, RayTracer


def test_vec3_operations():
    """Testa operações vetoriais"""
    print("🧪 Testando operações vetoriais...")

    v1 = Vec3(1, 2, 3)
    v2 = Vec3(4, 5, 6)

    # Adição
    assert (v1 + v2).x == 5
    print("  ✓ Adição")

    # Subtração
    assert (v1 - v2).z == -3
    print("  ✓ Subtração")

    # Multiplicação por escalar
    v3 = v1 * 2
    assert v3.y == 4
    print("  ✓ Multiplicação escalar")

    # Divisão por escalar
    v4 = v2 / 2
    assert v4.x == 2
    print("  ✓ Divisão escalar")

    # Produto escalar
    dot = v1.dot(v2)
    assert dot == 32  # 1*4 + 2*5 + 3*6
    print("  ✓ Produto escalar")

    # Produto vetorial
    cross = v1.cross(v2)
    assert cross.x == -3  # 2*6 - 3*5 = -3
    print("  ✓ Produto vetorial")

    # Comprimento
    v5 = Vec3(3, 4, 0)
    assert abs(v5.length() - 5.0) < 0.001
    print("  ✓ Comprimento")

    # Normalização
    v6 = v5.normalize()
    assert abs(v6.length() - 1.0) < 0.001
    print("  ✓ Normalização")

    print("✅ Todos os testes de Vec3 passaram!\n")


def test_ray_sphere_intersection():
    """Testa interseção raio-esfera"""
    print("🧪 Testando interseção raio-esfera...")

    sphere = Sphere(
        center=Vec3(0, 0, -5),
        radius=1.0,
        material=Material(RED)
    )

    # Raio direto ao centro
    ray1 = Ray(Vec3(0, 0, 0), Vec3(0, 0, -1).normalize())
    hit1 = sphere.intersect(ray1)
    assert hit1.hit
    assert 3.5 < hit1.t < 4.5  # Deve estar próximo de 4 (5 - 1)
    print("  ✓ Raio frontal")

    # Raio que erra
    ray2 = Ray(Vec3(0, 0, 0), Vec3(1, 0, 0).normalize())
    hit2 = sphere.intersect(ray2)
    assert not hit2.hit
    print("  ✓ Raio que erra")

    # Raio dentro da esfera
    ray3 = Ray(Vec3(0, 0, -5), Vec3(0, 0, 1).normalize())
    hit3 = sphere.intersect(ray3, t_min=0, t_max=float('inf'))
    assert hit3.hit
    print("  ✓ Raio interno")

    print("✅ Todos os testes de interseção passaram!\n")


def test_colors():
    """Testa operações com cores"""
    print("🧪 Testando cores...")

    c1 = Color(0.5, 0.5, 0.5)
    c2 = Color(0.3, 0.3, 0.3)

    # Adição
    c3 = c1 + c2
    assert abs(c3.r - 0.8) < 0.001
    print("  ✓ Adição de cores")

    # Multiplicação
    c4 = c1 * 0.5
    assert abs(c4.r - 0.25) < 0.001
    print("  ✓ Multiplicação de cores")

    # Conversão RGB
    rgb = c1.to_rgb()
    assert rgb == (127, 127, 127)
    print("  ✓ Conversão para RGB")

    print("✅ Todos os testes de cores passaram!\n")


def test_scene_rendering():
    """Testa renderização simples"""
    print("🧪 Testando renderização...")

    # Cena simples
    scene = Scene()
    
    sphere = Sphere(Vec3(0, 0, -5), 1.0, Material(RED))
    scene.add_sphere(sphere)
    
    light = Light(Vec3(5, 5, 0), Color(1, 1, 1))
    scene.add_light(light)

    # Câmera
    camera = Camera(
        Vec3(0, 0, 0),
        Vec3(0, 0, -5),
        fov=60
    )

    # Renderiza um único pixel
    ray = camera.get_ray(0.5, 0.5)
    color = scene.trace_ray(ray)

    # Verifica se retorna uma cor válida
    assert 0 <= color.r <= 1
    assert 0 <= color.g <= 1
    assert 0 <= color.b <= 1
    print("  ✓ Ray tracing básico")

    # Renderiza imagem pequena
    tracer = RayTracer(width=100, height=75, samples=1)
    image = tracer.render(scene, camera)
    
    assert len(image) == 75
    assert len(image[0]) == 100
    print("  ✓ Renderização completa")

    print("✅ Todos os testes de renderização passaram!\n")


def test_camera():
    """Testa câmera"""
    print("🧪 Testando câmera...")

    camera = Camera(
        position=Vec3(0, 0, 0),
        look_at=Vec3(0, 0, -10),
        fov=90,
        aspect_ratio=16/9
    )

    # Centro da tela
    ray_center = camera.get_ray(0.5, 0.5)
    assert ray_center.origin == Vec3(0, 0, 0)
    print("  ✓ Raio do centro")

    # Diferentes posições
    ray_top = camera.get_ray(0.5, 0)
    ray_bottom = camera.get_ray(0.5, 1)
    ray_left = camera.get_ray(0, 0.5)
    ray_right = camera.get_ray(1, 0.5)

    # Direções devem ser diferentes
    assert ray_top.direction != ray_bottom.direction
    assert ray_left.direction != ray_right.direction
    print("  ✓ Raios em diferentes posições")

    print("✅ Todos os testes de câmera passaram!\n")


def test_shadows():
    """Testa detecção de sombras"""
    print("🧪 Testando sombras...")

    scene = Scene()

    # Esfera frontal
    front_sphere = Sphere(Vec3(0, 0, -5), 1.0, Material(RED))
    scene.add_sphere(front_sphere)

    # Esfera traseira
    back_sphere = Sphere(Vec3(0, 0, -10), 1.0, Material(BLUE))
    scene.add_sphere(back_sphere)

    # Luz que pode projetar sombra
    light = Light(Vec3(0, 5, 0), Color(1, 1, 1))
    scene.add_light(light)

    camera = Camera(Vec3(0, 0, 0), Vec3(0, 0, -7.5))

    # Ponto no meio das duas esferas
    ray = camera.get_ray(0.5, 0.5)
    color = scene.trace_ray(ray)

    # Não deve ser totalmente branco (há oclusão)
    assert color.r < 1.0 or color.g < 1.0 or color.b < 1.0
    print("  ✓ Sombras funcionando")

    print("✅ Todos os testes de sombra passaram!\n")


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("RAY TRACER - TESTES UNITÁRIOS")
    print("=" * 60)
    print()

    try:
        test_vec3_operations()
        test_ray_sphere_intersection()
        test_colors()
        test_camera()
        test_scene_rendering()
        test_shadows()

        print("=" * 60)
        print("✅ TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        return True

    except AssertionError as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
