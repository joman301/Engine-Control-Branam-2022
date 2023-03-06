





class Calculator:
    def __init__(self, value1, value2, value3):
        self.value1 = value1
        self.value2 = value2
        self.value3 = value3
        print("I am done initializing")
        self.add(4)

    def multiply(self, input):
        print(self.value1 + "'s multiplied answer: " + str(self.value2 * input))

    def add(self, input):
        print(self.value1 + "'s added answer: " + str(self.value2 + input))


if __name__ == "__main__":
    
    calculators = {
        "Calculator_1": Calculator("Josh", 2, True),
        "Calculator_2": Calculator("Nick", 3, False),
        "Calculator_3": Calculator("Matt", 3, False),
        "Calculator_4": Calculator("Micah", 3, False),
        "Calculator_5": Calculator("John", 3, False),
        "Hello" : "I am a string"
    }

    for key in calculators:
        print("Calculator name: " + key)
        print("Name in object: " + calculators[key].value1)
   

