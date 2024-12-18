from rich import print

__project__ = "Verificador de precatórios"
__author__ = "Dom Zeck I"
__version__ = "1.0"


def print_project_information():
    """ Imprimir os valores de metadatas"""
    
    tab = 5
    num_asteriscos = 50
    print(f"[yellow]" + tab * " " + "*" * num_asteriscos)

    text = f"       Projeto: [bold cyan]{__project__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    text = f"       Autor:   [bold cyan]{__author__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    text = f"       Versão:  [bold cyan]{__version__}[/bold cyan]"
    text = f"{text}{' ' * (39 - len(text))}"
    print(tab * " " + text)

    print("[yellow]" + tab * " " + "*" * num_asteriscos)

if __name__ == "__main__":
    print_project_information()