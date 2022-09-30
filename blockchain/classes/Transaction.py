class Transaction:

    def __init__(self, sender: str, reciever: str, amount: int, time: str):
        self.sender = sender 
        self.reciever = reciever
        self.amount = amount
        self.time = time