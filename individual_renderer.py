import pygame

from constants import COLOR_COOPERATOR, COLOR_PUNISHER, COLOR_DEFECTOR
from individual import Role


class IndividualRenderer:
    """Responsible for rendering an Individual on a pygame surface."""

    def render(self, individual, surface):
        # Determine color based on role
        if individual.role == Role.COOPERATOR:
            color = COLOR_COOPERATOR
        elif individual.role == Role.PUNISHER:
            color = COLOR_PUNISHER
        else:  # Role.DEFECTOR
            color = COLOR_DEFECTOR

        # Draw the frame
        pygame.draw.rect(
            surface, color,
            (individual.x, individual.y, individual.width, individual.height), 1
        )

        # Fill based on payoff (from bottom up)
        fill_height = int(individual.payoff * individual.height)
        if fill_height > 0:
            pygame.draw.rect(
                surface, color,
                (
                    individual.x,
                    individual.y + individual.height - fill_height,
                    individual.width, fill_height
                )
            )

        # Draw checkmark if cooperates
        if individual.cooperates:
            pygame.draw.line(
                surface, (255, 255, 255),
                (individual.x + 3, individual.y + individual.height - 7),
                (individual.x + 7, individual.y + individual.height - 3), 2
            )
            pygame.draw.line(
                surface, (255, 255, 255),
                (individual.x + 7, individual.y + individual.height - 3),
                (individual.x + individual.width - 3, individual.y + individual.height - 10), 2
            )
