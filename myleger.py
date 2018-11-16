# -*- coding:utf-8 -*-
from utils import gen_pub_pvt


class Income(object):
    def __init__(self, ID, peerID, amount):
        #和Leger的ID保持一致
        self.ID = ID
        self.peerID = peerID
        self.amount = amount
        super(Income, self).__init__()

    def toString(self):
        res = self.peerID, " -> ", self.ID, " : ", self.amount
        return res

class Expense(object):
    def __init__(self, ID, peerID, amount):
        #和Leger的ID保持一致
        self.ID = ID
        self.peerID = peerID
        self.amount = amount
        super(Expense, self).__init__()

    def toString(self):
        res = self.ID, " -> ", self.peerID, " : ", self.amount, "\n"
        return res


class Leger(object):
    def __init__(self, ID):
        #和node的ID保持一致
        self.ID = ID
        self.pub_key, self.pvt_key = gen_pub_pvt()
        self.incomes = []
        self.expenses = []
        super(Leger, self).__init__()

    # def pay(self, peerID, amount):
    #     ex = expense(self.ID, peerID,amount)
    #     self.expense(ex)

    def income(self, income):
        self.incomes.append(income)

    def expense(self, expense):
        self.expenses.append(expense)

    def store(self):
        filePath = 'legers/leger', self.ID
        with open(filePath, 'w') as f:
            f.write(self.toString())


    def toString(self):
        res = "incomes: \n"
        for income in self.incomes:
            res += income.toString()

        res += "expenses: \n"
        for expense in self.expenses:
            res += expense.toString()

        return res