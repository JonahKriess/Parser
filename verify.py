import Parser as p0

count = 0
def test_parser(test_input, expected_output):
    """
    This function runs the lexer and parser on the test input,
    compares the parsed AST with the expected output, and returns the result.
    """
    global count
    # Initialize the lexer and tokenize the input
    lexer = p0.Lexer(test_input)
    tokens = lexer.tokenize()
    # Initialize the parser and generate the AST
    parser = p0.Parser(tokens)
    ast = parser.parse()


    result = parser.messages
    # Compare the result with the expected output
    if result == expected_output:
        print("Test passed.")
        count += 1
    else:
        print("Test failed.")
        print("Expected:")
        print(expected_output)
        print("Got:")
        print(result)



# Testcase 1
def test1():
    text1 = '''
    int a = 10
    int b = 10.2
    '''

    correctMessages = ['Type Mismatch between int and float']
    if test_parser(text1, correctMessages) == 0:
        return 1
    return 0


# Testcase 2: Use of undeclared variable and redeclaration in nested loop
def test2():
    text4 = '''
    while x > 0 {
      int x = 10
      int y = x
    }
    int c = y
    '''
    correctMessages = ['Variable x has not been declared in the current or any enclosing scopes', 
                       'Variable y has not been declared in the current or any enclosing scopes', 
                       ]
    if test_parser(text4, correctMessages) == 0:
        return 1
    return 0

# Testcase 3: Type mismatch in while loop and nested if
def test3():
    text5 = '''
    float x = 0.234
    int y = 0
    int z = 0
    if x > y {
      float sum = 10.50
      int cnt = 20
      if cnt > 0 {
        int x = 1
        sum = 2.0 * sum
        x = x + 1
      }
      x = 10
      while x > 1.9 {
        z = z + y
        x = x - 1.0
        sum = x + sum
      }
    }
    '''
    correctMessages = ['Type Mismatch between float and int', 'Type Mismatch between float and int']
    if test_parser(text5, correctMessages) == 0:
        return 1
    return 0

# Testcase 4: Valid code with nested blocks
def test4():
    text7 = '''
    int a = 10
    int b = 12
    float z = 10.2

    if a > 10 {
        int zoo = 10
        if a > 10 {
            int zoo = 12
            float a = 10.2
            zoo = 10
        }
        zoo = a
    } else {
        float c = 20.3
        c = 10.2
    }
    while a > 10 {
        int y = 100
        y = y + y
    }
    '''
    correctMessages = []
    if test_parser(text7, correctMessages) == 0:
        return 1
    return 0


def test5():
    text10 = '''
    int a = 10
    while a > 0 {
        int b = 5
        while b > 0 {
            c = a + b
            b = b - 1
        }
        a = a - 1
    }
    '''
    correctMessages = ['Variable c has not been declared in the current or any enclosing scopes']
    if test_parser(text10, correctMessages) == 0:
        return 1
    return 0

# Running all tests and counting passes
passed = 0
test1()
test2()
test3()
test4()
test5()
print(count)

if count == 5:
    print(f"All {count} test cases are passed") 
else:
    print(f"Only {count} testcases are passed, pls fix the logic")