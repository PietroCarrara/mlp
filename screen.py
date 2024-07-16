class Screen():
    def print(self, contents: str) -> None:
        raise Exception("not implemented")


class TestScreen(Screen):
    def __init__(self) -> None:
        super().__init__()
        self.contents = ""

    def print(self, contents: str):
        self.contents += contents + "\n"

    def get_contents(self) -> str:
        return self.contents
