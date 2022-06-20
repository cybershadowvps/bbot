import csv
import json

from .base import BaseOutputModule


class Line:
    def __init__(self):
        self._line = None

    def write(self, line):
        self._line = line

    def read(self):
        return self._line


class CSV(BaseOutputModule):
    def setup(self):
        self.line = Line()
        self.writer = csv.writer(self.line)
        self.writer.writerow(
            ["Event type", "Event data", "Source Module", "Event ID", "Event Tags", "Source Event ID"]
        )
        self.stdout(self.line.read().strip())
        return True

    def handle_event(self, event):
        self.writer.writerow(
            [
                getattr(event, "type", ""),
                getattr(event, "data", ""),
                str(getattr(event, "module", "")),
                getattr(event, "id", ""),
                json.dumps(sorted(list(getattr(event, "tags", [])))),
                getattr(event, "source_id", ""),
            ]
        )
        self.stdout(self.line.read().strip())
