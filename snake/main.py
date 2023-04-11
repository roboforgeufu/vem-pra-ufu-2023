#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Stop


class Snake:
    def __init__(
        self,
        eyes_port: Port,
        mouth_port: Port,
        body_port: Port,
        neck_port: Port,
    ) -> None:
        self.brick = EV3Brick()
        self.eyes = UltrasonicSensor(eyes_port)
        self.mouth = Motor(mouth_port)
        self.body = Motor(body_port)
        self.neck = Motor(neck_port)

    def cycle(self):
        self.mouth.run_until_stalled(150)
        self.mouth.reset_angle(0)
        mouth_open = 0
        mouth_closed = self.mouth.run_until_stalled(-150, then=Stop.HOLD)

        self.neck.run_time(200, 1000, then=Stop.BRAKE)
        leftmost_neck = self.neck.angle()
        self.neck.run_time(-200, 1000, then=Stop.BRAKE)
        rightmost_neck = self.neck.angle()

        print(leftmost_neck, rightmost_neck)

        cycle_neck_direction = "left"
        while True:
            self.body.run(300)
            if cycle_neck_direction == "left":
                if abs(self.neck.angle() - leftmost_neck) <= 30:
                    cycle_neck_direction = "right"
                else:
                    self.neck.run(150)
            if cycle_neck_direction == "right":
                if abs(self.neck.angle() - rightmost_neck) <= 30:
                    cycle_neck_direction = "left"
                else:
                    self.neck.run(-150)


def main():
    snake = Snake(
        eyes_port=Port.S4,
        mouth_port=Port.C,
        body_port=Port.A,
        neck_port=Port.B,
    )
    snake.cycle()


if __name__ == "__main__":
    main()
