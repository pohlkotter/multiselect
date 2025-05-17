import enum
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
            self.role = random.choice(new_roles)

    def render(self, surface):
        """Render the individual as a square with appropriate color"""
        # Draw the frame
        pygame.draw.rect(surface, (50, 50, 50), (self.x, self.y, self.width, self.height), 1)

        # Determine color based on role
        if self.role == Role.COOPERATOR:
            color = COLOR_COOPERATOR
        elif self.role == Role.PUNISHER:
            color = COLOR_PUNISHER
        else:  # Role.DEFECTOR
            color = COLOR_DEFECTOR

        # Fill based on payoff (from bottom up)
        fill_height = int(self.payoff * self.height)
        if fill_height > 0:
            pygame.draw.rect(surface, color,
                             (self.x, self.y + self.height - fill_height,
                              self.width, fill_height))

        # Draw checkmark if cooperates
        if self.cooperates:
            # Simple checkmark
            pygame.draw.line(surface, (255, 255, 255),
                             (self.x + 3, self.y + self.height - 7),
                             (self.x + 7, self.y + self.height - 3), 2)
            pygame.draw.line(surface, (255, 255, 255),
                             (self.x + 7, self.y + self.height - 3),
                             (self.x + self.width - 3, self.y + self.height - 10), 2)

