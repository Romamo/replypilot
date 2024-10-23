import re
from dataclasses import dataclass


@dataclass
class AppID:
    store: str
    id: str


class Detector:
    _RE_ID = re.compile(r'(?:/store/apps/details\?id=|https://www.appbrain.com/app/[\w-]+/|^)(?P<play_id>\w+\.[\w.]+)|(id|^)(?P<ios_id>\d{9,10})')

    @classmethod
    def parse(cls, s):
        m = cls._RE_ID.search(s)
        if m:
            d = m.groupdict()
            if d['play_id']:
                return AppID('play', d['play_id'])
            elif d['ios_id']:
                return AppID('ios', d['ios_id'])
