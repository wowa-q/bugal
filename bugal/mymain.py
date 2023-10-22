# pylint: skip-file
# flake8: noqa

from enum import Enum
import re

class MyEnum(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

# Alle Attribute der Enum-Klasse abrufen
all_attributes = dir(MyEnum)

# Nur die tatsächlichen Enum-Mitglieder (Attribute) auswählen
enum_attributes = [attr for attr in all_attributes if not attr.startswith('_')]

# Die Liste der Enum-Mitglieder ausgeben
# print(enum_attributes)

# if 'FIRST' in enum_attributes:
#     print('gefunden')

def _make_int(value: str) -> int:
    # Verwenden Sie einen regulären Ausdruck, um nur Zahlen und Dezimalpunkt zu behalten
    cleaned_string = re.sub(r'[^\d.]', '', value)
    print(float(cleaned_string))
    value.replace(',', '.')
    value.replace('\xa0€', '')
    print(value)
    value.replace(' €', '')
    print(value)
    cleaned_string = value[:-2]
    print(cleaned_string)
    print(len(cleaned_string))

def _make_num(value: str) -> float:
        # cleaned_string = value[:-2]
        if '€' in value: print('€')
        cleaned_string = value.replace(' €', '')
        cleaned_string = cleaned_string.replace(',', '.')
        print(cleaned_string)
        # print(float(cleaned_string))
        # return float(cleaned_string)

if __name__ == "__main__":
    #_make_int("200.00 €")
    s1 = '-40,00\xa0€'
    #_make_int(s1)
    _make_num(s1)
