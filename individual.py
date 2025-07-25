import enum
import logging
import random

from constants import INDIVIDUAL_SIZE, MUTATION_CHANCE

class Role(enum.Enum):
    """Enum for individual roles"""
    COOPERATOR = "C"
    PUNISHER = "P"
    DEFECTOR = "D"


class Individual:
    """Class representing an individual in the simulation"""

    def __init__(self, role: Role = None, have_punisher = True):
        """Initialize an individual with given role or random role"""
        self.role = role if role else random.choice(list(Role))
        self.payoff = 1.0  # Start with baseline payoff
        self.cooperates = None  # Will be set during the cooperation stage
        self.have_punisher = have_punisher

        # Position for rendering
        self.x = 0
        self.y = 0
        self.width = INDIVIDUAL_SIZE
        self.height = INDIVIDUAL_SIZE
        self.members = None

    def reset_payoff(self):
        """Reset payoff to baseline"""
        self.payoff = 1.0

    def clone(self):
        """Create a copy of this individual"""
        clone = Individual(self.role, self.have_punisher)
        clone.payoff = self.payoff
        clone.cooperates = self.cooperates
        return clone

    def mutate(self):
        """Potentially change role based on mutation chance"""
        if random.random() < MUTATION_CHANCE:
            # Choose a new role different from current one
            new_roles = [r for r in Role if r != self.role]
            if not self.have_punisher:
                new_roles = [r for r in new_roles if r != Role.PUNISHER]
            old_role = self.role
            self.role = random.choice(new_roles)
            logging.info("mutated from %s to %s", old_role, self.role )

    def __repr__(self):
        return (f"Individual(role={self.role.name}, payoff={self.payoff:.2f}, "
                f"cooperates={self.cooperates}, pos=({self.x}, {self.y}))")
