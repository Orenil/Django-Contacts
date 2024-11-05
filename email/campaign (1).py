class EmailVariant:
    def __init__(self, subject, body, conditions=None):
        self.subject = subject
        self.body = body
        self.conditions = conditions or {}

    def render_email(self, variables):
        """Replace variables in the email body and subject."""
        rendered_subject = self.subject.format(**variables)
        rendered_body = self.body.format(**variables)
        return rendered_subject, rendered_body

    def __repr__(self):
        return f"EmailVariant(subject='{self.subject}')"


class EmailStep:
    def __init__(self, step_number):
        self.step_number = step_number
        self.variants = []

    def add_variant(self, subject, body, conditions=None):
        """Add a new variant to this step."""
        variant = EmailVariant(subject, body, conditions)
        self.variants.append(variant)

    def get_variant(self, index):
        """Retrieve a specific variant by index."""
        if index < len(self.variants):
            return self.variants[index]
        return None

    def __repr__(self):
        return f"EmailStep(step_number={self.step_number}, variants={len(self.variants)})"


class EmailSequence:
    def __init__(self, name):
        self.name = name
        self.steps = []

    def add_step(self):
        """Add a new step to the sequence."""
        step_number = len(self.steps) + 1
        step = EmailStep(step_number)
        self.steps.append(step)
        return step

    def get_step(self, step_number):
        """Retrieve a step by its number."""
        for step in self.steps:
            if step.step_number == step_number:
                return step
        return None

    def remove_step(self, step_number):
        """Remove a step from the sequence."""
        self.steps = [step for step in self.steps if step.step_number != step_number]

    def __repr__(self):
        return f"EmailSequence(name='{self.name}', steps={len(self.steps)})"

# Example usage
sequence = EmailSequence(name="Welcome Series")
step1 = sequence.add_step()
step1.add_variant("Welcome, {first_name}!", "Hi {first_name}, welcome to our platform.")
step1.add_variant("Hello {first_name}", "Hey {first_name}, thanks for joining!")

step2 = sequence.add_step()
step2.add_variant("Follow-up: {first_name}", "Just checking in, {first_name}. How can we help?")

# Display the sequence
print(sequence)
