# Stability-Setup
Stability Tester for Perovskite Devices Summer 2022 JP lab

https://www.ti.com/lit/ds/symlink/ina219.pdf

https://cdn-shop.adafruit.com/datasheets/mcp4725.pdf

https://docs.arduino.cc/resources/datasheets/A000066-datasheet.pdf

[Git Command Line no Login](https://stackoverflow.com/questions/35942754/how-can-i-save-username-and-password-in-git#35942890)

https://forum.arduino.cc/t/serial-input-basics-updated/382007

https://www.electroschematics.com/simple-microampere-meter-circuit/

https://www.eevblog.com/forum/beginners/reading-micro-amp-current-output-of-a-sensor/

https://training.ti.com/ti-precision-labs-current-sense-amplifiers-current-sensing-different-types-amplifiers?context=1139747-1139745-1138708-1139729-1138709



Traceback (most recent call last):
  File "c:\Users\achen\Dropbox\code\Stability-Setup\readArduinoData_auto.py", line 107, in <module>
    scan(VOLTAGE_RANGE, VOLTAGE_STEP_SIZE, VOLTAGE_READ_COUNT, "backward")
  File "c:\Users\achen\Dropbox\code\Stability-Setup\readArduinoData_auto.py", line 87, in scan
    if ser.in_waiting > 0:
  File "C:\Users\achen\anaconda3\envs\stabilitySetup\lib\site-packages\serial\serialwin32.py", line 259, in in_waiting
    raise SerialException("ClearCommError failed ({!r})".format(ctypes.WinError()))
serial.serialutil.SerialException: ClearCommError failed (OSError(22, 'The I/O operation has been aborted because of either a thread exit or an application request.', None, 995))
PS C:\Users\achen\Dropbox\code\Stability-Setup>