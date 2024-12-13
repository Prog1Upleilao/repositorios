from rich import print

__project__ = "FANSTASMA"
__author__ = "Dom Zeck I"
__version__ = "2.0.0"


def print_project_information():
    """ Imprimir os valores de metadatas"""
    
    tab = 70
    print(f"[yellow]" + tab * " " + "*" * 33)

    text = f"       Projeto: [bold cyan]{__project__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    text = f"       Autor:   [bold cyan]{__author__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    text = f"       Versão:  [bold cyan]{__version__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    print("[yellow]" + tab * " " + "*" * 33)

if __name__ == "__main__":
    print_project_information()