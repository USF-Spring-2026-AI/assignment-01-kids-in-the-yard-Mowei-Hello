import random
from typing import List
from person import Person
from person_factory import PersonFactory


class FamilyTree:
    """
    Driver class for generating and managing the family tree.

    Attributes:
        factory: PersonFactory instance for creating people
        original_person1: First person born in 1950
        original_person2: Second person born in 1950
        all_people: List of all Person objects in the tree
        people_by_decade: Dictionary organizing people by birth decade
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
        self.people_by_decade = {}

        # Initialize the two original people born in 1950
        self._initialize_original_people()

    def _initialize_original_people(self):
        """Create the first two people born in 1950."""
        # Create first person (e.g., "Desmond Jones")
        self.original_person1 = self.factory.create_person(
            year_born=1950,
            gender="male",
            is_descendant=False,
            original_last_names=[],  # Will be set after creation
            parents=None
        )

        # Create second person (e.g., "Molly Smith")
        self.original_person2 = self.factory.create_person(
            year_born=1950,
            gender="female",
            is_descendant=False,
            original_last_names=[],  # Will be set after creation
            parents=None
        )

        # Link them as partners
        self.original_person1.set_partner(self.original_person2)
        self.original_person2.set_partner(self.original_person1)

        # Add to all_people list
        self.all_people.append(self.original_person1)
        self.all_people.append(self.original_person2)

        # Track by decade
        self._add_to_decade(self.original_person1)
        self._add_to_decade(self.original_person2)

    def _add_to_decade(self, person: Person):
        """
        Add a person to the people_by_decade tracking dictionary.

        Args:
            person: Person to add to decade tracking
        """
        year_born = person.get_year_born()
        decade = (year_born // 10) * 10

        if decade not in self.people_by_decade:
            self.people_by_decade[decade] = []

        self.people_by_decade[decade].append(person)

    def add_person(self, person: Person):
        """
        Add a person to the family tree.

        Args:
            person: Person to add to the tree
        """
        self.all_people.append(person)
        self._add_to_decade(person)

    def get_original_last_names(self) -> List[str]:
        """
        Get the last names of the two original people.

        Returns:
            List of the two original last names
        """
        return [
            self.original_person1.get_last_name(),
            self.original_person2.get_last_name()
        ]

    def calculate_num_children(self, year_born: int, has_partner: bool) -> int:
        """
        Calculate the number of children a person should have.

        Args:
            year_born: Year the person was born
            has_partner: True if the person has a partner

        Returns:
            Number of children (integer)
        """
        # Determine the decade
        decade_num = (year_born // 10) * 10
        decade = f"{decade_num}s"

        # Get birth rate for this decade
        if decade in self.factory.birth_marriage_rates:
            birth_rate = self.factory.birth_marriage_rates[decade]['birth_rate']
        else:
            # Default to 2.0 if decade not found
            birth_rate = 2.0

        # Apply +/- 1.5 variation
        min_children = birth_rate - 1.5
        max_children = birth_rate + 1.5

        # Round up to get integer bounds
        min_children = max(0, int(min_children + 0.5))
        max_children = int(max_children + 0.5)

        # Random number of children within range
        num_children = random.randint(min_children, max_children)

        # CS 562: Single parent has 1 fewer child
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

    def generate_tree(self):
        """
        Generate the complete family tree starting from the two original people.

        Uses a queue-based algorithm to process each person and generate their
        children until no more children can be born or until year 2120.
        """
        # Queue of people who can potentially have children
        # Each entry is a tuple: (person, is_primary_parent)
        queue = [(self.original_person1, True), (self.original_person2, True)]
        processed = set()  # Track which people have been processed

        original_last_names = self.get_original_last_names()

        while queue:
            person, is_primary_parent = queue.pop(0)

            # Skip if already processed
            person_id = id(person)
            if person_id in processed:
                continue

            processed.add(person_id)

            # Check if person has a partner
            partner = person.get_partner()
            has_partner = partner is not None

            # If person has a partner and we're the primary parent, handle children
            # (to avoid processing the same couple twice)
            if has_partner and not is_primary_parent:
                continue

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

            birth_years = self.distribute_birth_years(elder_year, num_children)

            # Create each child
            for birth_year in birth_years:
                # Stop if birth year exceeds 2120
                if birth_year > 2120:
                    break

                # Randomly assign gender to child
                child_gender = random.choice(["male", "female"])

                # Determine parents tuple
                if has_partner:
                    parents = (person, partner)
                else:
                    parents = (person, None)

                # Create the child
                child = self.factory.create_person(
                    year_born=birth_year,
                    gender=child_gender,
                    is_descendant=True,
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
                        is_descendant=False,
                        original_last_names=original_last_names
                    )
                    # Add partner to tree
                    self.add_person(child_partner)

                    # Add partner to queue (but not as primary parent)
                    queue.append((child_partner, False))

                # Add child to queue for processing
                queue.append((child, True))

    def get_total_count(self) -> int:
        """
        Get the total number of people in the tree.

        Returns:
            Total count of all people
        """
        return len(self.all_people)

    def get_count_by_decade(self):
        """
        Get the count of people born in each decade.

        Returns:
            Dictionary mapping decade to count {decade: count}
        """
        decade_counts = {}

        for decade, people in self.people_by_decade.items():
            decade_counts[decade] = len(people)

        return decade_counts

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
