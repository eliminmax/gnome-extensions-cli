from dataclasses import dataclass
from itertools import count
from typing import Iterable, Optional, Union

import requests

from .schema import AvailableExtension, Search


@dataclass
class GnomeExtensionStore:
    """
    Interface to search for extensions on Gnome Website
    """

    url: str = "https://extensions.gnome.org"
    timeout: int = 20

    def find(
        self, ext: Union[str, int], shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its uuid or pk
        """
        if isinstance(ext, int):
            return self.find_by_pk(ext, shell_version=shell_version)
        if isinstance(ext, str) and ext.isnumeric():
            return self.find_by_pk(int(ext), shell_version=shell_version)
        return self.find_by_uuid(ext, shell_version=shell_version)

    def find_by_uuid(
        self, uuid: str, shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its uuid
        """
        params = {"uuid": uuid}
        if shell_version is not None:
            params["shell_version"] = str(shell_version)
        resp = requests.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return AvailableExtension.parse_raw(resp.content)

    def find_by_pk(
        self, pk: int, shell_version: Optional[str] = None
    ) -> Optional[AvailableExtension]:
        """
        Find an extension by its pk
        """
        params = {"pk": str(pk)}
        if shell_version is not None:
            params["shell_version"] = str(shell_version)
        resp = requests.get(
            f"{self.url}/extension-info/",
            params=params,
            timeout=self.timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return AvailableExtension.parse_raw(resp.content)

    def search(
        self, motif: str, shell_version: str = "all", limit: int = 0
    ) -> Iterable[AvailableExtension]:
        """
        Search for extensions
        """
        params = {"search": motif, "shell_version": shell_version, "page": 1}
        count = 0
        while True:
            resp = requests.get(
                f"{self.url}/extension-query/",
                params=params,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            data = Search.parse_raw(resp.content)
            for ext in data.extensions:
                yield ext
                count += 1
                if 0 < limit <= count:
                    return
            if params["page"] >= data.numpages:
                break
            params["page"] += 1
