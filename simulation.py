import random
import pygame
import numpy as np
from typing import List, Optional

from constants import SCREEN_WIDTH, SCREEN_HEIGHT, INDIVIDUAL_SIZE, MARGIN, COLOR_COOPERATOR, COLOR_PUNISHER, \
    COLOR_DEFECTOR, COLOR_CONNECTION
from group import Group
from individual import Role, Individual
from renderer import draw_dotted_line


class Simulation:
    """Class managing the multi-level selection simulation"""

    def __init__(self,
                 group_sizes: List[int],
                 initial_cooperator_ratio: float = 0.33,
                 initial_punisher_ratio: float = 0.33):
        """
        Initialize the simulation with hierarchical groups

        Args:
            group_sizes: List of group sizes at each level (e.g., [5, 4, 3] means
                        3 third-order groups, each with 4 second-order groups,
                        each with 5 individuals)
            initial_cooperator_ratio: Initial ratio of cooperators
            initial_punisher_ratio: Initial ratio of punishers
                        (defector ratio is 1 - cooperator_ratio - punisher_ratio)
        """
        self.group_sizes = group_sizes
        self.initial_cooperator_ratio = initial_cooperator_ratio
        self.initial_punisher_ratio = initial_punisher_ratio

        # Animation speed (frames per second)
        self.speed = 1.0

        # Current state
        self.selected_group = None
        self.current_stage = 0
        self.stage_connections = []
        self.connection_timer = 0

        # Initialize the simulation
        self.root_group = self._create_hierarchy(group_sizes)

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Multi-Level Selection Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Calculate positions for rendering
        self._calculate_positions(self.root_group, 50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150)

    def _create_hierarchy(self, sizes: List[int], level: int = None) -> Group:
        """Create a hierarchical structure of groups based on the given sizes"""
        if level is None:
            level = len(sizes)

        if level == 1:
            # Create a first-order group with individuals
            individuals = []
            for _ in range(sizes[0]):
                # Determine role based on initial ratios
                rand = random.random()
                if rand < self.initial_cooperator_ratio:
                    role = Role.COOPERATOR
                elif rand < self.initial_cooperator_ratio + self.initial_punisher_ratio:
                    role = Role.PUNISHER
                else:
                    role = Role.DEFECTOR

                individuals.append(Individual(role))
            return Group(individuals, 1)
        else:
            # Create a higher-order group with subgroups
            subgroups = []
            for _ in range(sizes[level - 1]):
                subgroups.append(self._create_hierarchy(sizes, level - 1))
            return Group(subgroups, level)

    def _calculate_positions(self, group: Group, x: int, y: int, max_width: int, max_height: int) -> None:
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

            if group.level == len(self.group_sizes):  # Top level
                # Arrange in a row
                available_width = max_width - 2 * MARGIN
                available_height = max_height - 2 * MARGIN

                group_width = available_width // n

                for i, subgroup in enumerate(group.members):  # type: ignore
                    sub_x = x + MARGIN + i * group_width
                    sub_y = y + MARGIN
                    self._calculate_positions(subgroup, sub_x, sub_y,
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
                    self._calculate_positions(subgroup, sub_x, sub_y,
                                              cell_width - MARGIN,
                                              cell_height - MARGIN)

                # Update group dimensions based on subgroups
                min_x = min(subgroup.x for subgroup in group.members)  # type: ignore
                min_y = min(subgroup.y for subgroup in group.members)  # type: ignore
                max_x = max(subgroup.x + subgroup.width for subgroup in group.members)  # type: ignore
                max_y = max(subgroup.y + subgroup.height for subgroup in group.members)  # type: ignore

                group.width = max_x - min_x + 2 * MARGIN
                group.height = max_y - min_y + 2 * MARGIN

    def run_step(self) -> None:
        """Run a single step of the simulation"""
        # Clear previous connections
        self.stage_connections = []

        # Advance to next stage
        self.current_stage = (self.current_stage + 1) % 5

        if self.current_stage == 0:  # Stage 1: Cooperation
            self.root_group.stage1_cooperation()
        elif self.current_stage == 1:  # Stage 2: Punishment
            self.stage_connections = self.root_group.stage2_punishment()
        elif self.current_stage == 2:  # Stage 3: Learning
            self.stage_connections = self.root_group.stage3_learning()
        elif self.current_stage == 3:  # Stage 4: Competition
            self.stage_connections = self.root_group.stage4_competition()
        elif self.current_stage == 4:  # Stage 5: Mutation
            self.root_group.stage5_mutation()

        # Set connection timer
        self.connection_timer = 30  # Show connections for 30 frames

    def handle_events(self) -> bool:
        """Handle pygame events, return False if should quit"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.run_step()
                elif event.key == pygame.K_UP:
                    self.speed = min(self.speed * 1.5, 10.0)
                elif event.key == pygame.K_DOWN:
                    self.speed = max(self.speed / 1.5, 0.1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Select group on click
                self.selected_group = self._find_group_at_position(
                    self.root_group, event.pos[0], event.pos[1])

        return True

    def _find_group_at_position(self, group: Group, x: int, y: int) -> Optional[Group]:
        """Find the group at the given position"""
        # Check if point is inside this group
        if not (group.x <= x <= group.x + group.width and
                group.y <= y <= group.y + group.height):
            return None

        # Check subgroups (depth-first)
        if not group.is_first_order():
            for subgroup in group.members:  # type: ignore
                found = self._find_group_at_position(subgroup, x, y)
                if found:
                    return found

        # If we're here, point is in this group but not in any subgroup
        return group

    def render(self) -> None:
        """Render the simulation state"""
        self.screen.fill((240, 240, 240))  # Light gray background

        # Draw UI elements
        self._draw_ui()

        # Draw the hierarchy
        self.root_group.render(self.screen)

        # Highlight selected group
        if self.selected_group:
            self.selected_group.render(self.screen, True)

        # Draw connections if timer is active
        if self.connection_timer > 0:
            self._draw_connections()
            self.connection_timer -= 1

        pygame.display.flip()

    def _draw_ui(self) -> None:
        """Draw UI elements"""
        # Draw stage label
        stage_names = ["1: Cooperation", "2: Punishment", "3: Learning",
                       "4: Competition", "5: Mutation"]
        stage_text = self.font.render(f"Stage: {stage_names[self.current_stage]}",
                                      True, (0, 0, 0))
        self.screen.blit(stage_text, (20, 20))

        # Draw speed label
        speed_text = self.font.render(f"Speed: {self.speed:.1f}x", True, (0, 0, 0))
        self.screen.blit(speed_text, (20, 50))

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
            pygame.draw.rect(self.screen, color, (legend_x, legend_y + i * 25, 15, 15))
            pygame.draw.rect(self.screen, (0, 0, 0), (legend_x, legend_y + i * 25, 15, 15), 1)

            # Draw text
            text = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text, (legend_x + 25, legend_y + i * 25))

        # Draw instructions
        instructions = [
            "Space: Advance simulation",
            "Up/Down: Change speed",
            "Click: Select group",
            "Esc: Quit"
        ]

        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (0, 0, 0))
            self.screen.blit(text, (legend_x, legend_y + (i + 4) * 25))

    def _draw_connections(self) -> None:
        """Draw connections between interacting entities"""
        for source, target in self.stage_connections:
            if hasattr(source, 'x') and hasattr(target, 'x'):  # Individuals
                # Draw dotted line between individuals
                start_pos = (source.x + INDIVIDUAL_SIZE // 2, source.y + INDIVIDUAL_SIZE // 2)
                end_pos = (target.x + INDIVIDUAL_SIZE // 2, target.y + INDIVIDUAL_SIZE // 2)
            else:  # Groups
                # Draw dotted line between groups
                start_pos = (source.x + source.width // 2, source.y + source.height // 2)
                end_pos = (target.x + target.width // 2, target.y + target.height // 2)

            # Draw dotted line
            draw_dotted_line(self.screen, COLOR_CONNECTION, start_pos, end_pos)

    def run(self) -> None:
        """Run the simulation main loop"""
        running = True
        step_timer = 0

        while running:
            # Handle events
            running = self.handle_events()

            # Auto-advance based on speed
            step_timer += self.speed
            if step_timer >= 60:  # Advance every 60 / speed frames
                self.run_step()
                step_timer = 0

            # Render
            self.render()

            # Cap framerate
            self.clock.tick(60)

        # Clean up
        pygame.quit()

if __name__ == "__main__":
    # Create and run the simulation
    # Example: 3 levels, 5 individuals per first-order group,
    # 3 first-order groups per second-order group,
    # 2 second-order groups per third-order group
    sim = Simulation(group_sizes=[10, 5, 1])
    sim.run()