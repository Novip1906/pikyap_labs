import math

class BiquadraticEquation:
    def __init__(self, a, b, c):
        if a == 0:
            raise ValueError("Коэффициент A не может быть равен 0.")
        self.a = a
        self.b = b
        self.c = c

    def solve(self):
        d = self.b**2 - 4*self.a*self.c
        roots = []

        if d < 0:
            return roots

        y1 = (-self.b + math.sqrt(d)) / (2*self.a)
        y2 = (-self.b - math.sqrt(d)) / (2*self.a)

        for y in (y1, y2):
            if y > 0:
                roots.append(math.sqrt(y))
                roots.append(-math.sqrt(y))
            elif y == 0:
                roots.append(0.0)

        return sorted(set(roots))

    def __str__(self):
        return f"{self.a}*x^4 + {self.b}*x^2 + {self.c} = 0"

def main():
    a = float(input("A = "))
    b = float(input("B = "))
    c = float(input("C = "))

    try:
        eq = BiquadraticEquation(a, b, c)
        roots = eq.solve()
        print("Уравнение:", eq)
        if roots:
            print("Корни:", ", ".join(map(str, roots)))
        else:
            print("Действительных корней нет.")
    except ValueError as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()
