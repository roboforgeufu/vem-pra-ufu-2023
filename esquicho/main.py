#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Color, Port


class Turtle:
    def __init__(
        self,
        eyes_port: Port,
        right_leg_port: Port,
        left_leg_port: Port,
        neck_port: Port,
    ) -> None:
        self.brick = EV3Brick()
        self.eyes = UltrasonicSensor(eyes_port)
        self.right_leg = Motor(right_leg_port)
        self.left_leg = Motor(left_leg_port)
        self.neck = Motor(neck_port)

        self.neck_inside = None
        self.neck_outside = None

    def hide(self, dir_multiplier=1):
        if dir_multiplier == 1:
            self.brick.light.on(Color.RED)
        else:
            self.brick.light.on(Color.GREEN)
        self.neck.run_until_stalled(-300 * dir_multiplier)

    def is_hidden(self):
        if self.neck_inside is None:
            raise ValueError("neck values not set")
        return abs(self.neck.angle() - self.neck_inside) < 20

    def cycle(self):
        self.neck.run_until_stalled(-150)
        self.neck.reset_angle(0)
        self.neck_inside = 0
        self.neck_outside = self.neck.run_until_stalled(150)

        while True:
            if self.is_hidden():
                # Distancia assustado
                distance = 200
            else:
                # Distancia explorando
                distance = 100

            if self.eyes.distance() < distance:
                self.left_leg.stop()
                self.right_leg.stop()
                self.hide()
            else:
                self.hide(-1)
                self.left_leg.run(180)
                self.right_leg.run(180)


def main():
    esguicho = Turtle(
        eyes_port=Port.S1,
        right_leg_port=Port.A,
        left_leg_port=Port.D,
        neck_port=Port.B,
    )
    esguicho.cycle()


if __name__ == "__main__":
    main()
