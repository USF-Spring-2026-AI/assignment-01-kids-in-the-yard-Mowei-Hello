from typing import List, Tuple


class Person:
    """
    Represents a person in the family tree.

    Attributes:
        year_born: The year the person was born
        year_died: The year the person died
        first_name: The person's first name
        last_name: The person's last name
        gender: The person's gender ('male' or 'female')
        partner: The person's spouse/partner (another Person object or None)
        children: List of the person's children (Person objects)
        parents: Tuple of the person's parents (Person objects or None)
    """

    def __init__(self, year_born: int, year_died: int, first_name: str, last_name: str,
                 gender: str, parents: Tuple['Person', 'Person'] | None = None):
        """
        Initialize a Person object.

        Args:
            year_born: Year the person was born
            year_died: Year the person died
            first_name: Person's first name
            last_name: Person's last name
            gender: Person's gender ('male' or 'female')
            parents: Tuple of (parent1, parent2) or None for original ancestors
        """
        self._year_born = year_born
        self._year_died = year_died
        self._first_name = first_name
        self._last_name = last_name
        self._gender = gender
        self._partner = None
        self._children = []
        self._parents = parents

###### Getter methods #######

    def get_year_born(self) -> int:
        """Return the year the person was born."""
        return self._year_born

    def get_year_died(self) -> int:
        """Return the year the person died."""
        return self._year_died

    def get_first_name(self) -> str:
        """Return the person's first name."""
        return self._first_name

    def get_last_name(self) -> str:
        """Return the person's last name."""
        return self._last_name

    def get_gender(self) -> str:
        """Return the person's gender."""
        return self._gender

    def get_partner(self) -> 'Person' | None:
        """Return the person's partner/spouse."""
        return self._partner

    def get_children(self) -> List['Person']:
        """Return list of the person's children."""
        return self._children

    def get_parents(self) -> Tuple['Person', 'Person'] | None:
        """Return tuple of the person's parents."""
        return self._parents

    def get_full_name(self) -> str:
        """Return the person's full name (first name + last name)."""
        return f"{self._first_name} {self._last_name}"

###### Setter methods #######

    def set_first_name(self, first_name: str) -> None:
        """Set the person's first name."""
        self._first_name = first_name

    def set_last_name(self, last_name: str) -> None:
        """Set the person's last name."""
        self._last_name = last_name

    def set_partner(self, partner: 'Person') -> None:
        """Set the person's partner/spouse."""
        self._partner = partner

    def add_child(self, child: 'Person') -> None:
        """Add a child to the person's list of children."""
        self._children.append(child)

    # def is_descendant_of(self, ancestor1: 'Person', ancestor2: 'Person') -> bool:
    #     """
    #     Check if this person is a descendant of the two given ancestors.

    #     Args:
    #         ancestor1: First original ancestor
    #         ancestor2: Second original ancestor

    #     Returns:
    #         True if this person is descended from either ancestor, False otherwise
    #     """
    #     if self._parents is None:
    #         # This person has no parents, so they are not a descendant
    #         return False

    #     # Check if either parent is one of the original ancestors
    #     parent1, parent2 = self._parents
    #     if parent1 == ancestor1 or parent1 == ancestor2:
    #         return True
    #     if parent2 is not None and (parent2 == ancestor1 or parent2 == ancestor2):
    #         return True

    #     # Recursively check parents
    #     is_desc_parent1 = parent1.is_descendant_of(ancestor1, ancestor2)
    #     is_desc_parent2 = False
    #     if parent2 is not None:
    #         is_desc_parent2 = parent2.is_descendant_of(ancestor1, ancestor2)

    #     return is_desc_parent1 or is_desc_parent2
