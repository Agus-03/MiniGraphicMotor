import numpy as np
import glm
from hit import HitBox, HitBoxOBB
from model import Vertex, VertexLayout, Model

class Sphere(Model):
    def __init__(self, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1),
                 name="sphere", animated=True, sector_count=32, stack_count=16, hittable = True):
        """
        Crea una esfera paramétrica.
        sector_count -> número de divisiones en longitud (horizontal)
        stack_count  -> número de divisiones en latitud (vertical)
        """
        self.name = name
        self.animated = animated
        self.position = glm.vec3(*position)
        self.rotation = glm.vec3(*rotation)
        self.scale = glm.vec3(*scale)
        self.__colision = HitBoxOBB(get_model_matrix = lambda: self.get_model_matrix(), hittable = hittable)

        vertices_pos = []
        vertices_color = []
        indices = []

        # Generar vértices y colores en tonos de rosa
        for i in range(stack_count + 1):
            stack_angle = np.pi / 2 - i * np.pi / stack_count  # de +pi/2 a -pi/2
            xy = np.cos(stack_angle)
            z = np.sin(stack_angle)

            for j in range(sector_count + 1):
                sector_angle = j * 2 * np.pi / sector_count

                x = xy * np.cos(sector_angle)
                y = xy * np.sin(sector_angle)

                # Colores: tono de rosa basado en la altura (z)
                # R ≈ 1, G ≈ 0.3-0.6, B ≈ 0.5-0.7
                r = 1.0
                g = 0.3 + 0.3 * (z + 1) / 2
                b = 0.5 + 0.2 * (z + 1) / 2

                vertices_pos.extend([x, y, z])
                vertices_color.extend([r, g, b])

        # Generar índices para formar triángulos
        for i in range(stack_count):
            k1 = i * (sector_count + 1)
            k2 = k1 + sector_count + 1

            for j in range(sector_count):
                if i != 0:
                    indices.extend([k1 + j, k2 + j, k1 + j + 1])
                if i != (stack_count - 1):
                    indices.extend([k1 + j + 1, k2 + j, k2 + j + 1])

        super().__init__(
            vertices = np.array(vertices_pos, dtype="f4"),
            indices = np.array(indices, dtype="i4"),
            colors = np.array(vertices_color, dtype="f4")
        )

    @property
    def aabb(self):
        ##pos_vertex = self.vertex_layout.get_attributes()[0]
        ##vertices_array = pos_vertex.array
        ##verts3 = vertices_array.reshape(-1,3)
        pos_attr = next(attr for attr in self.vertex_layout.get_attributes() if attr.name == "in_pos")
        verts3 = pos_attr.array.reshape(-1, 3)
        pts = [self.get_model_matrix() * glm.vec4(v[0], v[1], v[2], 1.0) for v in verts3]
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]
        zs = [p.z for p in pts]
        return (glm.vec3(min(xs), min(ys), min(zs)),
                glm.vec3(max(xs), max(ys), max(zs)))

    def check_hit(self, origin, direction):
        return self.__colision.check_hit(origin, direction)
    def get_model_matrix(self):
        model = glm.mat4(1)
        model = glm.translate(model, self.position)
        model = glm.rotate(model, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        model = glm.rotate(model, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        model = glm.rotate(model, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        model = glm.scale(model, self.scale)
        return model
