def a():
    print(__name__)
def b():
    print(__name__)
def main():
    print(__name__)
    a()
    b()

if __name__ == "__main__":
    print(__name__)
    main()
