from argparse import ONE_OR_MORE, ArgumentParser, Namespace
from typing import Any, Dict, List, Optional

from gnome_extensions_cli.schema import AvailableExtension

from ..icons import Color, Icons
from ..manager import ExtensionManager
from ..store import GnomeExtensionStore
from .show import build_url, print_key_value

INDENT = "  "


def configure(parser: ArgumentParser):
    parser.set_defaults(handler=run)
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="search for extensions"
    )
    parser.add_argument("-l", "--limit", type=int, default=0, help="limit to N items")
    parser.add_argument(
        "motif",
        nargs=ONE_OR_MORE,
        help="search motif",
    )


def run(args: Namespace, manager: ExtensionManager, store: GnomeExtensionStore):
    installed_extensions = {e.uuid: e for e in manager.list_installed_extensions()}

    results = list(store.search(" ".join(args.motif), limit=args.limit))
    for index, available_ext in enumerate(results, 1):
        installed_ext = installed_extensions.get(available_ext.uuid)
        print(
            Icons.DOT_BLUE if installed_ext is not None else Icons.DOT_WHITE,
            f"[{index}/{len(results)}]",
            Color.DEFAULT(available_ext.name, style="bright"),
            f"({Color.YELLOW(available_ext.uuid)})",
        )
        print_key_value("link", build_url(store.url, available_ext.link), 1)
        print_key_value("screenshot", build_url(store.url, available_ext.screenshot), 1)
        print_key_value("creator", available_ext.creator, 1)
        print_key_value("recommended version", available_ext.version, 1)
        if installed_ext is not None:
            print_key_value("installed version", installed_ext.metadata.version, 1)
        if args.verbose:
            print_key_value("description", available_ext.description, 1)

        print("-" * 80)
