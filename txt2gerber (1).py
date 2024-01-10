import unidecode
import serial
from time import sleep

braille_dict = {
    'a': '100000',
    'b': '101000',
    'c': '110000',
    'd': '110100',
    'e': '100100',
    'f': '111000',
    'g': '111100',
    'h': '101100',
    'i': '011000',
    'j': '011100',
    'k': '100010',
    'l': '101010',
    'm': '110010',
    'n': '110110',
    'o': '100110',
    'p': '111010',
    'q': '111110',
    'r': '101110',
    's': '011010',
    't': '011110',
    'u': '100011',
    'v': '101011',
    'w': '011101',
    'x': '110011',
    'y': '110111',
    'z': '100111',
    'á': '001000',
    'é': '010110',
    'í': '011000',
    'ó': '010100',
    'ú': '011100',
    'ü': '100111',
    'ñ': '110110',
    '0': '001100',
    '1': '001000',
    '2': '001010',
    '3': '001110',
    '4': '001001',
    '5': '001101',
    '6': '001011',
    '7': '001111',
    '8': '001100',
    '9': '001100',
    ' ': '000000',
    ',': '010000',
    '.': '010110',
    '!': '011001',
    '?': '010010',
    ':': '010100',
    ';': '011100',
    '-': '010001',
    "'": '010011',
    '"': '010101',
    '(': '011011',
    ')': '011110',
    '/': '010111',
    '+': '011010',
    '=': '010111',
    '@': '011111',
    '#': '110001',
    '$': '110101',
    '%': '101001',
    '&': '111001',
    '*': '101101',
    '_': '011011',
    '|': '111101',
    '[': '111111',
    ']': '111110',
    '<': '101111',
    '>': '100001',
    '{': '101111',
    '}': '100001',
    '¡': '010011',
    '¿': '010010',
}



def texto_a_braille(texto):
    texto = unidecode.unidecode(texto.lower())
    resultado = ""
    ultimo_tipo = None

    for caracter in texto:
        if caracter in braille_dict:
            tipo_actual = 'letra' if caracter.isalpha() else 'numero'

            if ultimo_tipo is not None and tipo_actual != ultimo_tipo:
                resultado += ' '

            resultado += braille_dict[caracter] + ' '
            ultimo_tipo = tipo_actual

    return resultado.strip()


def text_to__braille_gcode(text,paperLimit=150):
    gcode_commands = []
    offsetX = 0
    offsetY = 0

    dot_positions = [
        (0, 0),
        (2.5, 0),
        (0, 2.5),
        (2.5, 2.5),
        (0, 5),
        (2.5, 5),
    ]

    for char in text:
      if(offsetX>paperLimit):
        offsetY += 10
        offsetX = 0
      braille_char = texto_a_braille(char)
      for i, dot in enumerate(braille_char):
        if dot == '1':
          dx, dy = dot_positions[i]
          x = offsetX+dx
          y = offsetY+dy
          gcode_commands.append(f'G1 Y{y} X{x} F5000')
          gcode_commands.append('M4 S100')
          gcode_commands.append('M4 S0')
      offsetX += 7


    gcode_commands.append('M84')    
    return gcode_commands

def write_to_serial_port(ser,string_to_write):
    try:
        string_to_write = string_to_write + "\n"
        ser.write(string_to_write.encode())
        
        print(string_to_write)
        
    except Exception as e:
        print(f'Error: {str(e)}')



input_text = """Diablo', qué safaera'
Tú tiene' un culo cabrón
Cualquier cosa que te pongas rompes la carretera (la-la-la-la-la)
Aight, muévelo, muévelo, muévelo, muévelo (la-la-la-la-la-la-la)
Qué safaera' (la-la-la-la-la)
Tú tiene' un culo cabrón
Cualquier cosa que te pongas rompes la carretera
Aight, (tra) muévelo, muévelo, muévelo, muévelo
Qué falta de respeto, mami
¿Cómo te atreve' a venir sin panty?
Hoy saliste puesta pa' mí
Yo que pensaba que venía a dormir, no
Vino ready ya, puesta pa' una cepillá'
Me chupa la lollipop, solita se arrodilla, hey
¿Cómo te atreve', mami, a venir sin panty?
"""
gcode_commands = text_to__braille_gcode(input_text)

port_name = "COM5" 
baud_rate = 250000  
ser = serial.Serial(port_name, baud_rate, timeout=1)
sleep(1)
write_to_serial_port(ser, "G90")
write_to_serial_port(ser, "M84")
write_to_serial_port(ser, "G28 X")
write_to_serial_port(ser, "G28 Y")
write_to_serial_port(ser, "G92 Y-30")
for comando in gcode_commands:
    write_to_serial_port(ser, comando)
    sleep(0.2)
ser.close()

# cadena = ";\n".join(gcode_commands)

# print((cadena))
