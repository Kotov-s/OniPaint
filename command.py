class command:
    def __init__(self):
        self.history = []
        self.position = 0
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
            self.position -= 1

    def redo(self):
        if len(self.history) > self.position:
            self.position += 1
        
    def new_file(self):
        self.position = 0
        self.history = []
        self.num = 0

    def delete_last(self):
        if (self.history !=-1):
            for j in range(self.position - 1, -1, -1):
                self.position = j
                break
