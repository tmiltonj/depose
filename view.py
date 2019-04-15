class UI():
    def message(self, message):
        print(message)

    def error(self, message):
        print("ERROR: " + message)

    def get_integer(self, prompt, error, min, max):
        value = min - 1
        while (value < min or value > max):
            self.message(prompt)
            try:
                value = int(input())
            except ValueError as e:
                self.error("not an integer")

            if (value < min or value > max):
                self.error(error)
        
        return value

    def get_choice(self, prompt, options):
        self.message(prompt)
        for i, opt in enumerate(options, 1):
            print('{0}) {1}'.format(i, opt))

        choice = self.get_integer('Enter selection: ', 'Invalid choice', 1, len(options))
        return options[choice - 1]

    
if __name__ == '__main__':
    ui = UI()

    options = [
        "Choice One",
        "Choice Two",
        "Choice Three"
    ]

    choice = ui.get_choice("Pick an option", options)

    ui.message("Chose: " + choice)
