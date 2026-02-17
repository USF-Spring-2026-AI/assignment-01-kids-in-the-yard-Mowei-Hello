from person_factory import PersonFactory
from family_tree import FamilyTree


def display_menu():
    """Display the interactive menu options."""
    print("Are you interested in:")
    print("(T)otal number of people in the tree")
    print("Total number of people in the tree by (D)ecade")
    print("(N)ames duplicated")


def show_total(tree: FamilyTree):
    """
    Display the total number of people in the tree.

    Args:
        tree: FamilyTree instance to query
    """
    total = tree.get_total_count()
    print(f"The tree contains {total} people total")


def show_by_decade(tree: FamilyTree):
    """
    Display the number of people born in each decade.

    Args:
        tree: FamilyTree instance to query
    """
    decade_counts = tree.get_count_by_decade()

    # Sort decades chronologically
    sorted_decades = sorted(decade_counts.keys())

    for decade in sorted_decades:
        count = decade_counts[decade]
        print(f"{decade}: {count}")


def show_duplicates(tree: FamilyTree):
    """
    Display all duplicate names in the tree.

    Args:
        tree: FamilyTree instance to query
    """
    duplicates = tree.find_duplicate_names()

    if len(duplicates) == 0:
        print("There are no duplicate names in the tree.")
    else:
        print(f"There are {len(duplicates)} duplicate names in the tree:")
        for name in duplicates:
            print(f"* {name}")


def get_user_input() -> str:
    """
    Get and validate user input.

    Returns:
        Uppercase single character representing user choice
    """
    while True:
        user_input = input("> ").strip().upper()

        if user_input in ['T', 'D', 'N', 'Q']:
            return user_input
        else:
            print("Invalid input. Please enter T, D, N, or Q.")


def main():
    """Main program execution."""
    print("Reading files...")
    factory = PersonFactory()
    factory.read_files()

    print("Generating family tree...")
    tree = FamilyTree(factory)
    tree.generate_tree()

    # Interactive query loop
    while True:
        display_menu()
        choice = get_user_input()

        if choice == 'T':
            show_total(tree)
        elif choice == 'D':
            show_by_decade(tree)
        elif choice == 'N':
            show_duplicates(tree)
        elif choice == 'Q':
            print("Exiting...")
            break

        print()  # Blank line for readability


if __name__ == "__main__":
    main()
