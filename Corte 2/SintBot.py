import sys
import ply.lex as lex
import ply.yacc as yacc
import scipy.stats as stats

if len(sys.argv) < 2:
    print("uso: ./SintBot <ruta del archivo>")
    sys.exit(1)
