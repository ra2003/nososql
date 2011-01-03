###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

import re

from nososql import tokens


class Token(object):

    def __init__(self, type, text):
        self.type = type
        self.text = text

    def __str__(self):
        return "<'{text}', {name}>".format(text=self.text, name=self.type)


class LexerException(Exception):

    def __init__(self, msg, pos):
        self.msg = msg
        self.pos = pos

    def __str__(self):
        return 'Error at position: %s - %s' % (self.pos, self.msg)


class Lexer(object):

    RULES = [
        (r'print', tokens.PRINT_KW),
        (r'create', tokens.CREATE_KW),
        (r'table', tokens.TABLE_KW),
        (r'primary', tokens.PRIMARY_KW),
        (r'key', tokens.KEY_KW),
        (r'insert', tokens.INSERT_KW),
        (r'into', tokens.INTO_KW),
        (r'set', tokens.SET_KW),
        (r'select', tokens.SELECT_KW),
        (r'from', tokens.FROM_KW),
        (r'where', tokens.WHERE_KW),
        (r'[a-zA-Z_]+\d*', tokens.ID),
        (r'\d+', tokens.INT),
        (r"'[^']*'", tokens.STRING),
        (r'\(', tokens.LPAREN),
        (r'\)', tokens.RPAREN),
        (r',', tokens.COMMA),
        (r';', tokens.SEMICOLON),
        (r'=', tokens.EQUALS),
        ]

    IS_WHITESPACE = re.compile(r'\s+').match
    IS_COMMENT = re.compile(r'#.*').match

    def __init__(self, buffer):
        self.buffer = buffer
        self.pos = 0
        self.regexp = self._build_master_regexp()

    def _build_master_regexp(self):
        result = []
        for regexp, group_name in self.RULES:
            result.append(r'(?P<%s>%s)' % (group_name, regexp))

        master_regexp = re.compile('|'.join(result), re.MULTILINE)
        return master_regexp

    def token(self):
        buffer, regexp = self.buffer, self.regexp
        IS_WHITESPACE = self.IS_WHITESPACE
        IS_COMMENT = self.IS_COMMENT
        end = len(buffer)

        while True:
            match = (IS_WHITESPACE(buffer, self.pos) or
                     IS_COMMENT(buffer, self.pos))

            if match is not None:
                self.pos = match.end()
            else:
                break

        # the end
        if self.pos >= end:
            return Token(tokens.EOF, 'EOF')

        match = regexp.match(buffer, self.pos)
        if match is None:
            raise LexerException('No valid token', self.pos)

        self.pos = match.end()

        group_name = match.lastgroup
        token = Token(group_name, match.group(group_name))
        return token

    def __iter__(self):
        return self.next()

    def next(self):
        while True:
            token = self.token()
            if tokens.type == tokens.EOF:
                yield token
                return
            yield token
