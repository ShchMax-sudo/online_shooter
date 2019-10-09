class Point():
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __add__(self, other):
        return Point(self.x, self.y)
    def norm(self):
        return Point(self.x / (self.x ** 2 + self.y ** 2) ** 0.5, self.y / (self.x ** 2 + self.y ** 2) ** 0.5)
    def resize(self, a):
        return Point(Point(self.x, self.y).norm().x * a, Point(self.x, self.y).norm().y * a)

opens = input("Did you want to get open cut?(y/n):\n") == "y"
x1, y1, x2, y2 = map(int, input("Input coords of begin and end of cut:\n").split())
a = Point(x2 - x1, y2 - y1).resize(30)
b = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5) // 30 + 1
print((b + (not opens)))
print()
for i in range(b):
    print(int(x1), int(y1))
    x1 += a.x
    y1 += a.y
if (not opens):
    print(int(x2), int(y2))
print()
print("2\n" * (b + (not opens)))