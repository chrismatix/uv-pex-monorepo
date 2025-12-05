import typer
from rich import print
from rich.panel import Panel
from rich.console import Console

from format.make_sarcastic import make_sarcastic

# Optional import of generated protobuf types for demo usage
try:
    from pb import sarcasm_pb2 as demo_pb2  # type: ignore
except Exception:
    demo_pb2 = None  # fallback to plain strings

app = typer.Typer(
    help="Convert boring text into sArCaStIc text with style!"
)

console = Console()


@app.command()
def convert(
        text: str = typer.Argument(..., help="The text to make sarcastic"),
        rainbow: bool = typer.Option(
            False, "--rainbow", "-r",
            help="Make it rainbow colored (because why not?)"
        ),
):
    """
    Convert your boring text into something more... interesting 💅
    """
    result = make_sarcastic(text)

    # If protobuf stubs are available, demonstrate constructing the messages
    if demo_pb2 is not None:
        req = demo_pb2.SarcasticRequest(text=text)
        resp = demo_pb2.SarcasticResponse(original=req.text, sarcastic=result)
        display_text = resp.sarcastic
    else:
        display_text = result

    if rainbow:
        print(Panel(
            display_text,
            title="[bold]Your sarcastic text[/bold]",
            border_style="rainbow",
            padding=(1, 2)
        ))
    else:
        print(Panel(
            display_text,
            title="[bold]Your sarcastic text[/bold]",
            border_style="blue",
            padding=(1, 2)
        ))

