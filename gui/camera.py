import math
import pyrr
from pyrr import Matrix44, Vector4

class Camera:
    def __init__(self):
        self._pos = Vector4([0, 1, 4, 1])
        self.pitch = 0.0
        self.yaw = 10.0
        self.roll = 0.0
        self.dist = 4.0
        self.fovY = 45
        self.aspect_ratio = 1
        self.perspective = True
        self.zoom_speed = 0.2

    def pos(self):
        return self._pos

    def euler(self):
        roll = math.radians(self.roll)
        pitch = math.radians(self.pitch)
        yaw = math.radians(self.yaw)
        return pyrr.euler.create(pitch, roll, yaw)

    def rot(self):
        return Matrix44.from_eulers(self.euler())

    def view(self):
        view = Matrix44.from_translation(-self.pos())
        view = self.rot() * view
        view = Matrix44.from_translation([0.0, 0.0, -self.dist, 0.0]) * view
        return view

    def proj(self):
        if self.perspective:
            return Matrix44.perspective_projection(self.fovY, self.aspect_ratio, 0.1, 1000.0)
        else:
            length = math.tan(math.radians(self.fovY / 2)) * abs(self.dist)
            if self.aspect_ratio >= 1:
                return Matrix44.orthogonal_projection(-length * self.aspect_ratio, length * self.aspect_ratio, -length, length, 0.1, 1000.0)
            else:
                return Matrix44.orthogonal_projection(-length, length, -length / self.aspect_ratio, length / self.aspect_ratio, 0.1, 1000.0)

    def view_proj(self):
        return self.proj() * self.view()

    def dolly(self, d):
        self.dist -= d * self.zoom_speed

    def orbit(self, dx, dy):
        self.perspective = True
        self.yaw -= dx * 0.5
        self.pitch -= dy * 0.5

    def pan(self, dx, dy):
        pan_speed = 0.01
        dv = Vector4([dx * -pan_speed, dy * pan_speed, 0.0, 0.0])
        dv = self.rot().inverse * dv

        # Update _pos directly with extracted x, y, z components
        new_x = self._pos.x + dv.x
        new_y = self._pos.y + dv.y
        new_z = self._pos.z + dv.z

        # Set the updated position, ensuring w remains 1.0
        self._pos = Vector4([new_x, new_y, new_z, 1.0])

    def orthogonal(self, direct, ctrl):
        self.perspective = False
        self.yaw, self.pitch, self.roll = 0.0, 0.0, 0.0
        if direct == 1:
            self.yaw = 0.0 if not ctrl else 180.0
        elif direct == 3:
            self.yaw = 90.0 if not ctrl else -90.0
        elif direct == 7:
            self.pitch = -90.0 if not ctrl else 90.0

    def focus(self, point):
        self._pos = Vector4([point[0], point[1], point[2], 1.0])
        self.dist = 1.0

