from itertools import cycle


class Cipher:
    alpha = 'abcdefghijklmnopqrstuvwxyz'

    @classmethod
    def get_char(cls, n):
        return cls.alpha[n % 26]


class Caesar(Cipher):
    @classmethod
    def encode(cls, text, n=5):
        res = [Cipher.get_char(cls.alpha.index(c) + n) if c in cls.alpha else c for c in text]
        return ''.join(res)

    @classmethod
    def decode(cls, text, n=5):
        return cls.encode(text, -n)


class Rot13:
    @classmethod
    def encode(cls, text):
        return Caesar.encode(text, 13)

    @classmethod
    def decode(cls, text):
        return cls.encode(text)


class Vigenere(Cipher):
    @classmethod
    def __process(cls, text, key, fn):
        result = ''
        key = key.replace(' ', '')
        for a, b in zip(text, cycle(key)):
            result += cls.get_char(
                fn(cls.alpha.index(a), cls.alpha.index(b))
            ) if a in cls.alpha else a
        return result

    @classmethod
    def decode(cls, text, key):
        return cls.__process(text, key, lambda x, y: x - y)

    @classmethod
    def encode(cls, text, key):
        return cls.__process(text, key, lambda x, y: x + y)
