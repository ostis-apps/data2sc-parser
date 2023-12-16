from aspose.cells import Workbook


def repair_xlsx(source: str, destination: str) -> None:
    """
    Repairs and overrides broken xlsx file.
    """
    workbook = Workbook(source)
    workbook.save(destination)
