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
syntax_error = None
tokens = [
    'TkCreate', 'TkWhile', 'TkBool', 'TkIf', 'TkInt', 'TkBot',
    'TkOn', 'TkActivation', 'TkDeactivation', 'TkDefault', 'TkStore', 'TkEnd', 'TkExecute',
    'TkActivate', 'TkDeactivate', 'TkTrue', 'TkFalse', 'TkElse',
    'TkAdvance', 'TkCollect', 'TkAs', 'TkDrop', 'TkRead', 'TkSend',
    'TkLeft', 'TkRight', 'TkUp', 'TkDown',

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
    'else': 'TkElse',
    'int': 'TkInt',
    'char': 'TkCaracter',
    'bot': 'TkBot',
    'on': 'TkOn',
    'activation': 'TkActivation',
    'deactivation': 'TkDeactivation',
    'default' : 'TkDefault',
    'store': 'TkStore',
    'end': 'TkEnd',
    'execute': 'TkExecute',
    'activate': 'TkActivate',
    'deactivate': 'TkDeactivate',
    'true': 'TkTrue',
    'false': 'TkFalse',
    'advance':'TkAdvance',
    'collect': 'TkCollect',
    'as': 'TkAs',
    'drop': 'TkDrop',
    'read': 'TkRead',
    'send': 'TkSend',
    'left': 'TkLeft',
    'right': 'TkRight',
    'up': 'TkUp',
    'down': 'TkDown',
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
t_TkNoIgual = r'!='

t_ignore = ' \t'

# una funcion rapidita para obtener la columna
def find_column(content, token):
    last_newline = content.rfind('\n', 0, token.lexpos)

    if last_newline < 0:
        last_newline = -1

    return token.lexpos - last_newline

# todas las funciones con el prefijo t_ sirven para que el lexer entienda:
# los comentarios, los caracteres solitos, las palabras redervadas y los numeros

def t_COMMENT_LINE(t):
    r'\$\$[^\n]*'
    pass

def t_COMMENT(t):
    r'\$-(.|\n)*?-\$'
    t.lexer.lineno += t.value.count('\n')
    pass

def t_TkCaracter(t):
    r"'(\\n|\\t|\\'|[^'\n])'"
    t.value = t.value[1:-1]
    return t

def t_TkIdent(t):
    r'[A-Za-z]+'
    t.type = reserved.get(t.value, 'TkIdent')
    return t

def t_TkNum(t):
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
def Tokenaizer():
    
    content = ReadBotFile(sys.argv[1])

    lexer.lineno = 1
    lexer.input(content)

    minitokens = []

    for tok in lexer:
        mini = ""
        colum = find_column(content, tok)
        if tok.type == 'TkIdent':
            mini += f'{str(tok.type)}("{tok.value}") {str(tok.lineno)} {str(colum)}'
        

        elif tok.type == 'TkNum':
            mini += f'{str(tok.type)}({tok.value}) {str(tok.lineno)} {str(colum)}'
       
        elif tok.type == 'TkCaracter':
            mini += f"{str(tok.type)}('{tok.value}') {str(tok.lineno)} {str(colum)}"

        else:
            mini += f"{str(tok.type)} {str(tok.lineno)} {str(colum)}"
        minitokens.append(mini)

    return minitokens

###################################################################################################
## ------------------------------- clases del arbol sintactico -------------------------------- ##
###################################################################################################

class node():
    def __init__(self, father=None, children=None):
        self.father = father
        self.children = children or []

    def __str__(self):
        return f"padre: {self.father}, hijos: {self.children}"

    def imprimir(self, nivel=0):
        return str(self)

def tab(nivel):
    return "  " * nivel

class Secuenciacion(node):
    def __init__(self, instrucciones):
        super().__init__('SECUENCIACION', instrucciones)
        self.instrucciones = instrucciones

    def imprimir(self, nivel=0):
        if len(self.instrucciones) == 0:
            return ""
        if len(self.instrucciones) == 1:
            return self.instrucciones[0].imprimir(nivel)

        texto = tab(nivel) + "SECUENCIACION\n"
        for instruccion in self.instrucciones:
            texto += instruccion.imprimir(nivel + 1)
        return texto

class instrutions(node):
    def __init__(self, father=None, children=None, nomIns='', var=None):
        super().__init__(father, children or [])
        self.nomIns = nomIns
        self.var = var

    def __str__(self):
        return f"{self.nomIns}\n\t var: {self.var}\n"

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + f"{self.nomIns}\n" +
            tab(nivel) + f"- var: {self.var}\n"
        )
    

class Almacenamiento(node):
    def __init__(self, valor):
        super().__init__('ALMACENAMIENTO', [valor])
        self.valor = valor

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + "ALMACENAMIENTO\n" +
            tab(nivel) + "- valor:\n" +
            self.valor.imprimir(nivel + 1)
        )
    

class InstruccionRobot(node):
    # Estas instrucciones se construyen para el AST, pero no se muestran como salida.
    def __init__(self, nombre, valor=None):
        super().__init__(nombre, [] if valor is None else [valor])
        self.nombre = nombre
        self.valor = valor

    def imprimir(self, nivel=0):
        return ""
    

class Condicional(node):
    def __init__(self, guardia, exito):
        super().__init__('CONDICIONAL', [guardia, exito])
        self.guardia = guardia
        self.exito = exito

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + "CONDICIONAL\n" +
            tab(nivel) + "- guardia:\n" +
            self.guardia.imprimir(nivel + 1) +
            tab(nivel) + "- exito:\n" +
            self.exito.imprimir(nivel + 1)
        )
    

class RepeticionIndeterminada(node):
    def __init__(self, guardia, cuerpo):
        super().__init__('REPETICION_INDETERMINADA', [guardia, cuerpo])
        self.guardia = guardia
        self.cuerpo = cuerpo

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + "REPETICION_INDETERMINADA\n" +
            tab(nivel) + "- guardia:\n" +
            self.guardia.imprimir(nivel + 1) +
            tab(nivel) + "- cuerpo:\n" +
            self.cuerpo.imprimir(nivel + 1)
        )
    

class Valor(node):
    def __init__(self, valor):
        super().__init__('VALOR', [])
        self.valor = valor

    def imprimir(self, nivel=0):
        return tab(nivel) + str(self.valor) + "\n"
    

class Binaria(node):
    def __init__(self, tipo, operacion, izquierda, derecha):
        super().__init__(tipo, [izquierda, derecha])
        self.tipo = tipo
        self.operacion = operacion
        self.izquierda = izquierda
        self.derecha = derecha

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + self.tipo + "\n" +
            tab(nivel) + f"- operacion: '{self.operacion}'\n" +
            tab(nivel) + "- operador izquierdo:\n" +
            self.izquierda.imprimir(nivel + 1) +
            tab(nivel) + "- operador derecho:\n" +
            self.derecha.imprimir(nivel + 1)
        )
    

class Unaria(node):
    def __init__(self, operacion, expresion):
        super().__init__('EXP_UNARIA', [expresion])
        self.operacion = operacion
        self.expresion = expresion

    def imprimir(self, nivel=0):
        return (
            tab(nivel) + "EXP_UNARIA\n" +
            tab(nivel) + f"- operacion: '{self.operacion}'\n" +
            tab(nivel) + "- expresion:\n" +
            self.expresion.imprimir(nivel + 1)
        )




###################################################################################################
## ------------------------------- producciones de la gramatica -------------------------------- ##
###################################################################################################

# Precedencia y asociatividad para resolver conflictos de intereses de expresiones JAJAJAJAJ

precedence = (
    ('left', 'TkDisyuncion'),
    ('left', 'TkConjuncion'),
    ('right', 'TkNegacion'),
    ('nonassoc', 'TkIgual', 'TkNoIgual', 'TkMenor', 'TkMenorIgual', 'TkMayor', 'TkMayorIgual'),
    ('left', 'TkSuma', 'TkResta'),
    ('left', 'TkMult', 'TkDiv', 'TkMod'),
)



##############################
##  BOT -> [CREATE] EXECUTE   ##
##       | lambda           ##
##############################
def p_bot(p):
    'BOT : CREATE EXECUTE'
    p[0] = p[2]


# def p_bot_nc(p):
#     'BOT : EXECUTE'
#     p[0] = p[2]
    
######################################
##  CREATE -> TkCreate DEFINITION   ##
##          | lambda                ##
######################################
def p_create(p):
    'CREATE : TkCreate DECLARATIONS'
    p[0] = (p[1],p[2])

def p_create_empty(p):
    'CREATE : empty'
    p[0] = None
    

############################################################
##  DECLARATIONS -> TkInt TkBot TkIdent ACTIONS TkEnd   ##
##              | lambda                                  ##
############################################################
def p_definition_recursive(p):
    'DECLARATIONS : DECLARATIONS TYPE TkBot IDENT_LIST ACTIONS TkEnd'
    p[0] = (p[1], p[2], p[4], p[5])
    
def p_definition_one(p):
    'DECLARATIONS : TYPE TkBot IDENT_LIST ACTIONS TkEnd'
    p[0] = (p[1], p[3], p[4])

def p_definition_empty(p):
    'DECLARATIONS : empty'
    p[0] = None

def p_type(p):
    '''TYPE : TkInt
            | TkBool
            | TkCaracter'''
    p[0] = p[1]

def p_id_list_one(p):
    'IDENT_LIST : TkIdent'
    p[0] = [p[1]]


def p_id_list_recursive(p):
    'IDENT_LIST : IDENT_LIST TkComa TkIdent'
    p[1].append(p[3])
    p[0] = p[1]
    
#######################################################################
##  ACTIONS -> ACTIONS EVENT | EVENT | lambda                ##
#######################################################################
def p_action(p):
    'ACTIONS : ACTIONS TkOn CONDITION TkDosPuntos INSTRUCTION TkEnd'
    p[0] = None


# def p_action(p):
#     'ACTIONS : EVENT'
#     p[0] = None


def p_action_empty(p):
    'ACTIONS : empty'
    p[0] = None

def p_condition_activation(p):
    'CONDITION : TkActivation'
    p[0] = None
    
def p_condition_deactivation(p):
    'CONDITION : TkDeactivation'
    p[0] = None
    
def p_condition_deafault(p):
    'CONDITION : EXP_BINARIA'
    p[0] = None
    
def p_condition_exp(p):
    'CONDITION : TkDefault'
    p[0] = None


# def p_event_activation(p):
#     'EVENT : TkOn TkActivation TkDosPuntos INSTRUCTION TkEnd'
#     p[0] = p[4]

# def p_event_deactivation(p):
#     'EVENT : TkOn TkDeactivation TkDosPuntos INSTRUCTION TkEnd'
#     p[0] = p[4]

# def p_event_default(p):
#     'EVENT : TkOn TkDefault TkDosPuntos INSTRUCTION TkEnd'
#     p[0] = p[4]

# def p_event_expr(p):
#     'EVENT : TkOn EXP_BINARIA TkDosPuntos INSTRUCTION TkEnd'
#     p[0] = p[4]


#####################################################
##  INSTRUCTION -> lista de instrucciones           ##
#####################################################
def p_instruction_recursive(p):
    'INSTRUCTION : INSTRUCTION SIMPLE_INSTRUCTION'
    if isinstance(p[1], Secuenciacion):
        p[1].instrucciones.append(p[2])
        p[0] = p[1]
    elif p[1] is None:
        p[0] = p[2]
    else:
        p[0] = Secuenciacion([p[1], p[2]])


def p_instruction_simple(p):
    'INSTRUCTION : SIMPLE_INSTRUCTION'
    p[0] = p[1]


def p_instruction_empty(p):
    'INSTRUCTION : empty'
    p[0] = Secuenciacion([])


def p_simple_instruction_store(p):
    'SIMPLE_INSTRUCTION : TkStore EXP_BINARIA TkPunto'
    p[0] = Almacenamiento(p[2])

def p_simple_instruction_collect(p):
    '''SIMPLE_INSTRUCTION : TkCollect TkPunto
                          | TkCollect TkAs TkIdent TkPunto'''
    p[0] = InstruccionRobot('COLECCION')

def p_simple_instruction_drop(p):
    'SIMPLE_INSTRUCTION : TkDrop EXP_BINARIA TkPunto'
    p[0] = InstruccionRobot('SOLTADO', p[2])

def p_direction(p):
    '''DIRECTION : TkLeft
                 | TkRight
                 | TkUp
                 | TkDown'''
    p[0] = p[1]

def p_simple_instruction_read(p):
    '''SIMPLE_INSTRUCTION : TkRead TkPunto
                          | TkRead TkAs TkIdent TkPunto'''
    p[0] = InstruccionRobot('ENTRADA')


def p_simple_instruction_send(p):
    'SIMPLE_INSTRUCTION : TkSend TkPunto'
    p[0] = InstruccionRobot('SALIDA')


def p_simple_instruction_move(p):
    '''SIMPLE_INSTRUCTION : DIRECTION TkPunto
                          | DIRECTION EXP_BINARIA TkPunto'''
    p[0] = InstruccionRobot('MOVIMIENTO')


def p_simple_instruction_activate(p):
    'SIMPLE_INSTRUCTION : TkActivate IDENT_LIST TkPunto'
    p[0] = instrutions('ACTIVACION', [], 'ACTIVACION', p[2])

def p_simple_instruction_deactivate(p):
    'SIMPLE_INSTRUCTION : TkDeactivate IDENT_LIST TkPunto'
    p[0] = instrutions('DEACTIVACION', [], 'DEACTIVACION', p[2])

def p_simple_instruction_advance(p):
    'SIMPLE_INSTRUCTION : TkAdvance IDENT_LIST TkPunto'
    p[0] = instrutions('AVANCE', [], 'AVANCE', p[2])


def p_simple_instruction_if(p):
    'SIMPLE_INSTRUCTION : TkIf EXP_BINARIA TkDosPuntos INSTRUCTION TkEnd'
    p[0] = Condicional(p[2], p[4])

def p_simple_instruction_if_else(p):
    'SIMPLE_INSTRUCTION : TkIf EXP_BINARIA TkDosPuntos INSTRUCTION TkElse TkDosPuntos INSTRUCTION TkEnd'
    p[0] = Condicional(p[2], Secuenciacion([p[4], p[7]]))


def p_simple_instruction_while(p):
    'SIMPLE_INSTRUCTION : TkWhile EXP_BINARIA TkDosPuntos INSTRUCTION TkEnd'
    p[0] = RepeticionIndeterminada(p[2], p[4])

def p_simple_instruction_scope(p):
    'SIMPLE_INSTRUCTION : CREATE EXECUTE'
    p[0] = p[2]



##############################################
##  EXECUTE -> TkExecute INSTRUCTION TkEnd  ##
##############################################
def p_execute(p):
    'EXECUTE : TkExecute INSTRUCTION TkEnd'
    p[0] = p[2]


################################################
##  Expresiones binarias, unarias y atomicas   ##
################################################
def p_exp_binaria_operador(p):
    '''EXP_BINARIA : EXP_BINARIA TkSuma EXP_BINARIA
                   | EXP_BINARIA TkResta EXP_BINARIA
                   | EXP_BINARIA TkMult EXP_BINARIA
                   | EXP_BINARIA TkDiv EXP_BINARIA
                   | EXP_BINARIA TkMod EXP_BINARIA
                   | EXP_BINARIA TkConjuncion EXP_BINARIA
                   | EXP_BINARIA TkDisyuncion EXP_BINARIA
                   | EXP_BINARIA TkIgual EXP_BINARIA
                   | EXP_BINARIA TkNoIgual EXP_BINARIA
                   | EXP_BINARIA TkMenorIgual EXP_BINARIA
                   | EXP_BINARIA TkMayorIgual EXP_BINARIA
                   | EXP_BINARIA TkMenor EXP_BINARIA
                   | EXP_BINARIA TkMayor EXP_BINARIA'''
    operaciones = {
        '+': ('BIN_ARITMETICA', 'Suma'),
        '-': ('BIN_ARITMETICA', 'Resta'),
        '*': ('BIN_ARITMETICA', 'Multiplicacion'),
        '/': ('BIN_ARITMETICA', 'Division'),
        '%': ('BIN_ARITMETICA', 'Modulo'),
        '/\\': ('BIN_BOOLEANA', 'Conjuncion'),
        '\\/': ('BIN_BOOLEANA', 'Disyuncion'),
        '=': ('BIN_RELACIONAL', 'Igual que'),
        '/=': ('BIN_RELACIONAL', 'Distinto que'),
        '<=': ('BIN_RELACIONAL', 'Menor o igual que'),
        '>=': ('BIN_RELACIONAL', 'Mayor o igual que'),
        '<': ('BIN_RELACIONAL', 'Menor que'),
        '>': ('BIN_RELACIONAL', 'Mayor que')
    }

    tipo, operacion = operaciones[p[2]]
    p[0] = Binaria(tipo, operacion, p[1], p[3])


def p_exp_binaria_paren(p):
    'EXP_BINARIA : TkParAbre EXP_BINARIA TkParCierra'
    p[0] = p[2]


def p_exp_unaria_negacion(p):
    'EXP_BINARIA : TkNegacion EXP_BINARIA'
    p[0] = Unaria('Negacion', p[2])


def p_exp_unaria_resta(p):
    'EXP_BINARIA : TkResta EXP_BINARIA %prec TkNegacion'
    p[0] = Unaria('Menos unario', p[2])


def p_exp_binaria_num(p):
    'EXP_BINARIA : TkNum'
    p[0] = Valor(p[1])


def p_exp_binaria_boolt(p):
    'EXP_BINARIA : TkTrue'
    p[0] = Valor('true')


def p_exp_binaria_boolf(p):
    'EXP_BINARIA : TkFalse'
    p[0] = Valor('false')


def p_exp_binaria_var(p):
    'EXP_BINARIA : TkIdent'
    p[0] = Valor(p[1])


def p_exp_binaria_char(p):
    'EXP_BINARIA : TkCaracter'
    p[0] = Valor("'" + p[1] + "'")

#######################
##  empty production ##
#######################
def p_empty(p):
    'empty :'
    pass


# Error sintactico: se guarda solo el primero, como pide el enunciado.
def p_error(p):
    global syntax_error

    if syntax_error is not None:
        return

    if p:
        column = find_column(p.lexer.lexdata, p)
        syntax_error = f'Error sintactico en la fila {p.lineno}, columna {column}: token inesperado "{p.value}"'
    else:
        syntax_error = 'Error sintactico: fin inesperado del archivo'


parser = yacc.yacc()


if __name__ == '__main__':
    content = ReadBotFile(sys.argv[1])

    # Primera pasada: detectar todos los errores lexicos.
    lexer.lineno = 1
    lexer.input(content)
    while lexer.token():
        pass

    if errors:
        for error in errors:
            print(error)
        sys.exit(1)

    # Segunda pasada: si no hubo errores lexicos, se analiza sintacticamente.
    lexer.lineno = 1
    AST = parser.parse(content, lexer=lexer)

    if syntax_error:
        print(syntax_error)
        sys.exit(1)

    if AST:
        print(AST.imprimir(), end='')
