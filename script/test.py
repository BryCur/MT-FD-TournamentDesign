test = "A"

def printTest():
    global test
    print(test)


if __name__ == "__main__":
    test = "B"
    printTest()
