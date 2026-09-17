#!/usr/bin/env python3
import sys
import ply.lex as lex
import ply.yacc as yacc

if len(sys.argv) < 2:
    print("uso: ./bot <ruta del archivo>")
    sys.exit(1)

def ReadBotFile(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"no se pudo encontrar '{file_name}'")
        sys.exit(1)
    except Exception as error:
        print(error)
        sys.exit(1)

###############################################################################################
## -------------- tokens y funciones t_ usadas por el analizador lexicografico-------------- ##
###############################################################################################

errors, context_errors = [], []
syntax_error = None
current_robot_type, current_robot_items = None, []
inside_behavior = 0

tokens = [
    'TkCreate','TkWhile','TkBool','TkMe','TkIf','TkInt','TkBot','TkOn',
    'TkActivation','TkDeactivation','TkDefault','TkStore','TkEnd','TkExecute',
    'TkActivate','TkDeactivate','TkTrue','TkFalse','TkElse','TkAdvance',
    'TkCollect','TkAs','TkDrop','TkRead','TkSend','TkLeft','TkRight','TkUp','TkDown',
    'TkIdent','TkNum','TkCaracter','TkComa','TkPunto','TkDosPuntos','TkParAbre',
    'TkParCierra','TkSuma','TkResta','TkMult','TkDiv','TkMod','TkConjuncion',
    'TkDisyuncion','TkNegacion','TkMenorIgual','TkMayorIgual','TkMenor',
    'TkMayor','TkIgual','TkNoIgual'
]

reserved = {
    'create':'TkCreate','while':'TkWhile','bool':'TkBool','me':'TkMe','if':'TkIf',
    'else':'TkElse','int':'TkInt','char':'TkCaracter','bot':'TkBot','on':'TkOn',
    'activation':'TkActivation','deactivation':'TkDeactivation','default':'TkDefault',
    'store':'TkStore','end':'TkEnd','execute':'TkExecute','activate':'TkActivate',
    'deactivate':'TkDeactivate','true':'TkTrue','false':'TkFalse','advance':'TkAdvance',
    'collect':'TkCollect','as':'TkAs','drop':'TkDrop','read':'TkRead','send':'TkSend',
    'left':'TkLeft','right':'TkRight','up':'TkUp','down':'TkDown'
}

t_TkComa=r'\,'; t_TkPunto=r'\.'; t_TkDosPuntos=r'\:'
t_TkParAbre=r'\('; t_TkParCierra=r'\)'; t_TkSuma=r'\+'; t_TkResta=r'\-'
t_TkMult=r'\*'; t_TkMod=r'\%'; t_TkConjuncion=r'/\\'; t_TkDisyuncion=r'\\/'
t_TkNegacion=r'∼'; t_TkMenorIgual=r'<='; t_TkMayorIgual=r'>='
t_TkMenor=r'<'; t_TkMayor=r'>'; t_TkIgual=r'='; t_TkDiv=r'/'; t_TkNoIgual=r'/='
t_ignore=' \t'

def find_column(content, token):
    last = content.rfind('\n', 0, token.lexpos)
    return token.lexpos - (-1 if last < 0 else last)

def t_COMMENT_LINE(t):
    r'\$\$[^\n]*'
    pass

def t_COMMENT(t):
    r'\$-(.|\n)*?-\$'
    t.lexer.lineno += t.value.count('\n')

def t_TkCaracter(t):
    r"'(\\n|\\t|\\'|[^'\n])'"
    raw=t.value[1:-1]
    t.value={'\\n':'\n','\\t':'\t',"\\'":"'"}.get(raw,raw)
    return t

def t_TkIdent(t):
    r'\b[a-zA-Z]\w*\b'
    t.type=reserved.get(t.value,'TkIdent')
    return t

def t_TkNum(t):
    r'[0-9]+'
    t.value=int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    errors.append(f'Error: Caracter inesperado "{t.value[0]}" en la fila {t.lineno}, columna {find_column(t.lexer.lexdata,t)}')
    t.lexer.skip(1)

lexer=lex.lex()

###############################################################################################
## ------------------------------- cosas de la tabla de simbolos ---------------------------- ##
###############################################################################################

tam, c_a, c_b = 97, 3, 2

def hash_function(value):
    return (c_a*sum(ord(char) for char in value)+c_b)%tam

class TS_item:
    def __init__(self,name,token,tp,value=None,is_robot=False):
        self.name=name; self.token=token; self.type=tp; self.value=value
        self.is_robot=is_robot; self.conditions=[]; self.active=False; self.position=[0,0]

class TS:
    def __init__(self,parent):
        self.simbolos=[None]*tam; self.padre=parent

def FindSlot(name,table,for_insert=False):
    start=hash_function(name)
    for offset in range(tam):
        key=(start+offset)%tam; item=table.simbolos[key]
        if item is None: return key if for_insert else None
        if item.name==name: return key
    return None

def InsertSimbol(name,tp,table,is_robot=False):
    key=FindSlot(name,table,True)
    if key is not None and table.simbolos[key] is not None:
        ContextError(f'redeclaracion de la variable "{name}" en el mismo alcance')
        return None
    if key is None:
        ContextError('la tabla de simbolos esta llena'); return None
    item=TS_item(name,'TkIdent',tp,None,is_robot); table.simbolos[key]=item
    return item

def LookupSimbol(name,table):
    while table is not None:
        key=FindSlot(name,table)
        if key is not None: return table.simbolos[key]
        table=table.padre
    return None

def ContextError(message,line=None):
    context_errors.append(f'Error de contexto: {message}'+(f', linea: {line}' if line else ''))

def RequireType(expression,expected,where,line=None):
    if expression.tipo not in ('error',expected):
        ContextError(f'{where} requiere tipo {expected}, pero recibio {expression.tipo}',line)
        return False
    return expression.tipo==expected

TS_program=TS(None)

###############################################################################################
## ------------------------------- clases del arbol sintactico ------------------------------ ##
###############################################################################################

class DynamicError(Exception): pass
def DynamicFail(message): raise DynamicError(f'Error dinamico: {message}')

def type_of(value):
    if isinstance(value,bool): return 'bool'
    if isinstance(value,int): return 'int'
    if isinstance(value,str) and len(value)==1: return 'char'
    return None

def printable(value):
    return 'true' if value is True else 'false' if value is False else str(value)

def read_typed_value(expected):
    raw=input()
    if expected=='int':
        try: return int(raw)
        except ValueError: DynamicFail('lectura inadecuada')
    if expected=='bool':
        if raw=='true': return True
        if raw=='false': return False
        DynamicFail('lectura inadecuada')
    if expected=='char' and len(raw)==1: return raw
    DynamicFail('lectura inadecuada')

class Runtime:
    def __init__(self): self.matrix={}
    def event_behavior(self,robot,event):
        return next((b for b in robot.conditions if b.condition==event),None)
    def run_behavior(self,robot,behavior):
        for symbol in behavior.local_symbols: symbol.value=None
        behavior.body.correr(self,robot)
    def activate(self,robot):
        if robot.active: DynamicFail(f'activacion ilegal del robot "{robot.name}"')
        robot.active=True; behavior=self.event_behavior(robot,'activation')
        if behavior: self.run_behavior(robot,behavior)
    def deactivate(self,robot):
        if not robot.active: DynamicFail(f'desactivacion ilegal del robot "{robot.name}"')
        behavior=self.event_behavior(robot,'deactivation')
        if behavior: self.run_behavior(robot,behavior)
        robot.active=False
    def advance(self,robot):
        if not robot.active: DynamicFail(f'avance ilegal del robot inactivo "{robot.name}"')
        default=None
        for behavior in robot.conditions:
            if behavior.condition in ('activation','deactivation'): continue
            if behavior.condition=='default': default=behavior; continue
            if behavior.condition.evaluar(self,robot): self.run_behavior(robot,behavior); return
        if default: self.run_behavior(robot,default); return
        DynamicFail(f'comportamiento inexistente para el robot "{robot.name}"')

class node:
    def __init__(self,father=None,children=None): self.father=father; self.children=children or []
    def imprimir(self,nivel=0): return str(self)

def tab(nivel): return '  '*nivel

class Secuenciacion(node):
    def __init__(self,instrucciones):
        super().__init__('SECUENCIACION',instrucciones); self.instrucciones=instrucciones
    def correr(self,runtime,robot=None):
        for instruction in self.instrucciones: instruction.correr(runtime,robot)
    def imprimir(self,nivel=0):
        if len(self.instrucciones)==1: return self.instrucciones[0].imprimir(nivel)
        return tab(nivel)+'SECUENCIACION\n'+''.join(i.imprimir(nivel+1) for i in self.instrucciones)

class instrutions(node):
    def __init__(self,name,robots):
        super().__init__(name,[]); self.nomIns=name; self.robots=robots; self.var=[r.name for r in robots]
    def correr(self,runtime,robot=None):
        for target in self.robots:
            {'ACTIVACION':runtime.activate,'DEACTIVACION':runtime.deactivate,'AVANCE':runtime.advance}[self.nomIns](target)
    def imprimir(self,nivel=0): return tab(nivel)+self.nomIns+'\n'+tab(nivel)+f'- var: {self.var}\n'

class InstruccionRobot(node):
    def __init__(self,name,value=None,target=None,direction=None):
        super().__init__(name,[] if value is None else [value])
        self.nombre=name; self.valor=value; self.target=target; self.direction=direction
    def correr(self,runtime,robot=None):
        if robot is None: DynamicFail(f'la instruccion {self.nombre} requiere un robot')
        if self.nombre=='store':
            value=self.valor.evaluar(runtime,robot)
            if type_of(value)!=robot.type: DynamicFail(f'almacenamiento inadecuado en el robot "{robot.name}"')
            robot.value=value
        elif self.nombre=='collect':
            cell=runtime.matrix.get(tuple(robot.position))
            if cell is None or cell[0]!=robot.type: DynamicFail(f'coleccion inadecuada en el robot "{robot.name}"')
            if self.target is None: robot.value=cell[1]
            else: self.target.value=cell[1]
        elif self.nombre=='drop':
            value=self.valor.evaluar(runtime,robot)
            if type_of(value)!=robot.type: DynamicFail(f'soltado inadecuado en el robot "{robot.name}"')
            runtime.matrix[tuple(robot.position)]=(robot.type,value)
        elif self.nombre=='read':
            value=read_typed_value(robot.type)
            if self.target is None: robot.value=value
            else: self.target.value=value
        elif self.nombre=='send':
            if robot.value is None: DynamicFail(f'valor no inicializado en el robot "{robot.name}"')
            print(printable(robot.value),end='')
        elif self.nombre=='move':
            distance=1 if self.valor is None else self.valor.evaluar(runtime,robot)
            if type_of(distance)!='int' or distance<0: DynamicFail(f'desplazamiento invalido del robot "{robot.name}"')
            if self.direction=='left': robot.position[0]-=distance
            elif self.direction=='right': robot.position[0]+=distance
            elif self.direction=='up': robot.position[1]+=distance
            else: robot.position[1]-=distance
    def imprimir(self,nivel=0): return tab(nivel)+self.nombre.upper()+'\n'

class Condicional(node):
    def __init__(self,guard,success,failure=None):
        super().__init__('CONDICIONAL',[guard,success]+([] if failure is None else [failure]))
        self.guardia=guard; self.exito=success; self.fracaso=failure
    def correr(self,runtime,robot=None):
        if self.guardia.evaluar(runtime,robot): self.exito.correr(runtime,robot)
        elif self.fracaso: self.fracaso.correr(runtime,robot)

class RepeticionIndeterminada(node):
    def __init__(self,guard,body):
        super().__init__('REPETICION_INDETERMINADA',[guard,body]); self.guardia=guard; self.cuerpo=body
    def correr(self,runtime,robot=None):
        while self.guardia.evaluar(runtime,robot): self.cuerpo.correr(runtime,robot)

class Ambito(node):
    def __init__(self,body): super().__init__('AMBITO',[body]); self.body=body
    def correr(self,runtime,robot=None): self.body.correr(runtime,robot)

class Behavior:
    def __init__(self,condition,body,local_table):
        self.condition=condition; self.body=body
        self.local_symbols=[item for item in local_table.simbolos if item is not None]

class Valor(node):
    def __init__(self,value,tp,symbol=None,is_me=False):
        super().__init__('VALOR',[]); self.valor=value; self.tipo=tp; self.symbol=symbol; self.is_me=is_me
    def evaluar(self,runtime,robot=None):
        if self.is_me:
            if robot is None or robot.value is None: DynamicFail('uso de un valor no inicializado')
            return robot.value
        if self.symbol is not None:
            if self.symbol.value is None: DynamicFail(f'uso de la variable no inicializada "{self.symbol.name}"')
            return self.symbol.value
        return self.valor
    def imprimir(self,nivel=0): return tab(nivel)+str(self.valor)+'\n'

class Binaria(node):
    arithmetic={'Suma','Resta','Multiplicacion','Division','Modulo'}
    boolean={'Conjuncion','Disyuncion'}
    order={'Menor o igual que','Mayor o igual que','Menor que','Mayor que'}
    symbols={'Suma':'+','Resta':'-','Multiplicacion':'*','Division':'/','Modulo':'%',
             'Conjuncion':'/\\','Disyuncion':'\\/','Igual que':'=','Distinto que':'/=',
             'Menor o igual que':'<=','Mayor o igual que':'>=','Menor que':'<','Mayor que':'>'}
    def __init__(self,kind,operation,left,right,line=None):
        super().__init__(kind,[left,right]); self.bina=kind; self.operacion=operation
        self.izquierda=left; self.derecha=right; self.valor=None
        if operation in self.arithmetic: valid=left.tipo==right.tipo=='int'; result='int'; expected='dos operandos int'
        elif operation in self.boolean: valid=left.tipo==right.tipo=='bool'; result='bool'; expected='dos operandos bool'
        elif operation in self.order: valid=left.tipo==right.tipo=='int'; result='bool'; expected='dos operandos int'
        else: valid=left.tipo==right.tipo and left.tipo in ('int','bool'); result='bool'; expected='operandos del mismo tipo'
        if 'error' in (left.tipo,right.tipo): self.tipo='error'
        elif valid: self.tipo=result
        else:
            ContextError(f'el operador {self.symbols[operation]} requiere {expected}',line); self.tipo='error'
    def evaluar(self,runtime,robot=None):
        left=self.izquierda.evaluar(runtime,robot); right=self.derecha.evaluar(runtime,robot); op=self.operacion
        if op=='Suma': return left+right
        if op=='Resta': return left-right
        if op=='Multiplicacion': return left*right
        if op in ('Division','Modulo'):
            if right==0: DynamicFail('division por cero')
            return left//right if op=='Division' else left%right
        if op=='Conjuncion': return left and right
        if op=='Disyuncion': return left or right
        if op=='Igual que': return left==right
        if op=='Distinto que': return left!=right
        if op=='Menor o igual que': return left<=right
        if op=='Mayor o igual que': return left>=right
        if op=='Menor que': return left<right
        return left>right

class Unaria(node):
    def __init__(self,operation,expression,line=None):
        super().__init__('EXP_UNARIA',[expression]); self.operacion=operation; self.expresion=expression; self.valor=None
        expected='int' if operation=='Menos unario' else 'bool'
        if expression.tipo=='error': self.tipo='error'
        elif expression.tipo==expected: self.tipo=expected
        else: ContextError(f'{operation} requiere un operando {expected}',line); self.tipo='error'
    def evaluar(self,runtime,robot=None):
        value=self.expresion.evaluar(runtime,robot)
        return -value if self.operacion=='Menos unario' else not value

###############################################################################################
## ------------------------------- producciones de la gramatica ----------------------------- ##
###############################################################################################

precedence=(('left','TkDisyuncion'),('left','TkConjuncion'),('right','TkNegacion'),
 ('nonassoc','TkIgual','TkNoIgual','TkMenor','TkMenorIgual','TkMayor','TkMayorIgual'),
 ('left','TkSuma','TkResta'),('left','TkMult','TkDiv','TkMod'))

def p_bot(p):
    'BOT : CREATE EXECUTE CLOSE_SCOPE'
    p[0]=p[2]

def p_create(p):
    'CREATE : TkCreate OPEN_SCOPE DECLARATIONS'
    p[0]=p[2]

def p_create_empty(p):
    'CREATE : OPEN_SCOPE'
    p[0]=p[1]

def p_abrir_alcance(p):
    'OPEN_SCOPE : empty'
    global TS_program
    TS_program=TS(TS_program); p[0]=TS_program

def p_cerrar_alcance(p):
    'CLOSE_SCOPE : empty'
    global TS_program
    TS_program=TS_program.padre

def p_definition_recursive(p):
    'DECLARATIONS : DECLARATIONS TYPE TkBot IDENT_LIST REGISTER_ROBOTS ACTIONS TkEnd'
    p[0]=None

def p_register_robots(p):
    'REGISTER_ROBOTS : empty'
    global current_robot_type,current_robot_items
    current_robot_type=p[-3]; current_robot_items=[]
    for name in p[-1]:
        item=InsertSimbol(name,current_robot_type,TS_program,True)
        if item: current_robot_items.append(item)

def p_definition_empty(p):
    'DECLARATIONS : empty'
    p[0]=None

def p_type(p):
    '''TYPE : TkInt
            | TkBool
            | TkCaracter'''
    p[0]=p[1]

def p_id_list_one(p):
    'IDENT_LIST : TkIdent'
    p[0]=[p[1]]

def p_id_list_recursive(p):
    'IDENT_LIST : IDENT_LIST TkComa TkIdent'
    p[1].append(p[3]); p[0]=p[1]

def p_action(p):
    'ACTIONS : ACTIONS TkOn ENTER_BEHAVIOR CONDITION TkDosPuntos OPEN_SCOPE INSTRUCTION_C TkEnd CLOSE_SCOPE EXIT_BEHAVIOR'
    behavior=Behavior(p[4],p[7],p[6])
    for robot in current_robot_items:
        if isinstance(p[4],str) and any(b.condition==p[4] for b in robot.conditions):
            ContextError(f'comportamiento {p[4]} redeclarado para el robot "{robot.name}"',p.lineno(2))
        else: robot.conditions.append(behavior)
    p[0]=None

def p_enter_behavior(p):
    'ENTER_BEHAVIOR : empty'
    global inside_behavior
    inside_behavior+=1

def p_exit_behavior(p):
    'EXIT_BEHAVIOR : empty'
    global inside_behavior
    inside_behavior-=1

def p_action_empty(p):
    'ACTIONS : empty'
    p[0]=None

def p_condition_activation(p):
    'CONDITION : TkActivation'
    p[0]='activation'
def p_condition_deactivation(p):
    'CONDITION : TkDeactivation'
    p[0]='deactivation'
def p_condition_expression(p):
    'CONDITION : EXP_BINARIA'
    p[0]=p[1]; RequireType(p[1],'bool','la condicion del comportamiento',p.lineno(1))
def p_condition_default(p):
    'CONDITION : TkDefault'
    p[0]='default'

def p_instruction_recursive_c(p):
    'INSTRUCTION_C : INSTRUCTION_C SIMPLE_INSTRUCTION_C'
    p[1].instrucciones.append(p[2]); p[0]=p[1]
def p_instruction_simple_c(p):
    'INSTRUCTION_C : SIMPLE_INSTRUCTION_C'
    p[0]=Secuenciacion([p[1]])
def p_instruction_recursive_e(p):
    'INSTRUCTION_E : INSTRUCTION_E SIMPLE_INSTRUCTION_E'
    if isinstance(p[1],Secuenciacion): p[1].instrucciones.append(p[2]); p[0]=p[1]
    else: p[0]=Secuenciacion([p[1],p[2]])
def p_instruction_simple_e(p):
    'INSTRUCTION_E : SIMPLE_INSTRUCTION_E'
    p[0]=p[1]

def p_simple_instruction_store(p):
    'SIMPLE_INSTRUCTION_C : TkStore EXP_BINARIA TkPunto'
    p[0]=InstruccionRobot('store',p[2]); RequireType(p[2],current_robot_type,'store',p.lineno(1))

def p_simple_instruction_collect(p):
    '''SIMPLE_INSTRUCTION_C : TkCollect TkPunto
                            | TkCollect TkAs TkIdent TkPunto'''
    target=InsertSimbol(p[3],current_robot_type,TS_program) if len(p)==5 else None
    p[0]=InstruccionRobot('collect',target=target)

def p_simple_instruction_drop(p):
    'SIMPLE_INSTRUCTION_C : TkDrop EXP_BINARIA TkPunto'
    p[0]=InstruccionRobot('drop',p[2])

def p_direction(p):
    '''DIRECTION : TkLeft
                 | TkRight
                 | TkUp
                 | TkDown'''
    p[0]=p[1]

def p_simple_instruction_read(p):
    '''SIMPLE_INSTRUCTION_C : TkRead TkPunto
                            | TkRead TkAs TkIdent TkPunto'''
    target=InsertSimbol(p[3],current_robot_type,TS_program) if len(p)==5 else None
    p[0]=InstruccionRobot('read',target=target)

def p_simple_instruction_send(p):
    'SIMPLE_INSTRUCTION_C : TkSend TkPunto'
    p[0]=InstruccionRobot('send')

def p_simple_instruction_move(p):
    '''SIMPLE_INSTRUCTION_C : DIRECTION TkPunto
                            | DIRECTION EXP_BINARIA TkPunto'''
    expression=p[2] if len(p)==4 else None
    p[0]=InstruccionRobot('move',expression,direction=p[1])
    if expression: RequireType(expression,'int','el desplazamiento',p.lineno(1))

def resolve_robot_list(names,line):
    result=[]
    for name in names:
        item=LookupSimbol(name,TS_program)
        if item is None: ContextError(f'la variable "{name}" no ha sido declarada',line)
        elif not item.is_robot: ContextError(f'"{name}" no identifica un robot',line)
        else: result.append(item)
    return result

def p_simple_instruction_activate(p):
    'SIMPLE_INSTRUCTION_E : TkActivate IDENT_LIST TkPunto'
    p[0]=instrutions('ACTIVACION',resolve_robot_list(p[2],p.lineno(1)))
def p_simple_instruction_deactivate(p):
    'SIMPLE_INSTRUCTION_E : TkDeactivate IDENT_LIST TkPunto'
    p[0]=instrutions('DEACTIVACION',resolve_robot_list(p[2],p.lineno(1)))
def p_simple_instruction_advance(p):
    'SIMPLE_INSTRUCTION_E : TkAdvance IDENT_LIST TkPunto'
    p[0]=instrutions('AVANCE',resolve_robot_list(p[2],p.lineno(1)))

def p_simple_instruction_if(p):
    'SIMPLE_INSTRUCTION_E : TkIf EXP_BINARIA TkDosPuntos INSTRUCTION_E TkEnd'
    p[0]=Condicional(p[2],p[4]); RequireType(p[2],'bool','la guardia de if',p.lineno(1))
def p_simple_instruction_if_else(p):
    'SIMPLE_INSTRUCTION_E : TkIf EXP_BINARIA TkDosPuntos INSTRUCTION_E TkElse TkDosPuntos INSTRUCTION_E TkEnd'
    p[0]=Condicional(p[2],p[4],p[7]); RequireType(p[2],'bool','la guardia de if',p.lineno(1))
def p_simple_instruction_while(p):
    'SIMPLE_INSTRUCTION_E : TkWhile EXP_BINARIA TkDosPuntos INSTRUCTION_E TkEnd'
    p[0]=RepeticionIndeterminada(p[2],p[4]); RequireType(p[2],'bool','la guardia de while',p.lineno(1))
def p_simple_instruction_scope(p):
    'SIMPLE_INSTRUCTION_E : CREATE EXECUTE CLOSE_SCOPE'
    p[0]=Ambito(p[2])

def p_execute(p):
    'EXECUTE : TkExecute INSTRUCTION_E TkEnd'
    p[0]=p[2]

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
    operations={'+':('BIN_ARITMETICA','Suma'),'-':('BIN_ARITMETICA','Resta'),
      '*':('BIN_ARITMETICA','Multiplicacion'),'/':('BIN_ARITMETICA','Division'),
      '%':('BIN_ARITMETICA','Modulo'),'/\\':('BIN_BOOLEANA','Conjuncion'),
      '\\/':('BIN_BOOLEANA','Disyuncion'),'=':('BIN_RELACIONAL','Igual que'),
      '/=':('BIN_RELACIONAL','Distinto que'),'<=':('BIN_RELACIONAL','Menor o igual que'),
      '>=':('BIN_RELACIONAL','Mayor o igual que'),'<':('BIN_RELACIONAL','Menor que'),
      '>':('BIN_RELACIONAL','Mayor que')}
    kind,operation=operations[p[2]]; p[0]=Binaria(kind,operation,p[1],p[3],p.lineno(2))

def p_exp_binaria_paren(p):
    'EXP_BINARIA : TkParAbre EXP_BINARIA TkParCierra'
    p[0]=p[2]
def p_exp_unaria_negacion(p):
    'EXP_BINARIA : TkNegacion EXP_BINARIA'
    p[0]=Unaria('Negacion',p[2],p.lineno(1))
def p_exp_unaria_resta(p):
    'EXP_BINARIA : TkResta EXP_BINARIA %prec TkNegacion'
    p[0]=Unaria('Menos unario',p[2],p.lineno(1))
def p_exp_binaria_num(p):
    'EXP_BINARIA : TkNum'
    p[0]=Valor(p[1],'int')
def p_exp_binaria_me(p):
    'EXP_BINARIA : TkMe'
    if inside_behavior==0:
        ContextError('la palabra reservada "me" solo puede usarse dentro de un comportamiento',p.lineno(1)); p[0]=Valor('me','error',is_me=True)
    else: p[0]=Valor('me',current_robot_type,is_me=True)
def p_exp_binaria_bool_true(p):
    'EXP_BINARIA : TkTrue'
    p[0]=Valor(True,'bool')
def p_exp_binaria_bool_false(p):
    'EXP_BINARIA : TkFalse'
    p[0]=Valor(False,'bool')
def p_exp_binaria_var(p):
    'EXP_BINARIA : TkIdent'
    item=LookupSimbol(p[1],TS_program)
    if item is None: ContextError(f'la variable "{p[1]}" no ha sido declarada',p.lineno(1)); p[0]=Valor(p[1],'error')
    else: p[0]=Valor(p[1],item.type,symbol=item)
def p_exp_binaria_char(p):
    'EXP_BINARIA : TkCaracter'
    p[0]=Valor(p[1],'char')

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    global syntax_error
    if syntax_error is not None: return
    if p: syntax_error=f'Error sintactico en la fila {p.lineno}, columna {find_column(p.lexer.lexdata,p)}: token inesperado "{p.value}"'
    else: syntax_error='Error sintactico: fin inesperado del archivo'

# No se generan mensajes ni archivos auxiliares durante la correccion en el LDC.
parser=yacc.yacc(debug=False,write_tables=False)

if __name__=='__main__':
    content=ReadBotFile(sys.argv[1])
    lexer.lineno=1; lexer.input(content)
    while lexer.token(): pass
    if errors:
        for error in errors: print(error)
        sys.exit(1)
    lexer.lineno=1; AST=parser.parse(content,lexer=lexer)
    if syntax_error: print(syntax_error); sys.exit(1)
    if context_errors:
        for error in context_errors: print(error)
        sys.exit(1)
    try: AST.correr(Runtime())
    except DynamicError as error: print(error); sys.exit(1)