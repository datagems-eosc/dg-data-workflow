from enum import Enum


class DataLocationKind(Enum):
    File = 0
    Http = 1
    Ftp = 2
    Remote = 3
    Staged = 4
    Database = 5
