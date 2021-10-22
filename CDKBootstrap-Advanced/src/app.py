from aws_cdk import core

class DummyStack(core.Stack):
    def __init__(self, app: core.App, id: str) -> None:
        super().__init__(app, id)

app = core.App()
DummyStack(app, "DummyStack")

app.synth()
