from generators.generator import Generator
from generators.html_generator import HTMLGenerator
from generators.mods_generator import MODSGenerator
from generators.pdf_generator import PDFGenerator
from generators.txt_generator import TXTGenerator
from clients import CeoItem


class METSGenerator(Generator):
    NSMAP = {
        "mets": "http://www.loc.gov/METS/",
        "mods": "http://www.loc.gov/mods/v3",
        "xlink": "http://www.w3.org/1999/xlink",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    def __init__(self) -> None:
        super().__init__()

        self._start_date:str | None = None
        self._end_date:str | None = None
