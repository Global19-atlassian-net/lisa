import re
from typing import Optional, Type

from lisa.executable import Tool


class Lscpu(Tool):
    __pattern_cores_per_socket = re.compile(r"^Core\(s\) per socket:[ ]+([\d]+)$", re.M)
    __pattern_sockets = re.compile(r"^Socket\(s\):[ ]+([\d]+)$", re.M)

    def _initialize(self) -> None:
        self._core_count: Optional[int] = None

    @property
    def command(self) -> str:
        return "lscpu"

    @classmethod
    def _windows_tool(cls) -> Optional[Type[Tool]]:
        return WindowsLscpu

    def _check_exists(self) -> bool:
        return True

    def get_core_count(self, force: bool = False) -> int:
        if self._core_count is None or force:
            result = self.run(no_info_log=True)
            matched = self.__pattern_cores_per_socket.findall(result.stdout)
            assert len(matched) == 1, "cores per socket should have exact one line"
            core_per_socket = int(matched[0])
            matched = self.__pattern_sockets.findall(result.stdout)
            assert len(matched) == 1, "sockets should have exact one line"
            sockets = int(matched[0])
            self._core_count = sockets * core_per_socket
        return self._core_count


class WindowsLscpu(Lscpu):
    @property
    def command(self) -> str:
        return "wmic cpu get"

    def get_core_count(self, force: bool = False) -> int:
        if self._core_count is None or force:
            result = self.run("NumberOfCores", no_info_log=True)
            lines = result.stdout.splitlines(keepends=False)
            assert "NumberOfCores" == lines[0]
            self._core_count = int(lines[1])
        return self._core_count