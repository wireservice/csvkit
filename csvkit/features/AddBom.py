from argparse import ArgumentParser, Namespace
from io import TextIOWrapper, BytesIO
from typing import Union


class AddBOM:

    @staticmethod
    def _get_BOM() -> bytes:

        from codecs import BOM_UTF8

        return BOM_UTF8

    @staticmethod
    def enabled(arguments: Union[Namespace,list, None] = None) -> bool:

        if isinstance(arguments, Namespace) or isinstance(arguments, list):
            return "add_bom" in arguments and arguments.add_bom

        return False

    @staticmethod
    def argument(arguments: ArgumentParser, utility: object):

        # These string usage to validate the class  is an architecture
        # fail as is not possible to check the class type before
        # is initialized

        if "SQL2CSV" in str(utility.__class__):
            return

        if "CSVPy" in str(utility.__class__):
            return

        arguments.add_argument(
            "--add-bom",
            dest="add_bom",
            action="store_true",
            default=False,
            help="Add Byte Order Mark (BOM) to the output",
        )

    @staticmethod
    def run(
        output: TextIOWrapper,
        arguments: Union[Namespace, None] = None,
    ):

        if not AddBOM.enabled(arguments):
            return

        BOM = AddBOM._get_BOM()
        output.buffer.write(BOM)
