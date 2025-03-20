
class Airport():
    def __init__(self):
        self.dictionary = {
            'BER': 'Berlin',
            'BIO': 'Bilbao',
            'BRE': 'Bremen',
            'GRX': 'Granada',
            'LBC': 'Lubeck',
            'HAM': 'Hamburg',
            'MAD': 'Madrid',
            'AGP': 'Malaga',
            'FMM': 'Memmingen',
            'MUC': 'Munich',
            'SVQ': 'Sevilla',
            'VIT': 'Vitoria',
            
            # 'Berlin': 'BER',
            # 'Bilbao': 'BIO',
            # 'Bremen': 'BRE',
            # 'Granada': 'GRX',
            # 'Lubeck': 'LBC',
            # 'Hamburg': 'HAM',
            # 'Madrid': 'MAD',
            # 'Malaga': 'AGP',
            # 'Memmingen': 'FMM',
            # 'Munich': 'MUC',
            # 'Sevilla': 'SVQ',
            # 'Vitoria': 'VIT',
        }

    def to_iata(self, airport_name):
        return self.dictionary[airport_name]
    