from pathlib import Path
from generators.generator import Generator
from generators.mets_generator import METSGenerator
from generators.html_generator import HTMLGenerator
from generators.mods_generator import MODSGenerator
from generators.pdf_generator import PDFGenerator
from generators.txt_generator import TXTGenerator
from clients import CeoItem


class IssueGenerator(Generator):
    def __init__(self) -> None:
        super().__init__()



    def generate(self) -> None:
        pass



    def dump(self, output_path: str | Path) -> None:
        pass
