import pygame
import numpy as np
from typing import List, Optional, Tuple

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, INDIVIDUAL_SIZE, MARGIN, COLOR_COOPERATOR, COLOR_PUNISHER, \
    COLOR_DEFECTOR, COLOR_CONNECTION
from group import Group
from individual import Role, Individual, HAVE_PUNISHER


class Renderer:
    """Class handling all UI-related aspects of the multi-level selection simulation"""

    def __init__(self, screen_width: int = SCREEN_WIDTH, screen_height: int = SCREEN_HEIGHT, havePunisher = True):
        """Initialize the renderer"""
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Multi-Level Selection Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Store dimensions
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.havePunisher = havePunisher
        self.single_step_mode = False

    def calculate_positions(self, root_group: Group, group_sizes: List[int]) -> None:
        """Calculate rendering positions for groups and individuals"""
        self._calculate_positions(root_group, 50, 100, self.screen_width - 100, self.screen_height - 150, group_sizes)

    def _calculate_positions(self, group: Group, x: int, y: int, max_width: int, max_height: int,
                             group_sizes: List[int]) -> None:
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
                    self._calculate_positions(subgroup, sub_x, sub_y,
                                              group_width - MARGIN,
                                              available_height - MARGIN,
                                              group_sizes)

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
                    self._calculate_positions(subgroup, sub_x, sub_y,
                                              cell_width - MARGIN,
                                              cell_height - MARGIN,
                                              group_sizes)

                # Update group dimensions based on subgroups
                min_x = min(subgroup.x for subgroup in group.members)  # type: ignore
                min_y = min(subgroup.y for subgroup in group.members)  # type: ignore
                max_x = max(subgroup.x + subgroup.width for subgroup in group.members)  # type: ignore
                max_y = max(subgroup.y + subgroup.height for subgroup in group.members)  # type: ignore

                group.width = max_x - min_x + 2 * MARGIN
                group.height = max_y - min_y + 2 * MARGIN

    def find_group_at_position(self, root_group: Group, x: int, y: int) -> Optional[Group]:
        """Find the group at the given position"""
        # Check if point is inside this group
        if not (root_group.x <= x <= root_group.x + root_group.width and
                root_group.y <= y <= root_group.y + root_group.height):
            return None

        # Check subgroups (depth-first)
        if not root_group.is_first_order():
            for subgroup in root_group.members:  # type: ignore
                found = self.find_group_at_position(subgroup, x, y)
                if found:
                    return found

        # If we're here, point is in this group but not in any subgroup
        return root_group

    def render(self, root_group: Group, selected_group: Optional[Group],
               current_stage: int, speed: float, connections: List[Tuple] = None,
               connection_timer: int = 0) -> None:
        """Render the complete simulation state"""
        self.screen.fill((240, 240, 240))  # Light gray background

        # Draw UI elements
        self._draw_ui(current_stage, speed)

        # Draw the hierarchy
        root_group.render(self.screen)

        # Highlight selected group
        if selected_group:
            selected_group.render(self.screen, True)

        # Draw connections if timer is active
        if connection_timer > 0 and connections:
            self._draw_connections(connections)

        pygame.display.flip()

    def _draw_ui(self, current_stage: int, speed: float) -> None:
        """Draw UI elements"""
        # Draw stage label
        stage_names = ["1: Cooperation", "2: Punishment", "3: Learning",
                       "4: Competition", "5: Mutation"]
        stage_text = self.font.render(f"Stage: {stage_names[current_stage]}",
                                      True, (0, 0, 0))
        self.screen.blit(stage_text, (20, 20))

        # Draw speed label
        speed_str = f"Speed: {speed:.1f}x" if not self.single_step_mode else f"Single Step Mode"
        speed_text = self.font.render(speed_str, True, (0, 0, 0))
        self.screen.blit(speed_text, (20, 50))

        # Draw legend
        legend_x = self.screen_width - 180
        legend_y = 20
        legend_items = [
            ("Cooperator (C)", COLOR_COOPERATOR),
            ("Punisher (P)", COLOR_PUNISHER),
            ("Defector (D)", COLOR_DEFECTOR)
        ] if HAVE_PUNISHER else  [
            ("Cooperator (C)", COLOR_COOPERATOR),
            ("Defector (D)", COLOR_DEFECTOR)
        ]

        for i, (label, color) in enumerate(legend_items):
            # Draw color box
            pygame.draw.rect(self.screen, color, (legend_x, legend_y + i * 25, 15, 15))
            pygame.draw.rect(self.screen, (0, 0, 0), (legend_x, legend_y + i * 25, 15, 15), 1)

            # Draw text
            text = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text, (legend_x + 25, legend_y + i * 25))

        # Draw instructions
        instructions = [
            "Space: Advance simulation",
            "Up/Down: Change speed ",
            "s: Single Step modus: ",
            "Right: Advance Single Step",
            "Click: Select group",
            "Esc: Quit"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (0, 0, 0))
            self.screen.blit(text, (legend_x, legend_y + (i + 4) * 25))

    def _draw_connections(self, connections: List[Tuple]) -> None:
        """Draw connections between interacting entities"""
        for source, target in connections:
            # Draw dotted line between individuals
            if hasattr(source, 'x') and hasattr(target, 'x'):  # Individuals
                start_pos = (source.x + INDIVIDUAL_SIZE // 2, source.y + INDIVIDUAL_SIZE // 2)
                end_pos = (target.x + INDIVIDUAL_SIZE // 2, target.y + INDIVIDUAL_SIZE // 2)
            else:  # Groups
                # Draw dotted line between groups
                start_pos = (source.x + source.width // 2, source.y + source.height // 2)
                end_pos = (target.x + target.width // 2, target.y + target.height // 2)

            # Draw dotted line
            self.draw_dotted_line(self.screen, COLOR_CONNECTION, start_pos, end_pos)

    def draw_dotted_line(self, surface, color, start_pos, end_pos, width=2, dash_length=5):
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

    def get_clock(self):
        """Get the pygame clock object"""
        return self.clock