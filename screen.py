class Screen():
    def print(self, contents: str) -> None:
        print(contents)


class TestScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.contents = ""

    def print(self, contents: str):
        self.contents += contents + "\n"

    def get_contents(self) -> str:
        return self.contents
