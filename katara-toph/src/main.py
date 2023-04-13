#!/usr/bin/env pybricks-micropython
import time

from pybricks.parameters import Button, Color, Port
from pybricks.tools import DataLog, wait
import constants as const
from robot import Robot

from pybricks.messaging import (
    BluetoothMailboxClient,
    BluetoothMailboxServer,
    LogicMailbox,
    NumericMailbox,
)

from utils import (
    PIDValues,
    ev3_print,
    get_hostname,
    normalize_color,
    wait_button_pressed,
)


def input_objetivo(ev3_brick):

    objetivo = None
    while True:
        buttons = ev3_brick.buttons.pressed()

        if Button.LEFT in buttons:
            objetivo = Color.RED
        elif Button.RIGHT in buttons:
            objetivo = Color.YELLOW
        
        ev3_brick.light.on(objetivo)

        if Button.CENTER in buttons:
            break
    
    return objetivo


def double_check_color(robot: Robot):

    color_left = robot.accurate_color(robot.color_l.rgb())
    color_right = robot.accurate_color(robot.color_r.rgb())

    if color_left == color_right:
        return color_left
    else:
        robot.pid_walk(cm=10, vel=-40)
        robot.forward_while_same_reflection(50, 50, 20)


def vem_pra_ufu_toph():
    toph = Robot(
        wheel_diameter=const.WHEEL_DIAMETER,
        wheel_distance=const.WHEEL_DIST,
        motor_claw=Port.A,
        motor_r=Port.C,
        motor_l=Port.B,
        ultra_front=Port.S1,
        color_l=Port.S2,
        color_r=Port.S3,
        turn_correction=0.9,
        color_max_value=110,
        debug=True,
    )

    # conexao entre os bricks por bluetooth
    toph.ev3_print(get_hostname())
    server = BluetoothMailboxServer()
    toph.ev3_print("SERVER: waiting for connection...")
    server.wait_for_connection()
    toph.ev3_print("SERVER: connected!")

    # espera a katara sair da meeting area
    # antes de comecar a rotina de localizacao
    logic_mbox = LogicMailbox("start", server)

    # espera a katara falar q conectou
    logic_mbox.wait()
    logic_mbox.send(True)

    #
    objetivo = input_objetivo(toph.brick)
    color = None

    dist = toph.ultra_front.distance()
    dist = max(1, dist - 5)
    toph.move_to_distance(50, sensor=toph.ultra_front, max_cm=35)
    toph.pid_walk(cm=8, vel=20)
    toph.off_motors()
    toph.motor_claw.reset_angle(0)
    toph.motor_claw.run_target(300, const.CLAW_UP)

    while True:
        toph.forward_while_same_reflection(50, 50, 20)
        toph.pid_walk(cm=1, vel=40)
        toph.pid_align(PIDValues(target=70, kp=0.5, ki=0.002, kd=0.1))
        toph.pid_walk(cm=4, vel=40)
        color = double_check_color(toph)
        if color == objetivo:
            break
        if color == Color.RED or color == Color.YELLOW:
            toph.forward_while_same_reflection(50, 50, 20)
            toph.pid_walk(cm=15, vel=-40)
            toph.pid_turn(90)
            toph.forward_while_same_reflection(50, 50, 20)
            toph.pid_walk(cm=5, vel=40)
            continue
        toph.pid_walk(cm=15, vel=-40)
        toph.pid_turn(90)
    
    toph.forward_while_same_reflection(50, 50, 20)

    if objetivo == Color.YELLOW:
        toph.pid_walk(cm=15, vel=-60)
        toph.pid_turn(-90)
        toph.forward_while_same_reflection(50, 50, 20)
        toph.pid_walk(cm=10, vel=-60)
        toph.pid_turn(90)
        logic_mbox.send(False)
        toph.motor_claw.run_target(300, const.CLAW_DOWN)
        toph.pid_walk(cm=30, vel=-60)
        toph.pid_turn(-90)
        toph.pid_walk(cm=30, vel=-40)
        toph.pid_turn(-90)

    elif objetivo == Color.RED:
        toph.pid_walk(cm=10, vel=-60)
        toph.pid_turn(-90)
        toph.forward_while_same_reflection(50, 50, 20)
        toph.pid_walk(cm=15, vel=-60)
        logic_mbox.send(True)
        toph.motor_claw.run_target(300, const.CLAW_DOWN)
        toph.pid_walk(cm=30, vel=-60)
        toph.pid_turn(90)
        toph.pid_walk(cm=30, vel=-40)
        toph.pid_turn(90)


def vem_pra_ufu_katara():
    katara = Robot(
                wheel_diameter=const.WHEEL_DIAMETER,
                wheel_distance=const.WHEEL_DIST,
                motor_r=Port.C,
                motor_l=Port.B,
                motor_claw=Port.A,
                color_l=Port.S1,
                color_r=Port.S2,
                ultra_front=Port.S4,
                debug=True,
                turn_correction=const.KATARA_TURN_CORRECTION,
                color_max_value=65,
            )

    katara.ev3_print(get_hostname())
    client = BluetoothMailboxClient()
    katara.ev3_print("CLIENT: establishing connection...")
    client.connect(const.SERVER)
    katara.ev3_print("CLIENT: connected!")

    katara.ev3_print("1")
    logic_mbox = LogicMailbox("start", client)
    katara.ev3_print("2")
    # Confirma conexão (sync)
    logic_mbox.send(True)
    katara.ev3_print("3")
    # Espera confirmação da Toph
    logic_mbox.wait()

    while True:
        katara.forward_while_same_reflection(50, 50, 20)
        katara.pid_walk(cm=1, vel=40)
        katara.pid_align(PIDValues(target=30, kp=0.5, ki=0.002, kd=0.1))
        katara.pid_walk(cm=4, vel=40)
        if (
            katara.color_l.reflection() > 0
            and katara.color_l.reflection() < 10
            and katara.color_r.reflection() > 0
            and katara.color_r.reflection() < 10
        ):
            break
        katara.pid_walk(cm=15, vel=-40)
        katara.pid_turn(90)
 
    katara.pid_walk(cm=15, vel=-40)
    logic_mbox.wait()
    var = logic_mbox.read()

    # True = RED, False = YELLOW
    if var:
        multiplier = -1

    katara.pid_turn(multiplier * 90)
    katara.forward_while_same_reflection(50, 50, 20)
    katara.pid_walk(cm=1, vel=40)
    katara.pid_align(PIDValues(target=30, kp=0.5, ki=0.002, kd=0.1))
    katara.pid_walk(cm=15, vel=-40)
    katara.pid_turn(multiplier * (-90))
    katara.forward_while_same_reflection(50, 50, 20)
    katara.pid_walk(cm=5, vel=40)
    katara.forward_while_same_reflection(50, 50, 20)
    katara.pid_walk(cm=20, vel=40)
    katara.pid_turn(multiplier * 90)
    katara.forward_while_same_reflection(50, 50, 20)
    katara.pid_walk(cm=1, vel=40)
    katara.pid_align(PIDValues(target=30, kp=0.5, ki=0.002, kd=0.1))
    katara.pid_walk(cm=10, vel=-40)
    katara.pid_turn(multiplier * (-90))


if __name__ == "__main__":
    vem_pra_ufu_toph()
