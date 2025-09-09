import sys
import math

def solve_biquadratic(a, b, c):
    d = b**2 - 4*a*c
    roots = []

    if d < 0:
        return roots

    y1 = (-b + math.sqrt(d)) / (2*a)
    y2 = (-b - math.sqrt(d)) / (2*a)

    for y in (y1, y2):
        if y > 0:
            roots.append(math.sqrt(y))
            roots.append(-math.sqrt(y))
        elif y == 0:
            roots.append(0.0)

    return sorted(set(roots))


def main():
    if len(sys.argv) == 4:
        try:
            a, b, c = map(float, sys.argv[1:])
        except ValueError:
            print("Ошибка: коэффициенты должны быть числами.")
            return
    else:
        print("Введите коэффициенты A, B, C:")
        try:
            a = float(input("A = "))
            b = float(input("B = "))
            c = float(input("C = "))
        except ValueError:
            print("Ошибка: нужно вводить числа.")
            return

    if a == 0:
        print("Ошибка: A не должно быть равно 0.")
        return

    roots = solve_biquadratic(a, b, c)

    print(f"\nУравнение: {a}*x^4 + {b}*x^2 + {c} = 0")
    if roots:
        print("Действительные корни:", ", ".join(map(str, roots)))
    else:
        print("Действительных корней нет.")


if __name__ == "__main__":
    main()
