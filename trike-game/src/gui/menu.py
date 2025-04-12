class Menu:
    def __init__(self):
        self.options = ["Start Game", "Settings", "Exit"]

    def display(self):
        print("Game Menu:")
        for index, option in enumerate(self.options):
            print(f"{index + 1}. {option}")

    def select_option(self, choice):
        if choice < 1 or choice > len(self.options):
            print("Invalid choice. Please select a valid option.")
            return None
        return self.options[choice - 1]