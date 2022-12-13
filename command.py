class command:
    def __init__(self):
        self.history = []
        self.position = 0
        #счетчики сколько раз перемещали слой на передний или задний план
        self.num = 0

    def execute(self, command):
        if len(self.history) != self.position:
            self.history = self.history[:self.position]
        self.position += 1
        self.history.append(command)

    def show_history(self):
        if self.position > 0:
            return self.history[:self.position]
        else:
            return -1
    
    def undo(self):
        if (self.position > 0):
            if (self.history[self.position-1][0] == 'LIF'):
                self.first_is_last()
                self.num -= 2
                self.position -= 2
            elif (self.history[self.position-1][0] == 'FIL'):
                self.last_is_first()
                self.num -= 2
                self.position -= 2
            else:
                self.position -= 1

    def redo(self):
        if len(self.history) > self.position:
            if (self.history[self.position][0] == 'LIF'):
                self.last_is_first()
            elif (self.history[self.position][0] == 'FIL'):
                self.first_is_last()
            else:
                self.position += 1
    
    def last_is_first(self):
        temp = []
        ti = 0
        if self.position-self.num > 1:
            for j in range(self.position - 1, 0, -1):
                if (self.history[j][0] != 'LIF' and self.history[j][0] != 'FIL'):
                    first = self.history[j]
                    break

            for i in range(self.position-1, 0, -1):
                if (self.history[i][0] != 'LIF' and self.history[i][0] != 'FIL' and temp==[]):
                    if(self.history[i-1][0] != 'LIF' and self.history[i-1][0] != 'FIL'):
                        self.history[i] = self.history[i-1]
                    else:
                        temp = self.history[i]
                        ti = i
                elif(self.history[i][0] != 'LIF' and self.history[i][0] != 'FIL' and temp!=[]):
                    self.history[ti] = self.history[i]
                    if (self.history[i-1][0] != 'LIF' and self.history[i-1][0] != 'FIL'):
                        self.history[i] = self.history[i-1]
                        temp = []
                    else:
                        temp = self.history[i]
                        ti = i
            self.history[0] = first
            self.history = self.history[:self.position]
            self.num += 1
            self.execute(['LIF'])
        else:
            return -1

    def first_is_last(self):
        if self.position-self.num>1:
            temp = []
            ti = 0
            first = self.history[0]
            for i in range(0, self.position-1):
                if (self.history[i][0] != 'LIF' and self.history[i][0] != 'FIL' and temp==[]):
                    if(self.history[i+1][0] != 'LIF' and self.history[i+1][0] != 'FIL'):
                        self.history[i] = self.history[i+1]
                    else:
                        temp = self.history[i]
                        ti = i
                elif(self.history[i+1][0] != 'LIF' and self.history[i+1][0] != 'FIL' and temp!=[]):
                    self.history[ti] = self.history[i+1]
                    temp = []                    
            for j in range(self.position - 1, 0, -1):
                if (self.history[j][0] != 'LIF' and self.history[j][0] != 'FIL'):
                    self.history[j] = first
                    break
            self.history = self.history[:self.position]
            self.num += 1
            self.execute(['FIL'])
        else:
            return -1
    
    def delete_last(self, new):
        for j in range(self.position - 1, 0, -1):
            if (self.history[j][0] != 'LIF' and self.history[j][0] != 'FIL'):
                self.history[j] = new
                break

    def last_one(self):
        if (len(self.history) != 1 and self.history !=-1):
            for j in range(self.position - 1, 0, -1):
                if (self.history[j][0] != 'LIF' and self.history[j][0] != 'FIL'):
                    return self.history[j]
        else:
            return self.history[0]
        
    def new_file(self):
        self.position = 0
        self.history = []

