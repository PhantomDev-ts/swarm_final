# Ray Tracer - Do Zero em Python Puro

Um ray tracer implementado **completamente do zero** em Python puro, usando **apenas matemática vetorial**. Sem bibliotecas gráficas, sem CUDA, sem GPU — só álgebra linear e geometria.

## 🎯 Características

✅ **Renderização de Esferas** - Intersecção raio-esfera via equação quadrática  
✅ **Modelo de Iluminação Phong** - Ambiente, difusa e especular  
✅ **Sombras Realistas** - Shadow rays para detectar oclusões  
✅ **Reflexões** - Reflexão recursiva com limite de profundidade  
✅ **Anti-aliasing** - Múltiplas amostras por pixel  
✅ **Câmera Configurável** - FOV, aspect ratio, posição e orientação  
✅ **Saída em PPM e PNG** - Exporta imagens em formatos comuns  

## 📁 Estrutura do Projeto

```
raytracer/
├── geometry.py       # Vetores 3D, raios, esferas
├── materials.py      # Cores, materiais, propriedades
├── scene.py          # Gerenciamento de cena, iluminação
├── raytracer.py      # Motor de renderização, câmera
├── example.py        # Scripts de demonstração
└── __init__.py       # Módulo principal
```

## 🔬 Fundamentos Matemáticos

### 1. Geometria Vetorial

Todas as operações são baseadas em **operações vetoriais**:

```
Vetor: V = (x, y, z)

Adição:           V1 + V2 = (x1+x2, y1+y2, z1+z2)
Subtração:        V1 - V2 = (x1-x2, y1-y2, z1-z2)
Produto Escalar:  V1 · V2 = x1*x2 + y1*y2 + z1*z2
Produto Vetorial: V1 × V2 = (y1*z2-z1*y2, z1*x2-x1*z2, x1*y2-y1*x2)
Normalização:     V_norm = V / |V|
```

### 2. Interseção Raio-Esfera

Um raio é: **P(t) = O + t*D**
- O: origem
- D: direção (normalizada)
- t: distância

Uma esfera é: **(P - C)² = r²**
- C: centro
- r: raio

Substituindo P(t) na equação da esfera:

```
(O + t*D - C)² = r²
(O - C + t*D)² = r²
|O - C|² + 2t*(O - C)·D + t²|D|² = r²

at² + bt + c = 0

onde:
a = |D|²
b = 2(O - C)·D
c = |O - C|² - r²

Solução: t = (-b ± √(b² - 4ac)) / 2a
```

Se há duas soluções reais, o raio intersecta a esfera.

### 3. Iluminação - Modelo Phong

Cor final em cada pixel:

```
C_final = C_ambiente + Σ(luzes) [C_difusa + C_especular]

C_ambiente = C_objeto × L_ambiente × k_a

C_difusa = C_luz × max(0, N·L) × k_d
(N: normal na superfície, L: direção para luz)

C_especular = C_luz × max(0, R·V)^shininess × k_s
(R: reflexão de L, V: direção para câmera)
```

### 4. Sombras

Para cada ponto iluminado, traça um **raio de sombra** da superfície até a luz:
- Se o raio intersecta outro objeto antes de chegar à luz → **em sombra**
- Caso contrário → **iluminado**

### 5. Reflexão

Para superfícies reflexivas:

```
R = I - 2(I·N)N

Traça novo raio na direção R
Cor_final += Cor_reflexão × reflectivity
```

## 🚀 Uso Rápido

### Instalação

```bash
# Copie a pasta raytracer para seu projeto
cd raytracer
```

### Exemplo Básico

```python
from geometry import Vec3, Sphere
from materials import Color, Material, RED
from scene import Scene, Light
from raytracer import Camera, RayTracer

# 1. Cria cena
scene = Scene()

# 2. Adiciona objetos
sphere = Sphere(
    center=Vec3(0, 0, -5),
    radius=1.0,
    material=Material(color=RED)
)
scene.add_sphere(sphere)

# 3. Adiciona luzes
light = Light(
    position=Vec3(5, 5, 0),
    color=Color(1, 1, 1),
    intensity=1.0
)
scene.add_light(light)

# 4. Configura câmera
camera = Camera(
    position=Vec3(0, 0, 0),
    look_at=Vec3(0, 0, -5),
    fov=60
)

# 5. Renderiza
tracer = RayTracer(width=800, height=600, samples=4)
tracer.render(scene, camera)
tracer.save_png("output.png")
```

### Executar Demo

```bash
cd raytracer
python example.py
```

Gera dois arquivos:
- `output_scene1.png` - Cena com 3 esferas e múltiplas luzes
- `output_scene2.png` - Cena com reflexividade variável

## 📊 Classes Principais

### `Vec3(x, y, z)`

Vetor 3D com operações completas.

```python
v1 = Vec3(1, 2, 3)
v2 = Vec3(4, 5, 6)

v1 + v2           # Vec3(5, 7, 9)
v1.dot(v2)        # 32
v1.cross(v2)      # Produto vetorial
v1.normalize()    # Normaliza para |v| = 1
v1.length()       # Comprimento
```

### `Ray(origin, direction)`

Raio de luz: P(t) = origin + direction*t

```python
ray = Ray(Vec3(0, 0, 0), Vec3(0, 0, 1))
point = ray.point_at(5)  # Vec3(0, 0, 5)
```

### `Sphere(center, radius, material)`

Esfera com intersecção automática.

```python
sphere = Sphere(Vec3(0, 0, -5), 1.0, material)
hit = sphere.intersect(ray)
if hit.hit:
    print(f"Intersecção em t={hit.t}")
    print(f"Ponto: {hit.point}")
    print(f"Normal: {hit.normal}")
```

### `Material(color, ambient, diffuse, specular, shininess, reflectivity)`

Define propriedades de superfície.

```python
material = Material(
    color=Color(1, 0, 0),      # Vermelho
    ambient=0.1,                # 10% luz ambiente
    diffuse=0.7,                # 70% luz difusa
    specular=0.2,               # 20% especular
    shininess=32.0,             # Brilho
    reflectivity=0.1            # 10% reflexão
)
```

### `Scene()`

Gerencia objetos, luzes e iluminação.

```python
scene = Scene(ambient_light=Color(0.2, 0.2, 0.2))
scene.add_sphere(sphere)
scene.add_light(light)

color = scene.trace_ray(ray)  # Traça um raio
```

### `Camera(position, look_at, up, fov, aspect_ratio)`

Define câmera de renderização.

```python
camera = Camera(
    position=Vec3(0, 1, 2),
    look_at=Vec3(0, 0, -5),
    up=Vec3(0, 1, 0),
    fov=50,
    aspect_ratio=16/9
)

ray = camera.get_ray(0.5, 0.5)  # Raio para pixel (0.5, 0.5)
```

### `RayTracer(width, height, samples)`

Motor de renderização.

```python
tracer = RayTracer(1200, 900, samples=4)
image = tracer.render(scene, camera)
tracer.save_ppm("output.ppm")
tracer.save_png("output.png")  # Requer PIL
```

## 🎨 Paleta de Cores

Cores pré-definidas em `materials.py`:

```python
RED, GREEN, BLUE, WHITE, BLACK, GRAY
YELLOW, CYAN, MAGENTA, ORANGE, PURPLE
```

Materiais pré-definidos:
```python
MATTE_WHITE    # Branco fosco
SHINY_RED      # Vermelho brilhante
METAL          # Metal reflexivo (80% reflexão)
PLASTIC        # Plástico (10% reflexão)
```

## ⚙️ Algoritmo Principal

```
Para cada pixel (x, y):
    1. Cria raio da câmera (camera.get_ray)
    2. Traça raio na cena (scene.trace_ray)
       a. Encontra objeto mais próximo
       b. Se não acertou → retorna cor de fundo
       c. Se acertou:
          - Calcula iluminação (Phong)
          - Testa sombras (shadow rays)
          - Calcula reflexões (recursivamente)
    3. Armazena cor final no pixel
```

## 📈 Complexidade

| Operação | Complexidade |
|----------|-------------|
| Raios primários | O(N) onde N = pixels |
| Intersecção | O(M) onde M = objetos |
| Iluminação | O(L) por intersecção, L = luzes |
| Sombras | O(M*L) por intersecção |
| Total | O(N * M * L * profundidade) |

Para 800x600, 5 esferas, 3 luzes, profundidade 5: ~10-15 segundos

## 🔧 Parâmetros de Renderização

```python
# Qualidade vs. Performance
tracer = RayTracer(
    width=800,      # 1920 para Alta
    height=600,     # 1440 para Alta
    samples=4       # 16 para Máxima qualidade (lento)
)
```

- `samples=1`: Rápido, com aliasing
- `samples=4`: Bom balanço
- `samples=16`: Alto quality, muito lento

## 🚨 Limitações e Futuras Melhorias

### Limitações Atuais
- Apenas esferas (sem triângulos)
- Sem refração (transparency)
- Sem texturas
- Sem bump mapping
- Sem ray marching

### Possíveis Extensões
```python
# Objetos adicionais
class Plane:
    def intersect(ray):
        # Intersecção plano-raio
        pass

class Triangle:
    def intersect(ray):
        # Intersecção triângulo-raio (barycentric)
        pass

# Materiais avançados
class TransparentMaterial:
    def refract(ray, hit):
        # Lei de Snell
        pass

# Otimizações
class BVHTree:  # Bounding Volume Hierarchy
    def intersect(ray):
        # Aceleração espacial
        pass
```

## 📝 Exemplo Completo

Veja [example.py](example.py) para:
- Duas cenas completas
- Configurações de câmera
- Múltiplas luzes coloridas
- Diferentes materiais
- Exportação PNG/PPM

## 🎓 Referências Matemáticas

1. **Ray-Sphere Intersection**: Equação quadrática
2. **Phong Illumination Model**: Cook & Torrance
3. **Vector Mathematics**: 3D Graphics for Game Programming
4. **Shadow Rays**: Foley et al., Computer Graphics

## 📄 Licença

Livre para uso educacional e comercial.

---

**Criado com 💚 do zero em Python puro!**
