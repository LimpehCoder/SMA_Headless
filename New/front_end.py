# Helper to convert Yes/No to boolean
def get_boolean_input(prompt):
    while True:
        answer = input(prompt + " ").strip().lower()
        if answer in ['yes', 'y', 'true', 't']:
            return True
        elif answer in ['no', 'n', 'false', 'f']:
            return False
        else:
            print("Please enter Yes or No.")

# Helper to get an integer input
def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt + " "))
        except ValueError:
            print("Please enter a valid number.")