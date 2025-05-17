import pygame
import numpy as np
from typing import List, Optional, Tuple, Union

from group import Group
from individual import Individual, Role

# Constants for rendering
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
INDIVIDUAL_SIZE = 20
MARGIN = 5

# Colors
COLOR_COOPERATOR = (0, 255, 0)  # Green
COLOR_PUNISHER = (0, 0, 0)  # Black
COLOR_DEFECTOR = (255, 0, 0)  # Red
COLOR_GROUP_FRAME = (100, 100, 100)  # Gray
COLOR_SELECTION = (0, 0, 255)  # Blue
COLOR_CONNECTION = (0, 0, 0)  # Black


def draw_dotted_line(surface, color, start_pos, end_pos, width=2, dash_length=5):
    """Draw a dotted line between two points"""
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)

    # Normalize direction
    dx, dy = dx / distance, dy / distance

    # Calculate number of segments
    segment_length = dash_length * 2  # dash + space
    segment_count = int(distance / segment_length) + 1

    # Draw dashes
    for i in range(segment_count):
        start = (start_pos[0] + dx * i * segment_length,
                 start_pos[1] + dy * i * segment_length)
        end = (min(start[0] + dx * dash_length, end_pos[0]),
               min(start[1] + dy * dash_length, end_pos[1]))
        pygame.draw.line(surface, color, start, end, width)


class Renderer:
    """Class for rendering the simulation"""

    def __init__(self):
        """Initialize the renderer"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multi-Level Selection Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

    def calculate_positions(self, group: Group, group_sizes: List[int],
                            x: int, y: int, max_width: int, max_height: int) -> None:
        """Calculate rendering positions for groups and individuals"""
        group.x, group.y = x, y

        if group.is_first_order():
            # Position individuals in a grid within the group
            n = len(group.members)  # type: ignore
            cols = max(1, min(int(np.sqrt(n)), 5))  # Max 5 columns
            rows = (n + cols - 1) // cols

            width = cols * (INDIVIDUAL_SIZE + MARGIN) + MARGIN
            height = rows * (INDIVIDUAL_SIZE + MARGIN) + MARGIN

            group.width, group.height = width, height

            # Position individuals
            for i, individual in enumerate(group.members):  # type: ignore
                row = i // cols
                col = i % cols
                individual.x = x + MARGIN + col * (INDIVIDUAL_SIZE + MARGIN)
                individual.y = y + MARGIN + row * (INDIVIDUAL_SIZE + MARGIN)
                individual.width = INDIVIDUAL_SIZE
                individual.height = INDIVIDUAL_SIZE
        else:
            # Position subgroups in a grid or row
            n = len(group.members)  # type: ignore

            if group.level == len(group_sizes):  # Top level
                # Arrange in a row
                available_width = max_width - 2 * MARGIN
                available_height = max_height - 2 * MARGIN

                group_width = available_width // n

                for i, subgroup in enumerate(group.members):  # type: ignore
                    sub_x = x + MARGIN + i * group_width
                    sub_y = y + MARGIN
                    self.calculate_positions(subgroup, group_sizes, sub_x, sub_y,
                                             group_width - MARGIN,
                                             available_height - MARGIN)

                # Update group dimensions based on subgroups
                min_x = min(subgroup.x for subgroup in group.members)  # type: ignore
                min_y = min(subgroup.y for subgroup in group.members)  # type: ignore
                max_x = max(subgroup.x + subgroup.width for subgroup in group.members)  # type: ignore
                max_y = max(subgroup.y + subgroup.height for subgroup in group.members)  # type: ignore

                group.width = max_x - min_x + 2 * MARGIN
                group.height = max_y - min_y + 2 * MARGIN

            else:  # Middle levels
                # Arrange in a grid
                cols = max(1, min(int(np.sqrt(n)), 3))  # Max 3 columns for clarity
                rows = (n + cols - 1) // cols

                available_width = max_width - 2 * MARGIN
                available_height = max_height - 2 * MARGIN

                cell_width = available_width // cols
                cell_height = available_height // rows

                for i, subgroup in enumerate(group.members):  # type: ignore
                    row = i // cols
                    col = i % cols
                    sub_x = x + MARGIN + col * cell_width
                    sub_y = y + MARGIN + row * cell_height
                    self.calculate_positions(subgroup, group_sizes, sub_x, sub_y,
                                             cell_width - MARGIN,
                                             cell_height - MARGIN)

                # Update group dimensions based on subgroups
                min_x = min(subgroup.x for subgroup in group.members)  # type: ignore
                min_y = min(subgroup.y for subgroup in group.members)  # type: ignore
                max_x = max(subgroup.x + subgroup.width for subgroup in group.members)  # type: ignore
                max_y = max(subgroup.y + subgroup.height for subgroup in group.members)  # type: ignore

                group.width = max_x - min_x + 2 * MARGIN
                group.height = max_y - min_y + 2 * MARGIN

    def render_individual(self, surface, individual: Individual):
        """Render an individual"""
        # Determine color based on role
        if individual.role == Role.COOPERATOR:
            color = COLOR_COOPERATOR
        elif individual.role == Role.PUNISHER:
            color = COLOR_PUNISHER
        else:  # Role.DEFECTOR
            color = COLOR_DEFECTOR

        # Draw the frame
        pygame.draw.rect(surface, color,
                         (individual.x, individual.y, individual.width, individual.height), 1)
        # Draw the fillout
        pygame.draw.rect(surface, (color[0] - 50, color[0] - 50, color[0] - 50),
                         (individual.x, individual.y, individual.width, individual.height))


        # Fill based on payoff (from bottom up)
        fill_height = int(individual.payoff * individual.height)
        if fill_height > 0:
            pygame.draw.rect(surface, color,
                             (individual.x, individual.y + individual.height - fill_height,
                              individual.width, fill_height))

        # Draw checkmark if cooperates
        if individual.cooperates:
            # Simple checkmark
            pygame.draw.line(surface, (255, 255, 255),
                             (individual.x + 3, individual.y + individual.height - 7),
                             (individual.x + 7, individual.y + individual.height - 3), 2)
            pygame.draw.line(surface, (255, 255, 255),
                             (individual.x + 7, individual.y + individual.height - 3),
                             (individual.x + individual.width - 3, individual.y + individual.height - 10), 2)

    def render_group(self, surface, group: Group, is_selected: bool = False):
        """Render a group and its members"""
        # Render frame
        frame_color = COLOR_SELECTION if is_selected else COLOR_GROUP_FRAME
        pygame.draw.rect(surface, frame_color, (group.x, group.y, group.width, group.height), 2)

        # Render members
        if group.is_first_order():
            for individual in group.members:  # type: ignore
                self.render_individual(surface, individual)
        else:
            for subgroup in group.members:  # type: ignore
                self.render_group(surface, subgroup)

    def render_connections(self, surface, connections: List[Tuple[Union[Individual, Group], Union[Individual, Group]]]):
        """Render connections between entities"""
        for source, target in connections:
            if hasattr(source, 'x') and hasattr(target, 'x'):
                # Draw connection between two points
                if isinstance(source, Individual) and isinstance(target, Individual):
                    # Connection between individuals
                    start_pos = (source.x + source.width // 2, source.y + source.height // 2)
                    end_pos = (target.x + target.width // 2, target.y + target.height // 2)
                else:
                    # Connection between groups
                    start_pos = (source.x + source.width // 2, source.y + source.height // 2)
                    end_pos = (target.x + target.width // 2, target.y + target.height // 2)

                # Draw dotted line
                draw_dotted_line(surface, COLOR_CONNECTION, start_pos, end_pos)

    def draw_ui(self, surface, current_stage: int, speed: float):
        """Draw UI elements"""
        # Draw stage label
        stage_names = ["1: Cooperation", "2: Punishment", "3: Learning",
                       "4: Competition", "5: Mutation"]
        stage_text = self.font.render(f"Stage: {stage_names[current_stage]}",
                                      True, (0, 0, 0))
        surface.blit(stage_text, (20, 20))

        # Draw speed label
        speed_text = self.font.render(f"Speed: {speed:.1f}x", True, (0, 0, 0))
        surface.blit(speed_text, (20, 50))

        # Draw legend
        legend_x = SCREEN_WIDTH - 180
        legend_y = 20
        legend_items = [
            ("Cooperator (C)", COLOR_COOPERATOR),
            ("Punisher (P)", COLOR_PUNISHER),
            ("Defector (D)", COLOR_DEFECTOR)
        ]

        for i, (label, color) in enumerate(legend_items):
            # Draw color box
            pygame.draw.rect(surface, color, (legend_x, legend_y + i * 25, 15, 15))
            pygame.draw.rect(surface, (0, 0, 0), (legend_x, legend_y + i * 25, 15, 15), 1)

            # Draw text
            text = self.font.render(label, True, (0, 0, 0))
            surface.blit(text, (legend_x + 25, legend_y + i * 25))

        # Draw instructions
        instructions = [
            "Space: Advance simulation",
            "Up/Down: Change speed",
            "Click: Select group",
            "Esc: Quit"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (0, 0, 0))
            surface.blit(text, (legend_x, legend_y + (i + 4) * 25))

    def render_simulation(self, root_group: Group, selected_group: Optional[Group],
                          connections: List[Tuple[Union[Individual, Group], Union[Individual, Group]]],
                          current_stage: int, speed: float):
        """Render the full simulation"""
        self.screen.fill((240, 240, 240))  # Light gray background

        # Draw UI
        self.draw_ui(self.screen, current_stage, speed)

        # Draw the hierarchy
        self.render_group(self.screen, root_group)

        # Highlight selected group
        if selected_group:
            self.render_group(self.screen, selected_group, True)

        # Draw connections
        self.render_connections(self.screen, connections)

        pygame.display.flip()

    def get_clock(self):
        """Get the pygame clock"""
        return self.clock

    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()