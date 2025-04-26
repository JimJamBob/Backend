def add(num1: int, num2: int):
    return num1 + num2

class Insufficient_Funds(Exception):
    pass

class Bankaccount:
    def __init__(self, input_balance):
        self.balance=input_balance
 
    def deposit(self, input_balance):
        self.balance += input_balance
 
    def withdraw(self, input_balance):
        if self.balance>=input_balance:
            self.balance-=input_balance
        else:
            raise Insufficient_Funds("Not enough monnayy")
 