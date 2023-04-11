#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Stop

BITE_DISTANCE = 100
WATCH_DISTANCE = 500


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

    def bite(self):
        self.body.run(0)
        self.neck.run(0)

        self.mouth.run_until_stalled(300)
        self.mouth.run_until_stalled(-300, then=Stop.HOLD)

        self.neck.run(0)
        self.neck.run(150)
        self.body.run_time(-300, 1000, then=Stop.BRAKE)
        self.neck.run(-150)
        self.body.run_time(-300, 1000, then=Stop.BRAKE)
        self.neck.run(0)

    def is_watching(self):
        return self.eyes.distance() < WATCH_DISTANCE

    def is_bite_distance(self):
        return self.eyes.distance() < BITE_DISTANCE

    def cycle(self):
        self.mouth.run_until_stalled(150)
        self.mouth.reset_angle(0)
        mouth_open = 0
        mouth_closed = self.mouth.run_until_stalled(-150, then=Stop.HOLD)

        self.neck.run_time(200, 1000, then=Stop.BRAKE)
        leftmost_neck = self.neck.angle()
        self.neck.run_time(-200, 1000, then=Stop.BRAKE)
        rightmost_neck = self.neck.angle()

        cycle_neck_direction = "left"
        while True:
            print(self.eyes.distance())
            neck_speed = 100

            if self.is_watching():
                neck_speed = 0

            if self.is_bite_distance():
                self.bite()

            self.body.run(300)
            if cycle_neck_direction == "left":
                if abs(self.neck.angle() - leftmost_neck) <= 30:
                    cycle_neck_direction = "right"
                else:
                    self.neck.run(neck_speed)
            if cycle_neck_direction == "right":
                if abs(self.neck.angle() - rightmost_neck) <= 30:
                    cycle_neck_direction = "left"
                else:
                    self.neck.run(-neck_speed)


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
