import random
from typing import List, Tuple, Optional
from person import Person


class PersonFactory:
    """
    Factory class for creating Person objects based on data from CSV files.

    Attributes:
        life_expectancy: Dictionary mapping year to life expectancy
        first_names: Nested dictionary of first names by decade and gender
        gender_probability: Dictionary mapping decade to probability of gendered name
        last_names: List of (last_name, rank) tuples
        rank_probabilities: List of probabilities corresponding to ranks 1-30
        birth_marriage_rates: Dictionary of birth and marriage rates by decade
    """

    def __init__(self):
        """Initialize the PersonFactory with empty data structures."""
        self.life_expectancy = {}
        self.first_names = {}
        self.gender_probability = {}
        self.last_names = []
        self.rank_probabilities = []
        self.birth_marriage_rates = {}

    def read_files(self):
        """Read all data files needed for person generation."""
        self.read_life_expectancy()
        self.read_first_names()
        self.read_gender_probability()
        self.read_last_names()
        self.read_rank_to_probability()
        self.read_birth_marriage_rates()

    def read_life_expectancy(self):
        """
        Read life_expectancy.csv and store in dictionary.
        Format: {year: life_expectancy}
        """
        with open('life_expectancy.csv') as file:
            # Skip header line
            file.readline()

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
        Format: {decade: {gender: [(name, frequency), ...]}}
        """
        with open('first_names.csv') as file:
            # Skip header line
            file.readline()

            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]  # e.g., "1950s"
                    gender = parts[1]  # "male" or "female"
                    name = parts[2]
                    frequency = float(parts[3])

                    # Initialize nested dictionaries if needed
                    if decade not in self.first_names:
                        self.first_names[decade] = {}
                    if gender not in self.first_names[decade]:
                        self.first_names[decade][gender] = []

                    # Append (name, frequency) tuple
                    self.first_names[decade][gender].append((name, frequency))

    def read_gender_probability(self):
        """
        Read gender_name_probability.csv and store in dictionary.
        Format: {decade: {gender: probability}}
        """
        with open('gender_name_probability.csv') as file:
            # Skip header line
            file.readline()

            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]  # e.g., "1950s"
                    gender = parts[1]  # "male" or "female"
                    probability = float(parts[2])

                    # Initialize nested dictionary if needed
                    if decade not in self.gender_probability:
                        self.gender_probability[decade] = {}

                    self.gender_probability[decade][gender] = probability

    def read_last_names(self):
        """
        Read last_names.csv and store as list of (last_name, rank) tuples.
        Format: Decade,Rank,LastName
        """
        with open('last_names.csv') as file:
            # Skip header line
            file.readline()

            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    # Extract: Decade, Rank, LastName
                    rank = int(parts[1])
                    last_name = parts[2]
                    self.last_names.append((last_name, rank))

    def read_rank_to_probability(self):
        """
        Read rank_to_probability.csv and store as list.
        The CSV contains probabilities for ranks 1-30 in a single row.
        """
        with open('rank_to_probability.csv') as file:
            # Read the first line which contains all probabilities
            line = file.readline().rstrip()
            if line:
                # Split by comma to get individual probabilities
                prob_strings = line.split(',')
                self.rank_probabilities = [float(prob) for prob in prob_strings]

    def read_birth_marriage_rates(self):
        """
        Read birth_and_marriage_rates.csv and store in dictionary.
        Format: {decade: {'birth_rate': float, 'marriage_rate': float}}
        """
        with open('birth_and_marriage_rates.csv') as file:
            # Skip header line
            file.readline()

            for line in file:
                line = line.rstrip()
                if line:  # Skip empty lines
                    parts = line.split(',')
                    decade = parts[0]  # e.g., "1950s"
                    birth_rate = float(parts[1])
                    marriage_rate = float(parts[2])

                    self.birth_marriage_rates[decade] = {
                        'birth_rate': birth_rate,
                        'marriage_rate': marriage_rate
                    }

    def get_year_died(self, year_born: int) -> int:
        """
        Calculate the year a person died based on life expectancy.

        Args:
            year_born: The year the person was born

        Returns:
            The year the person died (life expectancy +/- 10 years)
        """
        # Get life expectancy for the birth year
        if year_born in self.life_expectancy:
            expectancy = self.life_expectancy[year_born]
        else:
            # If exact year not found, use closest available year
            closest_year = min(self.life_expectancy.keys(), key=lambda x: abs(x - year_born))
            expectancy = self.life_expectancy[closest_year]

        # Add random variation of +/- 10 years
        variation = random.randint(-10, 10)
        years_lived = int(expectancy) + variation

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
        # Determine the decade
        decade_num = (year_born // 10) * 10
        decade = f"{decade_num}s"

        # For CS 562: Use gender probability to determine if should use gendered name
        # The probability indicates likelihood of using a name matching their gender
        if decade in self.gender_probability and gender in self.gender_probability[decade]:
            use_gendered = random.random() < self.gender_probability[decade][gender]
        else:
            use_gendered = True

        # Get names for this decade and gender
        if use_gendered and decade in self.first_names and gender in self.first_names[decade]:
            names_with_freq = self.first_names[decade][gender]
        elif not use_gendered and decade in self.first_names:
            # Use opposite gender name
            opposite_gender = "female" if gender == "male" else "male"
            if opposite_gender in self.first_names[decade]:
                names_with_freq = self.first_names[decade][opposite_gender]
            else:
                # Fallback to own gender if opposite not available
                names_with_freq = self.first_names[decade].get(gender, [("Alex", 1.0)])
        else:
            # Fallback to 1950s if decade not found
            names_with_freq = self.first_names.get("1950s", {}).get(gender, [("John", 1.0)])

        # Extract names and frequencies
        names = [name for name, freq in names_with_freq]
        frequencies = [freq for name, freq in names_with_freq]

        # Select a name based on weighted probabilities
        selected_name = random.choices(names, weights=frequencies, k=1)[0]

        return selected_name

    def get_last_name(self, is_descendant: bool, original_last_names: List[str]) -> str:
        """
        Select a last name based on descendant status.

        Args:
            is_descendant: True if person is descended from original two people
            original_last_names: List of last names from the original ancestors

        Returns:
            A last name
        """
        if is_descendant:
            # Randomly choose from original last names
            return random.choice(original_last_names)
        else:
            # Use rank probabilities to select from last_names list
            # Only use first 30 names (matching rank_probabilities length)
            available_names = self.last_names[:min(30, len(self.last_names))]

            # Extract last names
            names = [name for name, rank in available_names]

            # Use rank probabilities as weights
            weights = self.rank_probabilities[:len(available_names)]

            # Select based on probability
            selected_name = random.choices(names, weights=weights, k=1)[0]

            return selected_name

    def create_person(self, year_born: int, gender: str, is_descendant: bool,
                     original_last_names: List[str],
                     parents: Optional[Tuple[Person, Person]] = None) -> Person:
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
        last_name = self.get_last_name(is_descendant, original_last_names)

        person = Person(year_born, first_name, last_name, gender, year_died, parents)

        return person

    def should_have_partner(self, year_born: int) -> bool:
        """
        Determine if a person should have a partner based on marriage rates.

        Args:
            year_born: The year the person was born

        Returns:
            True if person should have a partner, False otherwise
        """
        # Determine the decade
        decade_num = (year_born // 10) * 10
        decade = f"{decade_num}s"

        # Get marriage rate for this decade
        if decade in self.birth_marriage_rates:
            marriage_rate = self.birth_marriage_rates[decade]['marriage_rate']
        else:
            # Default to 0.5 if decade not found
            marriage_rate = 0.5

        # Random decision based on marriage rate
        return random.random() < marriage_rate

    def create_partner(self, person: Person, is_descendant: bool,
                      original_last_names: List[str]) -> Person:
        """
        Create a partner for the given person.

        Args:
            person: The person who needs a partner
            is_descendant: True if partner is descended from original ancestors
            original_last_names: List of original ancestor last names

        Returns:
            A new Person object as the partner
        """
        # Partner's birth year is within +/- 10 years
        partner_year_born = person.get_year_born() + random.randint(-10, 10)

        # Partner has opposite gender (for simplicity)
        partner_gender = "female" if person.get_gender() == "male" else "male"

        # Create the partner
        partner = self.create_person(partner_year_born, partner_gender,
                                     is_descendant, original_last_names, parents=None)

        # Link them as partners (bidirectional)
        person.set_partner(partner)
        partner.set_partner(person)

        return partner
