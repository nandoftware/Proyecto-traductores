import sys
import ply.lex as lex


if len(sys.argv) < 2:
    print("uso: ./LexBot <ruta del archivo>")
    sys.exit(1)

file_name: str = sys.argv[1]

errors = []
tokens = [
    'TkCreate', 'TkWhile', 'TkBool', 'TkIf', 'TkInt', 'TkBot',
    'TkOn', 'TkActivation', 'TkStore', 'TkEnd', 'TkExecute',
    'TkActivate', 'TkTrue', 'TkFalse',

    'TkIdent', 'TkNum', 'TkCaracter',

    'TkComa', 'TkPunto', 'TkDosPuntos',
    'TkParAbre', 'TkParCierra',

    'TkSuma', 'TkResta', 'TkMult', 'TkDiv', 'TkMod',
    'TkConjuncion', 'TkDisyuncion', 'TkNegacion',
    'TkMenorIgual', 'TkMayorIgual',
    'TkMenor', 'TkMayor', 'TkIgual'
]

reserved = {
    'create': 'TkCreate',
    'while': 'TkWhile',
    'bool': 'TkBool',
    'if': 'TkIf',
    'int': 'TkInt',
    'bot': 'TkBot',
    'on': 'TkOn',
    'activation': 'TkActivation',
    'store': 'TkStore',
    'end': 'TkEnd',
    'execute': 'TkExecute',
    'activate': 'TkActivate',
    'true': 'TkTrue',
    'false': 'TkFalse'
}

t_TkComa = r'\,'
t_TkPunto = r'\.'
t_TkDosPuntos = r'\:'
t_TkParAbre = r'\('
t_TkParCierra = r'\)'

t_TkSuma = r'\+'
t_TkResta = r'\-'
t_TkMult = r'\*'
t_TkMod = r'\%'
t_TkConjuncion = r'/\\'
t_TkDisyuncion = r'\\/'
t_TkNegacion = r'∼'
t_TkMenorIgual = r'<='
t_TkMayorIgual = r'>='
t_TkMenor = r'<'
t_TkMayor = r'>'
t_TkIgual = r'='
t_TkDiv = r'/'

t_ignore = ' \t'

# una funcion rapidita para obtener la columna
def find_column(content, token):
    last_newline = content.rfind('\n', 0, token.lexpos)

    if last_newline < 0:
        last_newline = -1

    return token.lexpos - last_newline

# todas las funciones con el prefijo t_ sirven para que el lexer entienda:
# los comentarios, los caracteres solitos, las palabras redervadas y los numeros

def t_COMMENT(t):
    r'\$-(.|\n)*?-\$'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_TkCaracter(t):
    r"'[^'\n]'"
    t.value = t.value[1:-1]
    return t


def t_IDENTIFICATOR(t):
    r'[A-Za-z]+'
    t.type = reserved.get(t.value, 'TkIdent')
    return t


def t_NUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    t.type = 'TkNum'
    return t

# despues esta la funcion de deteccion de errores del lexer 

def t_error(t):
    global errors
    column = find_column(t.lexer.lexdata, t)
    errors.append(
        f'Error: Caracter inesperado "{t.value[0]}" en la fila {t.lineno}, columna {column}'
    )
    t.lexer.skip(1)

# y por ultimo este cosito que a veces el lexer lo hace solo y otras veces no

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

lexer = lex.lex()

# la funcion parser extrae los tokens de un archivo de texto
# proximamente solo de los .bot
# devuelve todos los tokens en el formato que imagino sera provisional
def Parser():
    global errors
    errors = []
    content: str

    try:
        # with cierra el archivo automaticamente
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()

    except FileNotFoundError:
        print(f"no se pudo encontrar '{file_name}'")
        sys.exit(1)
    except Exception as e:
        print(f"{e}")
        sys.exit(1)

    lexer.lineno = 1
    lexer.input(content)

    minitokens = []

    for tok in lexer:
        colum = find_column(content, tok)
        mini = ""

        if tok.type == 'TkIdent':
            mini += f'{str(tok.type)}("{tok.value}") {str(tok.lineno)} {str(colum)}'
            minitokens.append(mini)

        elif tok.type == 'TkNum':
            mini += f'{str(tok.type)}({tok.value}) {str(tok.lineno)} {str(colum)}'
            minitokens.append(mini)

        elif tok.type == 'TkCaracter':
            mini += f"{str(tok.type)}('{tok.value}') {str(tok.lineno)} {str(colum)}"
            minitokens.append(mini)

        else:
            mini += f"{str(tok.type)} {str(tok.lineno)} {str(colum)}"
            minitokens.append(mini)

    return minitokens


if __name__ == '__main__':
    resultado = Parser()

    if errors:
        for error in errors:
            print(error)
    else:
        print(', '.join(resultado))