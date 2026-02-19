from collections import deque
import math
import random
from typing import Dict, List
from person import Person
from person_factory import PersonFactory
from utils import get_decade_string


class FamilyTree:
    """
    Driver class for generating and managing the family tree.

    Attributes:
        factory: PersonFactory instance for creating people
        original_person1: First person born in 1950
        original_person2: Second person born in 1950
        all_people: List of all Person objects in the tree
        people_by_birth_decade: Dictionary organizing people by birth decade
        people_alive_by_decade: Dictionary organizing people alive in each decade
    """

    def __init__(self, factory: PersonFactory):
        """
        Initialize the FamilyTree with a PersonFactory.

        Args:
            factory: PersonFactory instance with loaded data files
        """
        self.factory = factory
        self.original_person1 = None
        self.original_person2 = None
        self.all_people = []
        self.people_by_birth_decade: Dict[str, List[Person]] = {}
        self.people_alive_by_decade: Dict[str, List[Person]] = {}

        # Initialize the two original people born in 1950
        self._initialize_original_people()

    def _initialize_original_people(self):
        """Create the first two people born in 1950."""
        # Create first person ("Desmond Jones")
        self.original_person1 = self.factory.create_person(
            year_born=1950,
            gender="male",
            is_descendant=False,
            original_last_names=['Jones', 'Smith'],
            parents=None
        )

        # Create second person ("Molly Smith")
        self.original_person2 = self.factory.create_person(
            year_born=1950,
            gender="female",
            is_descendant=False,
            original_last_names=['Jones', 'Smith'],
            parents=None
        )

        # Set names explicitly to ensure they are "Desmond Jones" and "Molly Smith"
        self.original_person1.set_first_name("Desmond")
        self.original_person1.set_last_name("Jones")
        self.original_person2.set_first_name("Molly")
        self.original_person2.set_last_name("Smith")

        # Link them as partners
        self.original_person1.set_partner(self.original_person2)
        self.original_person2.set_partner(self.original_person1)

        # Add the original people to the tree
        self.add_person(self.original_person1)
        self.add_person(self.original_person2)


    def _add_to_decade(self, person: Person):
        """
        Add a person to the people_by_decade tracking dictionary.

        Args:
            person: Person to add to decade tracking
        """
        decade = get_decade_string(person.get_year_born())

        if decade not in self.people_by_birth_decade:
            self.people_by_birth_decade[decade] = []

        self.people_by_birth_decade[decade].append(person)

    def add_person(self, person: Person):
        """
        Add a person to the family tree.

        Args:
            person: Person to add to the tree
        """
        self.all_people.append(person)
        self._add_to_decade(person)

    def calculate_num_children(self, year_born: int, has_partner: bool) -> int:
        """
        Calculate the number of children a person should have.

        Args:
            year_born: Year the person was born
            has_partner: True if the person has a partner

        Returns:
            Number of children (integer)
        """
        decade = get_decade_string(year_born)

        birth_rate = self.factory.birth_marriage_rates[decade]['birth_rate']

        # Apply +/- 1.5 variation
        min_children = birth_rate - 1.5
        max_children = birth_rate + 1.5

        # Round up to get integer bounds and ensure min is not negative
        min_children = max(0, math.ceil(min_children))
        max_children = math.ceil(max_children)

        # Random number of children within range
        num_children = random.randint(min_children, max_children)

        # Extra requirement for grad student: single parent has 1 fewer child
        if not has_partner:
            num_children = max(0, num_children - 1)

        return num_children

    def distribute_birth_years(self, parent_year_born: int, num_children: int) -> List[int]:
        """
        Distribute children's birth years evenly across parent's fertile period.

        Args:
            parent_year_born: Year the parent was born
            num_children: Number of children to distribute

        Returns:
            List of birth years for children
        """
        if num_children == 0:
            return []

        # Children born between parent's year + 25 and parent's year + 45
        start_year = parent_year_born + 25
        end_year = parent_year_born + 45

        # Distribute evenly
        if num_children == 1:
            # Single child: randomly in the range
            birth_years = [random.randint(start_year, end_year)]
        else:
            # Multiple children: distribute evenly
            step = (end_year - start_year) / (num_children - 1)
            birth_years = [int(start_year + i * step) for i in range(num_children)]

        return birth_years
    
    def build_people_alive_by_decade(self):
        """
        Build the people_alive_by_decade dictionary to track which people are alive in each decade.
        This is called after the tree is fully generated.
        Format: {decade_string: [Person objects]}
        """
        for person in self.all_people:
            birth_decade = get_decade_string(person.get_year_born())
            death_decade = get_decade_string(person.get_year_died())

            # Get all decades from birth to death (inclusive)
            birth_decade_num = int(birth_decade[:-1])  # Remove 's' and convert to int
            death_decade_num = int(death_decade[:-1])

            for decade_num in range(birth_decade_num, death_decade_num + 10, 10): # Iterate through each decade from birth to death
                decade_str = f"{decade_num}s"
                if decade_str not in self.people_alive_by_decade:
                    self.people_alive_by_decade[decade_str] = []
                self.people_alive_by_decade[decade_str].append(person)

    def generate_tree(self):
        """
        Generate the complete family tree starting from the two original people.

        Uses a queue-based algorithm to process each person and generate their
        children (and potential spouses of the children) until no more children can be born or until year 2120.
        """
        # Queue of people who can potentially have children
        queue = deque([self.original_person1]) # Only need to process one of the original people since they are partners
        processed = set()  # Track which people have been processed

        original_last_names = [
            self.original_person1.get_last_name(),
            self.original_person2.get_last_name()
        ]

        while queue:
            person = queue.popleft() # FIFO queue for preserving generational order

            # Skip if already processed, reference: https://stackoverflow.com/questions/1252357/is-there-an-object-unique-identifier-in-python
            person_id = id(person)
            if person_id in processed:
                continue

            processed.add(person_id)

            # Check if person has a partner
            partner = person.get_partner()
            has_partner = partner is not None

            # Determine number of children
            num_children = self.calculate_num_children(person.get_year_born(), has_partner)

            if num_children == 0:
                continue

            # Determine birth years for children
            # Use the elder parent's birth year for calculation
            if has_partner:
                elder_year = min(person.get_year_born(), partner.get_year_born())
            else:
                elder_year = person.get_year_born()

            children_birth_years = self.distribute_birth_years(elder_year, num_children)

            # Create each child
            for birth_year in children_birth_years:
                # Skip if birth year exceeds 2120
                if birth_year > 2120:
                    continue

                # Assign a gender based on the gender probability csv
                child_gender = self.factory.assign_gender(birth_year)

                # Determine parents tuple
                if has_partner:
                    parents = (person, partner)
                else:
                    parents = (person, None)

                # Create the child
                child = self.factory.create_person(
                    year_born=birth_year,
                    gender=child_gender,
                    is_descendant=True, # A child is a direct descendant because they are naturally born into the tree
                    original_last_names=original_last_names,
                    parents=parents
                )

                # Add child to parent(s)
                person.add_child(child)
                if has_partner:
                    partner.add_child(child)

                # Add child to tree
                self.add_person(child)

                # Determine if child should have a partner
                if self.factory.should_have_partner(birth_year):
                    # Create partner for child
                    child_partner = self.factory.create_partner(
                        child,
                        is_descendant=False, # A partner is not a direct descendant because they are married into the tree
                        original_last_names=[] # Partners do not inherit original last names
                    )
                    # Add partner to tree
                    if child_partner is not None:
                        self.add_person(child_partner)

                # Add child to queue for further processing
                queue.append(child)

        # After generating the tree, build the people_alive_by_decade dictionary for later queries
        self.build_people_alive_by_decade()

    def get_total_count(self) -> int:
        """
        Get the total number of people in the tree.

        Returns:
            Total count of all people
        """
        return len(self.all_people)

    def get_birth_count_by_decade(self):
        """
        Get the count of people born in each decade.

        Returns:
            Dictionary mapping decade to count {decade: count}
        """
        decade_counts = {}

        for decade, people in self.people_by_birth_decade.items():
            decade_counts[decade] = len(people)

        return decade_counts
    
    def get_alive_count_by_decade(self):
        """
        Get the count of people alive in each decade.

        Returns:
            Dictionary mapping decade to count {decade: count}
        """
        alive_counts = {}

        for decade, people in self.people_alive_by_decade.items():
            alive_counts[decade] = len(people)

        return alive_counts

    def find_duplicate_names(self) -> List[str]:
        """
        Find all duplicate full names in the tree.

        Returns:
            List of duplicate full names (each unique name appears once)
        """
        name_counts = {}

        # Count occurrences of each full name
        for person in self.all_people:
            full_name = person.get_full_name()
            if full_name in name_counts:
                name_counts[full_name] += 1
            else:
                name_counts[full_name] = 1

        # Find names that appear more than once
        duplicates = []
        for name, count in name_counts.items():
            if count > 1:
                duplicates.append(name)

        # Sort alphabetically for consistent output
        duplicates.sort()

        return duplicates
