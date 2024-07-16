class StringReader():
    def __init__(self, string: str) -> None:
        self.string = string
        self.position = 0
        self.end = len(string)

    def next_number(self) -> int | None:
        signal = 1
        value = 0
        found_at_least_one_digit = False

        if self.compare_advance('-'):
            signal = -1
        while True:
            char = self.peek()
            if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                found_at_least_one_digit = True
                value = value*10 + int(char)
                self.advance()
            else:
                break

        if not found_at_least_one_digit:
            if signal == -1:  # Give back the minus sign
                self.retreat()
            return None

        return value * signal

    def next_word(self) -> str | None:
        word = ''
        while True:
            match self.peek():
                case " " | "(" | ")" | "\n" | "\t":
                    return None if word == '' else word

                case character:
                    if character is None:
                        return None if word == '' else word
                    self.advance()
                    word += character

    def skip_whitespaces(self):
        while self.size() > 0 and self.peek() in [' ', '\t', '\n']:
            self.advance()

    def peek(self) -> str | None:
        if self.size() <= 0:
            return None
        return self.string[self.position]

    def advance(self):
        if self.size() > 0:
            self.position += 1

    def retreat(self):
        if self.position > 0:
            self.position -= 1

    def compare_advance(self, character: str) -> bool:
        assert len(character) == 1

        if self.peek() == character:
            self.advance()
            return True

        return False

    def size(self):
        return self.end - self.position

    def with_location(self, exception: Exception) -> Exception:
        line = 1
        char = 1

        for token in self.string[:self.position]:
            if token == '\n':
                line += 1
                char = 1
            else:
                char += 1

        return Exception(f"line {line}, character {char}: {exception}")
