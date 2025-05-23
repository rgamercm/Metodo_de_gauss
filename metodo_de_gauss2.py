from sympy import symbols, Eq, simplify, sympify, solve
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import re

# Transformaciones para permitir multiplicación implícita
transformations = standard_transformations + (implicit_multiplication_application,)

def pedir_ecuaciones():
    while True:
        try:
            n = int(input("¿Cuántas ecuaciones (y variables) vas a ingresar?: "))
            if n < 2:
                print("Debes ingresar al menos 2 ecuaciones.")
                continue
            break
        except ValueError:
            print("Por favor, ingresa un número entero válido.")

    ecuaciones = []
    print("\nIngresa cada ecuación en una sola línea, con esta sintaxis (sin espacios):")
    print("Ejemplo: -1.2x+3.5y+2.8z=24.8")

    for i in range(n):
        ecuacion = input(f"Ecuación {i+1}: ").replace(" ", "")
        ecuaciones.append(ecuacion)
    return ecuaciones

def extraer_variables(ecuaciones):
    variables = sorted(set(re.findall(r'[a-zA-Z]', ''.join(ecuaciones))))
    return symbols(variables)

def parsear_ecuaciones(ecuaciones):
    variables = extraer_variables(ecuaciones)
    simbolos_dict = {str(v): v for v in variables}
    sistema = []

    for ecuacion in ecuaciones:
        izquierda, derecha = ecuacion.split('=')
        izquierda = parse_expr(izquierda, local_dict=simbolos_dict, transformations=transformations)
        derecha = parse_expr(derecha, local_dict=simbolos_dict, transformations=transformations)
        sistema.append(Eq(izquierda, derecha))

    return sistema, variables

def imprimir_ecuacion(ec):
    return str(ec.lhs) + " = " + str(ec.rhs)
def aplicar_reduccion(ec1, ec2, variable):
    coef1 = ec1.lhs.coeff(variable)
    coef2 = ec2.lhs.coeff(variable)

    if coef1 == 0 or coef2 == 0:
        print(f"No se puede eliminar la variable {variable} porque uno de los coeficientes es 0.")
        return ec2

    # Multiplicamos para hacer los coeficientes opuestos
    mult1 = coef2
    mult2 = -coef1

    nueva_ec1 = Eq(simplify(ec1.lhs * mult1), simplify(ec1.rhs * mult1))
    nueva_ec2 = Eq(simplify(ec2.lhs * mult2), simplify(ec2.rhs * mult2))

    print(f"\nMultiplicamos Ecuación A por {mult1} y Ecuación B por {mult2} para cancelar '{variable}':")
    print("Ecuación A:", imprimir_ecuacion(nueva_ec1))
    print("Ecuación B:", imprimir_ecuacion(nueva_ec2))

    lhs_nueva = simplify(nueva_ec1.lhs + nueva_ec2.lhs)
    rhs_nueva = simplify(nueva_ec1.rhs + nueva_ec2.rhs)
    nueva_ec = Eq(lhs_nueva, rhs_nueva)

    print("Resultado de la suma:")
    print(imprimir_ecuacion(nueva_ec))

    return nueva_ec


def resolver_sistema(sistema, variables):
    n = len(sistema)
    nuevas_ecs = sistema.copy()

    print("\n--- Reducción paso a paso ---")
    for i in range(n - 1):
        print(f"\nEliminando variable: {variables[i]}")
        nuevas_ecs_tmp = []
        for j in range(i + 1, len(nuevas_ecs)):
            reducida = aplicar_reduccion(nuevas_ecs[i], nuevas_ecs[j], variables[i])
            nuevas_ecs_tmp.append(reducida)
        nuevas_ecs = nuevas_ecs[:i + 1] + nuevas_ecs_tmp

    print("\n--- Sustitución hacia atrás ---")
    soluciones = {}
    for i in reversed(range(len(nuevas_ecs))):
        ec = nuevas_ecs[i]
        ec_sust = ec.subs(soluciones)
        vars_restantes = [v for v in variables if v not in soluciones and ec_sust.lhs.has(v)]

        if not vars_restantes:
            if simplify(ec_sust.lhs - ec_sust.rhs) != 0:
                print("El sistema no tiene solución.")
                return None
            else:
                continue

        solucion = solve(ec_sust, vars_restantes[0])
        if not solucion:
            print(f"No se pudo resolver para la variable {vars_restantes[0]}.")
            return None

        soluciones[vars_restantes[0]] = solucion[0]
        print(f"{vars_restantes[0]} = {solucion[0]}")

    return soluciones

# Programa principal
print("=== Método de Gauss por Reducción Simbólica ===")
ecuaciones = pedir_ecuaciones()
sistema, variables = parsear_ecuaciones(ecuaciones)

print("\nSistema de ecuaciones:")
for i, ec in enumerate(sistema):
    print(f"Ecuación {i+1}: {imprimir_ecuacion(ec)}")

soluciones = resolver_sistema(sistema, variables)

if soluciones:
    print("\n=== Soluciones finales ===")
    for var in variables:
        if var in soluciones:
            print(f"{var} = {simplify(soluciones[var])}")
        else:
            print(f"{var} no tiene un valor definido (se canceló en el proceso)")
