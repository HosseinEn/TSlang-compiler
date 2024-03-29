"""
    exec: python3 TestTokenizer.py
"""



import unittest
from TeslangLexer import Tokenizer

class TestTokenizer(unittest.TestCase):
    def test_comment(self):
        data = '''
        # This is a comment
        1 + 2
        '''
        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)
        self.assertEqual(token_list[0].type, 'NUMBER')
        self.assertEqual(token_list[0].value, 1)
        self.assertEqual(token_list[1].type, 'PLUS')
        self.assertEqual(token_list[1].value, '+')
        self.assertEqual(token_list[2].type, 'NUMBER')
        self.assertEqual(token_list[2].value, 2)

    def test_string(self):
        data = '''
        def int main() {
            var str x = "hello world";
        }
        '''

        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)
        self.assertEqual(token_list[0].type, 'DEF')
        self.assertEqual(token_list[0].value, 'def')
        self.assertEqual(token_list[1].type, 'INT')
        self.assertEqual(token_list[1].value, 'int')
        self.assertEqual(token_list[2].type, 'ID')
        self.assertEqual(token_list[2].value, 'main')
        self.assertEqual(token_list[3].type, 'LPAREN')
        self.assertEqual(token_list[3].value, '(')
        self.assertEqual(token_list[4].type, 'RPAREN')
        self.assertEqual(token_list[4].value, ')')
        self.assertEqual(token_list[5].type, 'LBRACE')
        self.assertEqual(token_list[5].value, '{')
        self.assertEqual(token_list[6].type, 'VAR')
        self.assertEqual(token_list[6].value, 'var')
        self.assertEqual(token_list[7].type, 'STR')
        self.assertEqual(token_list[7].value, 'str')
        self.assertEqual(token_list[8].type, 'ID')
        self.assertEqual(token_list[8].value, 'x')
        self.assertEqual(token_list[9].type, 'EQUALS')
        self.assertEqual(token_list[9].value, '=')
        self.assertEqual(token_list[10].type, 'STRING')
        self.assertEqual(token_list[10].value, "hello world")
        self.assertEqual(token_list[11].type, 'SEMI')
        self.assertEqual(token_list[11].value, ';')
        self.assertEqual(token_list[12].type, 'RBRACE')
        self.assertEqual(token_list[12].value, '}')

    def test_double_quote_escape(self):
        data = '''
        def int main() {
            var str x = "hello\\" world";
        }
        '''

        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)
        self.assertEqual(token_list[0].type, 'DEF')
        self.assertEqual(token_list[0].value, 'def')
        self.assertEqual(token_list[1].type, 'INT')
        self.assertEqual(token_list[1].value, 'int')
        self.assertEqual(token_list[2].type, 'ID')
        self.assertEqual(token_list[2].value, 'main')
        self.assertEqual(token_list[3].type, 'LPAREN')
        self.assertEqual(token_list[3].value, '(')
        self.assertEqual(token_list[4].type, 'RPAREN')
        self.assertEqual(token_list[4].value, ')')
        self.assertEqual(token_list[5].type, 'LBRACE')
        self.assertEqual(token_list[5].value, '{')
        self.assertEqual(token_list[6].type, 'VAR')
        self.assertEqual(token_list[6].value, 'var')
        self.assertEqual(token_list[7].type, 'STR')
        self.assertEqual(token_list[7].value, 'str')
        self.assertEqual(token_list[8].type, 'ID')
        self.assertEqual(token_list[8].value, 'x')
        self.assertEqual(token_list[9].type, 'EQUALS')
        self.assertEqual(token_list[9].value, '=')
        self.assertEqual(token_list[10].type, 'STRING')
        self.assertEqual(token_list[10].value, "hello\" world")
        self.assertEqual(token_list[11].type, 'SEMI')
        self.assertEqual(token_list[11].value, ';')
        self.assertEqual(token_list[12].type, 'RBRACE')
        self.assertEqual(token_list[12].value, '}')
    
    def test_id(self):
        data = '''
        # This is a comment
        x + 2
        '''
        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)
        self.assertEqual(token_list[0].type, 'ID')
        self.assertEqual(token_list[0].value, 'x')
        self.assertEqual(token_list[1].type, 'PLUS')
        self.assertEqual(token_list[1].value, '+')
        self.assertEqual(token_list[2].type, 'NUMBER')
        self.assertEqual(token_list[2].value, 2)
    
    def test_reserved(self):
        data = '''
        def int main(str something) {
            var int x = 0;
        }
        '''

        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)
        self.assertEqual(token_list[0].type, 'DEF')
        self.assertEqual(token_list[0].value, 'def')
        self.assertEqual(token_list[1].type, 'INT')
        self.assertEqual(token_list[1].value, 'int')
        self.assertEqual(token_list[2].type, 'ID')
        self.assertEqual(token_list[2].value, 'main')
        self.assertEqual(token_list[3].type, 'LPAREN')
        self.assertEqual(token_list[3].value, '(')
        self.assertEqual(token_list[4].type, 'STR')
        self.assertEqual(token_list[4].value, 'str')
        self.assertEqual(token_list[5].type, 'ID')
        self.assertEqual(token_list[5].value, 'something')
        self.assertEqual(token_list[6].type, 'RPAREN')
        self.assertEqual(token_list[6].value, ')')
        self.assertEqual(token_list[7].type, 'LBRACE')
        self.assertEqual(token_list[7].value, '{')
        self.assertEqual(token_list[8].type, 'VAR')
        self.assertEqual(token_list[8].value, 'var')
        self.assertEqual(token_list[9].type, 'INT')
        self.assertEqual(token_list[9].value, 'int')
        self.assertEqual(token_list[10].type, 'ID')
        self.assertEqual(token_list[10].value, 'x')
        self.assertEqual(token_list[11].type, 'EQUALS')
        self.assertEqual(token_list[11].value, '=')
        self.assertEqual(token_list[12].type, 'NUMBER')
        self.assertEqual(token_list[12].value, 0)
        self.assertEqual(token_list[13].type, 'SEMI')
        self.assertEqual(token_list[13].value, ';')
        self.assertEqual(token_list[14].type, 'RBRACE')
        self.assertEqual(token_list[14].value, '}')

    def test_line_number(self):
        def assert_with_while(number_of_tokens, lineno):
            nonlocal counter
            bound = counter + number_of_tokens
            while counter < bound:
                print(token_list[counter].lineno, lineno)
                self.assertEqual(token_list[counter].lineno, lineno)
                counter += 1


        data = '''
        def int main() {




            var int y = 1;
        }
        '''

        tokenizer = Tokenizer()
        token_list = tokenizer.tokenize(data)

        counter = 0
        # 6 tokens in line 2
        assert_with_while(6, 2)
        # 6 tokens in line 7
        assert_with_while(6, 7)
        # 1 token in line 8
        assert_with_while(1, 8)


if __name__ == '__main__':
    unittest.main()