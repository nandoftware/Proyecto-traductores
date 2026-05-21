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


def find_column(content, token):
    last_newline = content.rfind('\n', 0, token.lexpos)

    if last_newline < 0:
        last_newline = -1

    return token.lexpos - last_newline


def t_COMMENT(t):
    r'\$-(.|\n)*?-\$'
    t.lexer.lineno += t.value.count('\n')
    pass


def t_TkCaracter(t):
    r"'[^'\n]'"
    t.value = t.value[1:-1]
    return t


def t_IDENTIFICATOR(t):
    r'[A-Za-z_]*'
    t.type = reserved.get(t.value, 'TkIdent')
    return t


def t_NUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    t.type = 'TkNum'
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    global errors
    column = find_column(t.lexer.lexdata, t)
    errors.append(
        f'Error: Caracter inesperado "{t.value[0]}" en la fila {t.lineno}, columna {column}'
    )
    t.lexer.skip(1)


lexer = lex.lex()


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