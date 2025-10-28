from bytelang.compiler import ByteLangCompiler
from bytelang.tools.string import FixedStringIO

bytelang = ByteLangCompiler.simpleSetup(r"A:\Projects\Vertical-Art-Robot-Technology\Code\VART-DesktopApp\res\bytelang")

SOURCE = """
.env vart_esp32

delay_ms 1000

set_planner_mode 0x02
set_speed 100
set_accel 75

set_active_tool 0x00
set_position 100 100

set_active_tool 0x01
set_position -250 250
set_position -250 -250
set_position 250 -250
set_position 250 250

set_active_tool 0x00
set_position 0 0

delay_ms 1000

quit    
"""

with open("out.blc", "wb") as bytecode_stream:
    result = bytelang.compile(FixedStringIO(SOURCE), bytecode_stream)
    print(result.getMessage())

with open("out.blc", "rb") as bytecode_stream:
    print(", ".join((
        f"0x{v:02X}"
        for v in bytecode_stream.read()
    )))
