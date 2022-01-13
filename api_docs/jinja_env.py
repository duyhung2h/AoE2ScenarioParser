from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / 'templates'),
    autoescape=select_autoescape(),
    trim_blocks=True
)

file_template = env.get_template("file.j2")
