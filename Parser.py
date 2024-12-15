import ASTNodeDefs as AST
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []
    
    # Move to the next position in the code increment by one.
    def advance(self):
        self.position += 1
        if self.position >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.position]

    # If the current char is whitespace, move ahead.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Tokenize the identifier.
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)
    

    # Tokenize numbers, including float handling
    def number(self):
        result = ''

        is_float = False
        #parse characters as long as they are numbers or decimal point
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if is_float:  #multiple decimal points are not allowed
                    self.error("Invalid number format: multiple decimal points")
                is_float = True
            result += self.current_char
            self.advance()

        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))

    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident  # Generic identifier
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EQ', '==')
                return ('EQUALS', '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('NEQ', '!=')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return ('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return ('COLON', ':')
            if self.current_char == '{':
                self.advance()
                return ("LBRACE", '{')
            if self.current_char == '}':
                self.advance()
                return ('RBRACE', '}')
            if self.current_char == '\n':
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all the tokens in a list.
    def tokenize(self):
        while True:
            token = self.token()
            self.tokens.append(token)
            if token[0] == 'EOF':
                break
        return self.tokens



import ASTNodeDefs as AST

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        # Use these to track the variables and their scope
        self.symbol_table = {'global': {}}
        self.scope_counter = 0
        self.scope_stack = [{}]
        self.messages = []

    def error(self, message):
        self.messages.append(message)
    
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    def enter_scope(self):
        new_scope = {}
        self.scope_counter += 1
        self.scope_stack.append(new_scope)

    def exit_scope(self):
        if not self.scope_stack:
            self.error("No scope to exit")
        self.scope_counter -= 1
        self.scope_stack.pop()  # Correctly pop the dictionary

    # Return the current scope name
    def current_scope(self):
        return self.scope_stack[-1] if self.scope_stack else {}

    def checkVarDeclared(self, identifier):
        if identifier in self.current_scope():
            self.error(f"Variable {identifier} has already been declared in the current scope")


    def checkVarUse(self, identifier):
        for scope in reversed(self.scope_stack):
            if identifier in scope:
                #if var is found, no error
                return  
        self.error(f"Variable {identifier} has not been declared in the current or any enclosing scopes")


    def checkTypeMatch2(self, vType, eType, var, exp):
        if (vType != eType) and (vType and eType in {'float', 'int'}):
            self.error(f"Type Mismatch between {vType} and {eType}")


    def add_variable(self, name, var_type):
        if not self.scope_stack:
            self.error('No scope to add variable.')
        curr_scope = self.scope_stack[-1]
        self.checkVarDeclared(name)
        curr_scope[name] = var_type 


    def get_variable_type(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
        return AST.Block(statements)

    def statement(self):
        if self.current_token[0] in {'INT', 'FLOAT'}:

            return self.decl_stmt()
        elif self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':
                return self.function_call()
            else:
                self.error(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt()
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()
        else:
            self.error(f"Unexpected token: {self.current_token}")
        self.advance()

    def decl_stmt(self):
        var_type = self.current_token[1]
        self.advance()

        if self.current_token[0] != 'IDENTIFIER':
            self.error(f"Expected identifier, got {self.current_token}")
        var_name = self.current_token[1]
        self.checkVarDeclared(var_name)
        self.advance()

        expression = None
        if self.current_token[0] == 'EQUALS':
            self.advance()
            expression = self.expression()

            expr_type = expression.value_type
            self.checkTypeMatch2(var_type, expr_type, var_name, expression)
        else:
            self.advance()
            expression = None
        
        self.add_variable(var_name, var_type)

        return AST.Declaration(var_type, var_name, expression)

    def assign_stmt(self):
        #parse var name
        if self.current_token[0] != 'IDENTIFIER':
            self.error(f'Expected identifier, got {self.current_token}')
        var_name = self.current_token[1]
        #check if var is declared
        self.checkVarUse(var_name)
        #acquire type
        var_type = self.get_variable_type(var_name)
        self.advance()

        #parse '='
        if self.current_token[0] != 'EQUALS':
            self.error(f"Expected '=', got {self.current_token}")
        self.advance()

        #parse expression
        expression = self.expression()
        expr_type = expression.value_type

        #check type compatibility
        self.checkTypeMatch2(var_type, expr_type, var_name, expression)

        return AST.Assignment(var_name, expression)

    def if_stmt(self):
        #parse 'if'
        if self.current_token[0] != 'IF':
            self.error(f"Expected 'if', got {self.current_token}")
        self.advance()

        #parse condition
        condition = self.boolean_expression()

        #parse then block
        self.enter_scope()
        then_block = self.block()
        self.exit_scope()

        #parse else block
        else_block = None
        if self.current_token[0] == 'ELSE':
            self.advance()

            self.enter_scope()
            else_block = self.block()
            self.exit_scope()
                                 
        return AST.IfStatement(condition, then_block, else_block)


    def while_stmt(self):
        #parse 'while'
        if self.current_token[0] != 'WHILE':
            self.error(f"Expected 'while', got {self.current_token}")
        self.advance()

        #parse condition
        condition = self.boolean_expression()

        #parse block
        self.enter_scope()
        block = self.block()
        self.exit_scope()        

        return AST.WhileStatement(condition, block)

    
    def block(self):
        statements = []
        #check opening bracket
        if self.current_token[0] != 'LBRACE':
            self.error(f"Expecting '{{', got {self.current_token}")
            return None
        self.advance()
        #self.enter_scope()

        #parse each statement until closing bracket
        while self.current_token[0] != 'RBRACE':
            statements.append(self.statement())
        if self.current_token[0] != 'RBRACE':
            self.error(f"Expected '}}', but got {self.current_token}")

        self.advance()
        #self.exit_scope()
        return AST.Block(statements)

    
    def expression(self):
        left = self.term()
        while self.current_token[0] in ['PLUS', 'MINUS']:
            op = self.current_token[1]
            self.advance()
            right = self.term()
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            
            result_type = left.value_type

            left = AST.BinaryOperation(left, op, right, value_type=result_type)

        return left

    def boolean_expression(self):
        left = self.expression()
        if self.current_token[0] not in {'EQ', 'NEQ', 'LESS', 'GREATER'}:
            self.error(f"Expected comparison operator, got {self.current_token}")
        op = self.current_token[0]
        self.advance()
        right = self.expression()
        self.checkTypeMatch2(left.value_type, right.value_type, left, right)
        return AST.BooleanExpression(left, op, right)
        

    # TODO: Implement parsing for multiplication and division and check for type compatibility
    def term(self):
        #parse first factor
        left = self.factor()

        #parse multiplication and division
        while self.current_token[0] in ['MULTIPLY', 'DIVIDE']:
            op = self.current_token[1]
            self.advance()

            #parse next factor
            right = self.factor()

            #type check
            self.checkTypeMatch2(left.value_type, right.value_type, left, right)

            #update type from operation
            result_type = left.value_type if left.value_type == right.value_type else 'float'
            left = AST.BinaryOperation(left, op, right, value_type=result_type)
        return left


        
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'int')
        elif self.current_token[0] == 'FNUMBER':
            num = self.current_token[1]
            self.advance()
            return AST.Factor(num, 'float')
        elif self.current_token[0] == 'IDENTIFIER':
            var_name = self.current_token[1]
            self.checkVarUse(var_name)
            var_type = self.get_variable_type(var_name)
            self.advance()
            return AST.Factor(var_name, var_type)
        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            if self.current_token[0] != 'RPAREN':
                self.error(f"Expected ')', got {self.current_token}")
                return None
            self.advance()
            return expr
        else:
            self.error(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = self.arg_list()
        self.expect('RPAREN')

        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        args = []
        if self.current_token[0] != 'RPAREN':
            args.append(self.expression())
            while self.current_token[0] == 'COMMA':
                self.advance()
                args.append(self.expression())

        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance()
        else:
            self.error(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        return self.tokens[0][0] if self.tokens else None
