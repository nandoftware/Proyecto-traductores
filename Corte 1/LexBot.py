import sys
import ply.lex as lex


if len(sys.argv) < 2:
    print("uso: ./LexBot <ruta del archivo>")
    sys.exit(1)

file_name:str = sys.argv[1]

errors = [];
tokens=[
    'TkCreate', 'TkInt', 'TkBot', 'TkIdent', 'TkNum', 'TkCaracter',
    'TkComa', 'TkPunto', 'TkDosPuntos', 'TkParAbre', 'TkParCierra',
    'TkSuma', 'TkResta', 'TkMult', 'TkDiv', 'TkMod', 'TkConjuncion', 'TkDisyuncion', 'TkNegacion', 'TkMenor', 'TkMenorIgual', 'TkMayor', 'TkMayorIgual', 'TkIgual'
]

t_TkComa = r'\,'
t_TkPunto = r'\.'
t_TkDosPuntos = r'\:'
t_TkParAbre = r'\('
t_TkParCierra = r'\)'

t_TkSuma = r'\+'
t_TkResta = r'\-'
t_TkMult = r'\*'
t_TkDiv = r'/'
t_TkMod = r'\%'
t_TkConjuncion = r'/\\'
t_TkDisyuncion = r'\\/'
t_TkNegacion = r'∼'
t_TkMenor = r'<'
t_TkMenorIgual = r'<='
t_TkMayor = r'>'
t_TkMayorIgual = r'>='
t_TkIgual = r'='



def t_IDENTIFICATOR(t):
    r'[A-Za-z]+'
    if t.value == 'int':
        t.type = 'TkInt'
    elif t.value == 'create':
        t.type = 'TkCreate'
    elif t.value == 'bot':
        t.type = 'TkBot'
    else:
        t.type = 'TkIdent'
    return t

def t_NUM(t):
    r'[0-9]+' 
    try:
        t.value = int(t.value)
    except:
        print("error de algun tipo")
    t.type = 'TkNum'
    return t

def t_error(t):
    global errors
    errors.append(f"simbolo no valido '{t.value[0]}' en la linea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()
def Parser():
    content: str

    try:
        # with cierra el archivo automaticamente
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()
            
    except FileNotFoundError:
        print(f"no se puedo encontrar '{file_name}'")
    except Exception as e:
        print(f"{e}")

    

    lexer.input(content)

    minitokens = []

    lexer.lineno = 1
    for tok in lexer:
        colum = tok.lexpos - content.rfind('\n', 0, tok.lexpos)
        mini = ""
        if(tok.type != 'TkIdent' and tok.type != 'TkNum'):
            
            mini += f"{str(tok.type)} {str(tok.lineno)} {str(colum)}"  
            minitokens.append(mini)
        else:
            
            mini += f"{str(tok.type)}(\"{tok.value}\") {str(tok.lineno)} {str(colum)}"  
            minitokens.append(mini)

    return minitokens

if __name__ == '__main__':
    print(Parser())