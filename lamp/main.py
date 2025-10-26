import machine
from machine import Pin, PWM, UART
from network import WLAN, STA_IF

import time

# 初期化処理
def initialize():
    global pir_sensor, pullup_input, buzzer_pwm, led_pwm, led_state, mode_led
    # GPIOピンの設定
    machine.freq(80_000_000)
    pir_sensor = Pin(0, Pin.IN, Pin.PULL_DOWN)  # PIRセンサ入力
    pullup_input = Pin(1, Pin.IN, Pin.PULL_UP)  # Pull-up付き入力
    buzzer_pwm = PWM(Pin(2))  # パッシブブザー用PWM出力
    led_pwm = PWM(Pin(10))  # LED用PWM出力
    mode_led = PWM(Pin(8))  # MODE_LED用PWM出力

    # PWMの設定
    buzzer_pwm.freq(2000)  # ブザー用PWM周波数（例: 2kHz）
    buzzer_pwm.duty_u16(0)  # 初期デューティサイクルを0に設定（音をOFF）
    led_pwm.freq(1000)  # LED用PWM周波数（1kHz）
    led_pwm.duty_u16(0)  # 初期デューティサイクルを0に設定
    mode_led.freq(1000)  # MODE_LED用PWM周波数（1kHz）
    mode_led.duty_u16(0xFFFF)  # 初期デューティサイクルを100%に設定

    # LEDの状態を保持する変数
    led_state = 0  # 0: 消灯, 1: 点灯

# LEDを光らせる関数
def set_led_brightness(brightness):
    """LEDの輝度を設定する（0~100%）"""
    duty = int((brightness / 100) * 65535)
    led_pwm.duty_u16(duty)

# ブザーを鳴らす関数
def play_buzzer(note, volume):
    """ブザーを鳴らす（音程: ドレミファソラシ, 音量: 0~100%）"""
    octave = 3  # オクターブ
    notes = {
        "ド": 262 * octave,
        "レ": 294 * octave,
        "ミ": 330 * octave,
        "ファ": 349 * octave,
        "ソ": 392 * octave,
        "ラ": 440 * octave,
        "シ": 494 * octave
    }
    if note in notes:
        buzzer_pwm.freq(notes[note])
        duty = int((volume / 100) * 65535)
        buzzer_pwm.duty_u16(duty)
    else:
        buzzer_pwm.duty_u16(0)  # 無効な音程の場合は音をOFF

def play_entry_melody():
    """入店音っぽいメロディーを再生"""
    melody = [
        ("ファ", 80, 0.14),  # (音程, 音量, 長さ[秒])
        ("ラ", 80, 0.14),
        ("ファ", 80, 0.14),
        ("ラ", 80, 0.14),
        ("ファ", 50, 0.14),
        ("ラ", 50, 0.14),
        ("ファ", 30, 0.14),
        ("ラ", 30, 0.14),
        (None, 0, 0.2),  # 休符
    ]
    for note, volume, duration in melody:
        play_buzzer(note, volume)
        time.sleep(duration)
    play_buzzer(None, 0)  # ブザーを停止

def play_exit_melody():
    """退店音っぽいメロディーを再生"""
    melody = [
        ("ファ", 80, 0.14),  # (音程, 音量, 長さ[秒])
        ("ラ", 80, 0.14),
        ("ファ", 80, 0.14),
        ("ラ", 80, 0.14),
        ("ファ", 50, 0.14),
        ("ラ", 50, 0.14),
        ("ファ", 30, 0.14),
        ("ラ", 30, 0.14),
        (None, 0, 0.2),  # 休符
    ]
    for note, volume, duration in melody:
        play_buzzer(note, volume)
        time.sleep(duration)
    play_buzzer(None, 0)  # ブザーを停止


# PIRセンサの状態を監視する関数
def monitor_pir_sensor():
    global led_state
    pir_high_start = None
    pir_low_start = None

    while True:
        pir_state = pir_sensor.value()

        if pir_state == 1:  # PIRセンサが1になった場合
            if pir_high_start is None:
                pir_high_start = time.ticks_ms()
            if pir_low_start is not None:
                pir_low_start = None  # LOW状態のタイマーをリセット

            # 10秒間継続したらLEDを点灯してブザーを鳴らす
            if time.ticks_diff(time.ticks_ms(), pir_high_start) >= 4000 and led_state == 0:
                set_led_brightness(80)  # LEDを点灯
                play_entry_melody()
                led_state = 1  # LEDを点灯状態に設定

        elif pir_state == 0:  # PIRセンサが0になった場合
            if pir_low_start is None:
                pir_low_start = time.ticks_ms()
            if pir_high_start is not None:
                pir_high_start = None  # HIGH状態のタイマーをリセット

            # 10秒間継続したらLEDを消灯してブザーを鳴らす
            if time.ticks_diff(time.ticks_ms(), pir_low_start) >= 10000 and led_state == 1:
                set_led_brightness(0)  # LEDを消灯
                play_exit_melody()
                play_buzzer(None, 0)  # ブザーを停止
                led_state = 0  # LEDを消灯状態に設定

        time.sleep(0.5)  # 100ms待機

# メイン処理
initialize()

# 起動時にPull-up付き入力が1だった場合、別モードに移行
if pullup_input.value() == 1:
    mode_led.duty_u16(0)    # MODE_LEDを点灯

else:
    # PIRセンサの監視を開始
    wlan = WLAN(STA_IF)
    wlan.active(False)
    monitor_pir_sensor()
