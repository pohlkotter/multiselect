import enum
import logging
import random

import pygame

from constants import INDIVIDUAL_SIZE, MUTATION_CHANCE, COLOR_COOPERATOR, COLOR_PUNISHER, COLOR_DEFECTOR


class Role(enum.Enum):
    """Enum for individual roles"""
    COOPERATOR = "C"
    PUNISHER = "P"
    DEFECTOR = "D"


class Individual:
    """Class representing an individual in the simulation"""

    def __init__(self, role: Role = None):
        """Initialize an individual with given role or random role"""
        self.role = role if role else random.choice(list(Role))
        self.payoff = 1.0  # Start with baseline payoff
        self.cooperates = None  # Will be set during the cooperation stage

        # Position for rendering
        self.x = 0
        self.y = 0
        self.width = INDIVIDUAL_SIZE
        self.height = INDIVIDUAL_SIZE

    def reset_payoff(self):
        """Reset payoff to baseline"""
        self.payoff = 1.0

    def clone(self):
        """Create a copy of this individual"""
        clone = Individual(self.role)
        clone.payoff = self.payoff
        clone.cooperates = self.cooperates
        return clone

    def mutate(self):
        """Potentially change role based on mutation chance"""
        if random.random() < MUTATION_CHANCE:
            # Choose a new role different from current one
            new_roles = [r for r in Role if r != self.role]
            old_role = self.role
            self.role = random.choice(new_roles)
            logging.info("mutated from %s to %s", old_role, self.role )
    def __repr__(self):
        return (f"Individual(role={self.role.name}, payoff={self.payoff:.2f}, "
                f"cooperates={self.cooperates}, pos=({self.x}, {self.y}))")
