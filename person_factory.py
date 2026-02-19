import random
from typing import Dict, List, Tuple
from person import Person
from utils import get_decade_string


class PersonFactory:
    """
    Factory class for creating Person objects based on data from CSV files.

    Attributes:
        life_expectancy: Dictionary mapping year to life expectancy
        first_names: Nested dictionary of first names by decade and gender
        gender_probability: Dictionary mapping decade to probability of gendered name
        last_names: Nested dictionary of last names by decade and rank
        rank_probabilities: List of probabilities corresponding to ranks 1-30
        birth_marriage_rates: Dictionary of birth and marriage rates by decade
    """

    def __init__(self):
        """Initialize the PersonFactory with empty data structures."""
        self.life_expectancy: Dict[int, float] = {}
        self.first_names: Dict[str, Dict[str, Dict[str, float]]] = {}
        self.gender_probability: Dict[str, Dict[str, float]] = {} # Extra requirement for grad student
        self.last_names: Dict[str, Dict[str, int]] = {}
        self.rank_probabilities: Dict[int, float] = {}
        self.birth_marriage_rates: Dict[str, Dict[str, float]] = {}
        self.last_names_with_frequencies: Dict[str, Dict[str, float]] = {} # convenience structure for last name selection

    def read_files(self):
        """Read all data files needed for person generation."""
        self.read_life_expectancy()
        self.read_first_names()
        self.read_gender_probability()
        self.read_last_names()
        self.read_rank_to_probability()
        self.read_birth_marriage_rates()
        self.build_last_names_with_frequencies()

###################### File reading methods ######################

    def read_life_expectancy(self):
        """
        Read life_expectancy.csv and store in dictionary.
        Format: {year: life_expectancy}
        """
        with open('life_expectancy.csv') as file:
            file.readline() # Skip header line
            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    year = int(parts[0])
                    expectancy = float(parts[1])
                    self.life_expectancy[year] = expectancy

    def read_first_names(self):
        """
        Read first_names.csv and store in nested dictionary.
        Format: {decade: {gender: {name: frequency, ...}}}
        """
        with open('first_names.csv') as file:
            file.readline() # Skip header line
            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]  
                    gender = parts[1]
                    name = parts[2]
                    frequency = float(parts[3])

                    # Initialize nested dictionaries if empty
                    if decade not in self.first_names:
                        self.first_names[decade] = {}
                    if gender not in self.first_names[decade]:
                        self.first_names[decade][gender] = {}

                    self.first_names[decade][gender][name] = frequency # Assuming a gendered name can only have one frequency per decade

    def read_gender_probability(self):
        """
        Extra requirement for grad student: read gender_name_probability.csv and store in dictionary.
        Format: {decade: {gender: probability}}
        """
        with open('gender_name_probability.csv') as file:
            file.readline() # Skip header line
            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]
                    gender = parts[1]
                    probability = float(parts[2])

                    # Initialize nested dictionary if needed
                    if decade not in self.gender_probability:
                        self.gender_probability[decade] = {}

                    self.gender_probability[decade][gender] = probability

    def read_last_names(self):
        """
        Read last_names.csv and store in nested dictionary.
        Format: {decade: {name: rank, ...}}
        """
        with open('last_names.csv') as file:
            file.readline() # Skip header line
            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0] 
                    rank = int(parts[1])
                    last_name = parts[2]

                    if decade not in self.last_names:
                        self.last_names[decade] = {}

                    self.last_names[decade][last_name] = rank # Assuming a last name can only have one rank per decade

    def read_rank_to_probability(self):
        """
        Read rank_to_probability.csv and store as dictionary.
        Format: {rank: probability}
        """
        with open('rank_to_probability.csv') as file:
            # Read the first and only line
            line = file.readline().rstrip()
            if line:
                # Split by comma to get individual probabilities
                prob_strings = line.split(',')

                # Convert to float and store in dictionary, with index+1 as rank (rank 1 = index 0)
                self.rank_probabilities = {i + 1: float(prob_str) for i, prob_str in enumerate(prob_strings)}

    def read_birth_marriage_rates(self):
        """
        Read birth_and_marriage_rates.csv and store in dictionary.
        Format: {decade: {'birth_rate': float, 'marriage_rate': float}}
        """
        with open('birth_and_marriage_rates.csv') as file:
            file.readline() # Skip header line
            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]
                    birth_rate = float(parts[1])
                    marriage_rate = float(parts[2])

                    self.birth_marriage_rates[decade] = {
                        'birth_rate': birth_rate,
                        'marriage_rate': marriage_rate
                    }
    
    def build_last_names_with_frequencies(self):
        """
        Build a nested dictionary of last names with their corresponding probabilities based on rank.
        Format: {decade: {last_name: probability, ...}}
        """
        for decade, names_with_ranks in self.last_names.items():
            self.last_names_with_frequencies[decade] = {}
            for name, rank in names_with_ranks.items():
                self.last_names_with_frequencies[decade][name] = self.rank_probabilities[rank]

###################### Person attribute methods ######################

    def get_year_died(self, year_born: int) -> int:
        """
        Calculate the year a person died based on life expectancy.

        Args:
            year_born: The year the person was born
        Returns:
            The year the person died (life expectancy +/- 10 years)
        """
        # Get life expectancy for the birth year, rounded down to the integer year
        expectancy = int(self.life_expectancy[year_born])

        # Add random variation of +/- 10 years
        variation = random.randint(-10, 10)
        years_lived = expectancy + variation

        return year_born + years_lived

    def get_first_name(self, year_born: int, gender: str) -> str:
        """
        Select a first name based on year born, gender, and frequency data.

        Args:
            year_born: The year the person was born
            gender: The person's gender ('male' or 'female')
        Returns:
            A randomly selected first name based on frequency distributions
        """
        decade = get_decade_string(year_born)
        names_with_freq = self.first_names[decade][gender]

        # Extract names and frequencies as lists for random.choices
        names = list(names_with_freq.keys())
        frequencies = list(names_with_freq.values())

        return random.choices(names, weights=frequencies)[0]

    def get_last_name(self, year_born: int, is_descendant: bool,
                     original_last_names: List[str]) -> str:
        """
        Select a last name based on descendant status and birth decade.

        Args:
            year_born: Year the person was born
            is_descendant: True if person is descended from original two people
            original_last_names: List of last names from the original ancestors
        Returns:
            A last name
        """
        if is_descendant:
            # Randomly choose from original last names
            return random.choice(original_last_names)

        decade = get_decade_string(year_born)
        names_with_frequencies = self.last_names_with_frequencies[decade]

        names = list(names_with_frequencies.keys())
        weights = list(names_with_frequencies.values())

        return random.choices(names, weights=weights)[0]

    def assign_gender(self, year_born: int) -> str:
        """
        Extra requirement for grad student: assign a gender based on gender probabilities by decade.

        Args:
            year_born: The year the person was born

        Returns:
            A gender ('male' or 'female') based on probabilities for the birth decade
        """
        decade = get_decade_string(year_born)

        # Use the gender probability for this decade
        gender_probs = self.gender_probability[decade]

        genders = list(gender_probs.keys())
        probabilities = list(gender_probs.values())
        return random.choices(genders, weights=probabilities)[0]


###################### Person creation methods ######################
        
    def create_person(self, year_born: int, gender: str, is_descendant: bool,
                     original_last_names: List[str],
                     parents: Tuple[Person, Person] | None = None) -> Person:
        """
        Create a new Person instance with all attributes generated.

        Args:
            year_born: Year the person was born
            gender: Person's gender ('male' or 'female')
            is_descendant: True if descended from original ancestors
            original_last_names: List of original ancestor last names
            parents: Tuple of (parent1, parent2) or None

        Returns:
            A new Person object
        """
        year_died = self.get_year_died(year_born)
        first_name = self.get_first_name(year_born, gender)
        last_name = self.get_last_name(year_born, is_descendant, original_last_names)

        person = Person(year_born, year_died, first_name, last_name, gender, parents)

        return person

    def should_have_partner(self, year_born: int) -> bool:
        """
        Determine if a person should have a partner based on marriage rates.

        Args:
            year_born: The year the person was born

        Returns:
            True if person should have a partner, False otherwise
        """
        decade = get_decade_string(year_born)
        marriage_rate = self.birth_marriage_rates[decade]['marriage_rate']

        # boolean decision based on marriage rate, reference: https://stackoverflow.com/questions/5886987/true-or-false-output-based-on-a-probability
        return random.random() < marriage_rate

    def create_partner(self, person: Person, is_descendant: bool,
                      original_last_names: List[str]) -> Person | None:
        """
        Create a partner for the given person.

        Args:
            person: The person who needs a partner
            is_descendant: True if partner is descended from original ancestors
            original_last_names: List of original ancestor last names

        Returns:
            A new Person object as the partner or None if partner cannot be created
        """
        # Partner's birth year is within +/- 10 years
        partner_year_born = person.get_year_born() + random.randint(-10, 10)

        if partner_year_born > 2120: 
            return None # If the calculated birth year is beyond 2120, we cannot generate a partner due to lack of csv data 

        # Partner's gender is NOT assumed to be the opposite
        partner_gender = self.assign_gender(partner_year_born)

        partner = self.create_person(partner_year_born, partner_gender,
                                     is_descendant, original_last_names, parents=None)

        # Link the person with the partner
        person.set_partner(partner)
        partner.set_partner(person)

        return partner
