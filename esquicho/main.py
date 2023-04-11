#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port


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

    def cycle(self):
        self.neck.run_until_stalled(-150)
        self.neck.reset_angle(0)
        neck_inside = 0
        neck_outside = self.neck.run_until_stalled(150)

        while True:
            print(self.neck.angle(), neck_inside, neck_outside)
            if self.eyes.distance() < 100:
                self.left_leg.stop()
                self.right_leg.stop()
                if abs(self.neck.angle() - neck_inside) > 50:
                    self.neck.run_target(-150, neck_inside, wait=False)
            else:
                if abs(self.neck.angle() - neck_outside) > 50:
                    self.neck.run_target(150, neck_outside, wait=False)
                self.left_leg.run(150)
                self.right_leg.run(150)


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
