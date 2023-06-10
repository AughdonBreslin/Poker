

class Player:
    def __init__(self, number : int, stackSize: int):
        self.number = number
        self.stackSize = stackSize

    def __str__(self):
        return f"P{self.number}: Stack: {self.stackSize}"
    