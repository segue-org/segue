from datetime import datetime
from decimal import Decimal

DATE_FORMAT = "%d%m%Y"

class BoletoFileParser(object):
    def parse(self, content):
        lines = content.split("\n")
        useful_lines = filter(self._is_line, lines)
        return map(self._parse_line, useful_lines)

    def _is_line(self, line):
        return len(line) > 0

    def _parse_line(self, line):
        parts = line.split(";")

        our_number      = parts[4][10:-1]
        payment_date    = parts[8]
        amount          = parts[10]

        return dict(
            our_number   = int(our_number),
            payment_date = datetime.strptime(payment_date, DATE_FORMAT).date(),
            amount       = Decimal(amount) / 100,
            line         = line,
            received_at  = datetime.now()
        )
