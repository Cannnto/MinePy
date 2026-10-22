import glfw
from geometry import *


class Input():
    def __init__(self, window, camera, speed=200, sensitivity=0.1):
        self.window = window
        self.camera = camera

        # units per second
        self.speed = speed
        # degrees per pixel of mouse movement
        self.sensitivity = sensitivity

        self.last_x = 0
        self.last_y = 0
        # ignores the first mouse event, so the camera doesn't jump when the cursor enters the window
        self.first_mouse = True

        glfw.set_cursor_pos_callback(window, self.on_mouse_move)
        glfw.set_mouse_button_callback(window, self.on_mouse_button)
        glfw.set_key_callback(window, self.on_key)

        self.capture_mouse()

    # hides the cursor and locks it inside the window
    def capture_mouse(self):
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        self.first_mouse = True

    def release_mouse(self):
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def is_mouse_captured(self):
        return glfw.get_input_mode(self.window, glfw.CURSOR) == glfw.CURSOR_DISABLED

    # called by glfw every time the mouse moves
    def on_mouse_move(self, window, xpos, ypos):
        if not self.is_mouse_captured():
            return

        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        xoffset = (xpos - self.last_x) * self.sensitivity
        yoffset = (self.last_y - ypos) * self.sensitivity  # reversed: screen y grows downwards
        self.last_x = xpos
        self.last_y = ypos

        # the camera looks towards +Z, so turning right means decreasing the yaw
        self.camera.yaw -= xoffset
        self.camera.pitch += yoffset

        # at exactly 90 degrees the front is parallel to the world up and the right axis becomes zero
        self.camera.pitch = max(-89, min(89, self.camera.pitch))

    # clicking inside the window captures the mouse again
    def on_mouse_button(self, window, button, action, mods):
        if action == glfw.PRESS and not self.is_mouse_captured():
            self.capture_mouse()

    # called once per key press (not every frame)
    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            if self.is_mouse_captured():
                self.release_mouse()
            else:
                glfw.set_window_should_close(window, True)

    def is_pressed(self, key):
        return glfw.get_key(self.window, key) == glfw.PRESS

    # keys that are held down: checked every frame
    def update(self, dt):
        step = self.speed * dt
        cam = self.camera

        if self.is_pressed(glfw.KEY_W): cam.coord.selfAdd(cam.directionAxis.scalarMultiply(step))
        if self.is_pressed(glfw.KEY_S): cam.coord.selfSubtract(cam.directionAxis.scalarMultiply(step))
        if self.is_pressed(glfw.KEY_D): cam.coord.selfAdd(cam.rightAxis.scalarMultiply(step))
        if self.is_pressed(glfw.KEY_A): cam.coord.selfSubtract(cam.rightAxis.scalarMultiply(step))

        if self.is_pressed(glfw.KEY_SPACE):      cam.coord.selfAdd(cam.upVector.scalarMultiply(step))
        if self.is_pressed(glfw.KEY_LEFT_SHIFT): cam.coord.selfSubtract(cam.upVector.scalarMultiply(step))
