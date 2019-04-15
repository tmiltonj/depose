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
            print('{0}) {1}\n'.format(i, opt))

        choice = self.get_integer('', 'Invalid choice', 1, len(options))
        return choice