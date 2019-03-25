import unittest
from cipher import Caesar, Rot13, Vigenere


class TestCipherMixin:
    text = 'the quick brown fox jumps over the lazy dog'

    def encode(self, text):
        raise NotImplementedError

    def decode(self, code):
        raise NotImplementedError

    def test_encode(self):
        code = self.encode(self.text)
        self.assertNotEqual(code, self.text)  # Закодированный текст отличается от исходого
        self.assertEqual(len(code), len(self.text))  # Длина закодированного и исходного текста совпадает

    def test_decode(self):
        decoded = self.decode(self.encode(self.text))
        self.assertEqual(decoded, self.text)  # Раскодированный шифр совпадает с исходным текстом


class TestCaesar(TestCipherMixin, unittest.TestCase):
    def encode(self, text):
        return Caesar.encode(text, 5)

    def decode(self, code):
        return Caesar.decode(code, 5)


class TestRot13(TestCipherMixin, unittest.TestCase):
    def encode(self, text):
        return Rot13.encode(text)

    def decode(self, code):
        return Rot13.decode(code)


class TestVigenere(unittest.TestCase):
    text = 'the five boxing wizards jump quickly'
    key = 'hello world'

    def test_encode(self):
        code = Vigenere.encode(self.text, self.key)
        self.assertNotEqual(code, self.text)
        self.assertEqual(len(code), len(self.text))
        #self.assertCountEqual(self.text, code)

    def test_decode(self):
        code = Vigenere.encode(self.text, self.key)
        decoded = Vigenere.decode(code, self.key)
        self.assertEqual(decoded, self.text)

if __name__ == '__main__':
    unittest.main()
