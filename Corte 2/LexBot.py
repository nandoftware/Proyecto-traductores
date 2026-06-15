#!/usr/bin/env python3
import sys
import ply.lex as lex
import ply.yacc as yacc


if len(sys.argv) < 2:
    print("uso: ./LexBot <ruta del archivo>")
    sys.exit(1)

# Encapsulamiento de la lectura del archivo .bot
def ReadBotFile(file_name: str):
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

    return content

###############################################################################################
## -------------- tokens y funciones t_ usadas por el analizador lexicografico-------------- ##
###############################################################################################

errors = []
tokens = [
    'TkCreate', 'TkWhile', 'TkBool', 'TkIf', 'TkInt', 'TkBot',
    'TkOn', 'TkActivation', 'TkDefault', 'TkStore', 'TkEnd', 'TkExecute',
    'TkActivate', 'TkTrue', 'TkFalse',

    'TkIdent', 'TkNum', 'TkCaracter',

    'TkComa', 'TkPunto', 'TkDosPuntos',
    'TkParAbre', 'TkParCierra',

    'TkSuma', 'TkResta', 'TkMult', 'TkDiv', 'TkMod',
    'TkConjuncion', 'TkDisyuncion', 'TkNegacion',
    'TkMenorIgual', 'TkMayorIgual',
    'TkMenor', 'TkMayor', 'TkIgual', 'TkNoIgual'
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
    'default' : 'TkDefault',
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



# la funcion parser extrae los tokens de un archivo de texto
# proximamente solo de los .bot
# devuelve todos los tokens en el formato que imagino sera provisional
def Tokenaizer():
    
    content = ReadBotFile(sys.argv[1])

    lexer.lineno = 1
    lexer.input(content)

    minitokens = ""

    for tok in lexer:
        minitokens += str(tok.value) + " "
        # colum = find_column(content, tok)
        # mini = ""

        # if tok.type == 'TkIdent':
        #     mini += f'{str(tok.type)}("{tok.value}") {str(tok.lineno)} {str(colum)}'
        #     minitokens.append(mini)

        # elif tok.type == 'TkNum':
        #     mini += f'{str(tok.type)}({tok.value}) {str(tok.lineno)} {str(colum)}'
        #     minitokens.append(mini)

        # elif tok.type == 'TkCaracter':
        #     mini += f"{str(tok.type)}('{tok.value}') {str(tok.lineno)} {str(colum)}"
        #     minitokens.append(mini)

        # else:
        #     mini += f"{str(tok.type)} {str(tok.lineno)} {str(colum)}"
        #     minitokens.append(mini)

    return minitokens



###################################################################################################
## ------------------------------- producciones de la gramatica -------------------------------- ##
###################################################################################################

##############################
##  BOT -> CREATE EXECUTE   ##
##       | lambda           ##
##############################
def p_bot(p):
    'BOT : CREATE EXECUTE'
    p[0] = (p[1],p[2])
    
    
    
def p_bot_empty(p):
    'BOT : empty'


######################################
##  CREATE -> TkCreate DEFINITION   ##
##          | lambda                ##
######################################
def p_create(p):
    'CREATE : TkCreate DEFINITION'
    p[0] = (p[1],p[2])
    

def p_create_empty(p):
    'CREATE : empty'
    

############################################################
##  DEFINITION -> TkInt TkBot TkIdent DECLARATION TkEnd   ##
##              | lambda                                  ##
############################################################
def p_definition_int(p):
    'DEFINITION : TkInt TkBot TkIdent DECLARATION TkEnd'
    p[0] = (p[1], p[3], p[4])
    

def p_definition_empty(p):
    'DEFINITION : empty'
    

#######################################################################
##  DECLARATION -> TkOn TkActivation TkDosPuntos INSTRUCTION TkEnd   ##
##               | TkOn TkDefault TkDosPuntos INSTRUCTION TkEnd      ##
##               | lambda                                            ##
#######################################################################
def p_declaration_activation(p):
    'DECLARATION : TkOn TkActivation TkDosPuntos INSTRUCTION TkEnd'
    p[0] = (p[2], p[4])
    

def p_declaration_default(p):
    'DECLARATION : TkOn TkDefault TkDosPuntos INSTRUCTION TkEnd'
    p[0] = (p[2], p[4])
    

def p_declaration_empty(p):
    'DECLARATION : empty'


#####################################################
##  INSTRUCTION -> TkStore TkNum TkPunto           ##
##               | TkActivate TkIdent TkPunto      ##
#####################################################
def p_instruction_store(p):
    'INSTRUCTION : TkStore TkNum TkPunto INSTRUCTION'
    p[0] = (p[1], p[2])
    

def p_instruction_activate(p):
    'INSTRUCTION : TkActivate TkIdent TkPunto INSTRUCTION'
    p[0] = (p[1], p[2])


def p_instruction_if(p):
    'INSTRUCTION : Tkif EXP_BINARIA TkDosPuntos INSTRUCTION TkEnd'
    p[0] = (p[1], p[2], p[4])


def p_instruction_while(p):
    'INSTRUCTION : TkWhile EXP_BINARIA TkDosPuntos INSTRUCTION TkEnd'
    p[0] = (p[1], p[2], p[4])


def p_exp_binaria_suma(p):
    'EXP_BINARIA : EXP_BINARIA TkSuma EXP_BINARIA'
    p[0] = p[1] + p[3]

def p_exp_binaria_resta(p):
    'EXP_BINARIA : EXP_BINARIA TkResta EXP_BINARIA'
    p[0] = p[1] - p[3]

def p_exp_binaria_mult(p):
    'EXP_BINARIA : EXP_BINARIA TkMult EXP_BINARIA'
    p[0] = p[1] * p[3]
    
def p_exp_binaria_div(p):
    'EXP_BINARIA : EXP_BINARIA TkDiv EXP_BINARIA'
    p[0] = p[1] / p[3]


def p_exp_binaria_mod(p):
    'EXP_BINARIA : EXP_BINARIA TkMod EXP_BINARIA'
    p[0] = p[1] % p[3]


def p_exp_binaria_conj(p):
    'EXP_BINARIA : EXP_BINARIA TkConjuncion EXP_BINARIA'
    p[0] = p[1] and p[3]


def p_exp_binaria_disj(p):
    'EXP_BINARIA : EXP_BINARIA TkDisyuncion EXP_BINARIA'
    p[0] = p[1] or p[3]

    
def p_exp_binaria_igual(p):
    'EXP_BINARIA : EXP_BINARIA TkIgual EXP_BINARIA'
    p[0] = p[1] == p[3]

def p_exp_binaria_menorI(p):
    'EXP_BINARIA : EXP_BINARIA TkMenorIgual EXP_BINARIA'
    p[0] = p[1] <= p[3]

def p_exp_binaria_mayorI(p):
    'EXP_BINARIA : EXP_BINARIA TkMayorIgual EXP_BINARIA'
    p[0] = p[1] >= p[3]

def p_exp_binaria_menor(p):
    'EXP_BINARIA : EXP_BINARIA TkMenor EXP_BINARIA'
    p[0] = p[1] < p[3]

def p_exp_binaria_mayor(p):
    'EXP_BINARIA : EXP_BINARIA TkMayor EXP_BINARIA'
    p[0] = p[1] > p[3]

def p_exp_binaria_paren(p):
    'EXP_BINARIA : TkParAbre EXP_BINARI TkParCierra'
    p[0] = p[2]

def p_exp_binaria_num(p):
    'EXP_BINARIA : TkNum'
    p[0] = p[1]

def p_exp_binaria_boolt(p):
    'EXP_BINARIA : TkTrue'
    p[0] = p[1]

def p_exp_binaria_boolf(p):
    'EXP_BINARIA : TkFalse'
    p[0] = p[1]

def p_exp_binaria_var(p):
    'EXP_BINARIA : TkIdent'
    p[0] = p[1]

def p_exp_unaria(p):
    'EXP_UNARI : TkNegacion EXP_BINARIA'
    p[0] = not p[2]

def p_instruction_empty(p):
    'INSTRUCTION : empty'


##############################################
##  EXECUTE -> TkExecute INSTRUCTION TkEnd  ##
##############################################
def p_execute(p):
    'EXECUTE : TkExecute INSTRUCTION TkEnd'
    p[0] = (p[1], p[2])
    


#######################
##  empty production ##
#######################
def p_empty(p):
    'empty :'
    pass


# y la de los errores que es temporal asi
def p_error(p):
    print("syntax error")
    print(p)


class node():
    def __init__(self, father, children):
        self.father = father
        self.children = children

    def __str__(self):
        return f"padre: {self.father}, hijos: {self.children}"

class instrutions(node):
    def __init__(self,  father, children, nomIns, var, ):
        self.father = father
        self.children = children
        self.nomIns = nomIns
        self.var = var

    def __str__(self):
        return f"{self.nomIns}\n\t var: {self.var}\n"
        
    

if __name__ == '__main__':
    lexer = lex.lex()
    resultado = Tokenaizer()

    yc = yacc.yacc()

    if errors:
        for error in errors:
            print(error)
    # else:
        # print(', '.join(resultado))
        # print(resultado)


    AST = yc.parse(resultado)
    
    print(AST)