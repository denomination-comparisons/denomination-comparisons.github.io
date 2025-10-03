class CurriculaMapper:
    def __init__(self):
        # Mapping CEFR to other standards
        self.cefr_to_ib = {
            'A1': 'Phase 1',
            'A2': 'Phase 2',
            'B1': 'Phase 3',
            'B2': 'Phase 4',
            'C1': 'Phase 5',
            'C2': 'Phase 6'
        }
        self.cefr_to_cambridge = {
            'A1': 'KET',
            'A2': 'PET',
            'B1': 'FCE',
            'B2': 'CAE',
            'C1': 'CPE',
            'C2': 'CPE Advanced'
        }

    def map_to_ib(self, cefr_level):
        return self.cefr_to_ib.get(cefr_level, cefr_level)

    def map_to_cambridge(self, cefr_level):
        return self.cefr_to_cambridge.get(cefr_level, cefr_level)