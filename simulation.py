import logging
import math
import random

import pygame
from typing import List

from constants import INITIAL_COOPERATOR_RATIO, INITIAL_PUNISHER_RATIO
from group import Group
from individual import Role, Individual
from renderer import Renderer

MIN_SPEED = 0.1

MAX_SPEED = 100.0


class Simulation:
    """Class managing the multi-level selection simulation"""

    def __init__(self,
                 group_sizes: List[int],
                 have_punisher = True,
                 initial_cooperator_ratio: float = INITIAL_COOPERATOR_RATIO,
                 initial_punisher_ratio: float = INITIAL_PUNISHER_RATIO):
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
        if not have_punisher:
            self.initial_punisher_ratio = 0

        # Animation speed (frames per second)
        self.speed = 1.0

        # Current state
        self.selected_group = None
        self.current_stage = -1
        self.stage_connections = []
        self.connection_timer = 0

        # whether single step modus is on or off
        self.single_step_mode = False

        # Initialize the simulation
        self.root_group = self._create_hierarchy(group_sizes, have_punisher = have_punisher)

        # Initialize renderer
        self.renderer = Renderer(havePunisher=have_punisher)
        self.renderer.calculate_positions(self.root_group, self.group_sizes)

    def _create_hierarchy(self, sizes: List[int], level: int = None, have_punisher = False) -> Group:
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

                individuals.append(Individual(role, have_punisher))
            return Group(individuals, 1)
        else:
            # Create a higher-order group with subgroups
            subgroups = []
            for _ in range(sizes[level - 1]):
                subgroups.append(self._create_hierarchy(sizes, level - 1, have_punisher))
            return Group(subgroups, level)

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

        if not self.single_step_mode:
            self.connection_timer = 30  # Show connections for 30 frames
        else:
            self.connection_timer = math.inf
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
                    self.speed = min(self.speed * 1.5, MAX_SPEED)
                elif event.key == pygame.K_DOWN:
                    self.speed = max(self.speed / 1.5, MIN_SPEED)
                if event.key == pygame.K_s:  # Toggle single-step mode
                    self.single_step_mode = not self.single_step_mode
                    self.renderer.single_step_mode = self.single_step_mode
                elif event.key == pygame.K_RIGHT and self.single_step_mode:
                    self.run_step()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Select group on click
                self.selected_group = self.renderer.find_group_at_position(
                    self.root_group, event.pos[0], event.pos[1])

        return True

    def run(self) -> None:
        """Run the simulation main loop"""
        running = True
        step_timer = 0

        while running:
            # Handle events
            running = self.handle_events()

            # If not single step mode, auto-advance based on speed
            if not self.single_step_mode:
                step_timer += self.speed
                if step_timer >= 60: # Advance every 60 / speed frames
                    self.run_step()
                    step_timer = 0

            # Render
            self.renderer.render(
                self.root_group,
                self.selected_group,
                self.current_stage,
                self.speed,
                self.stage_connections,
                self.connection_timer
            )

            # Update connection timer if active
            if self.connection_timer > 0:
                self.connection_timer -= 1

            # Cap framerate
            self.renderer.get_clock().tick(60)

        # Clean up
        pygame.quit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # Create and run the simulation
    # individuals per group, first level groups, second leve groups

    # single group scenario, no punishers
    sim = Simulation(group_sizes=[6, 1, 1], initial_cooperator_ratio=0.5, have_punisher=False)

    # multiple group scenario, no punishers
    #sim = Simulation(group_sizes=[50, 1, 6], initial_cooperator_ratio=0.5, have_punisher=False)

    # single group scenario, few punishers
    #sim = Simulation(group_sizes=[50, 1, 1], initial_cooperator_ratio=0.4, initial_punisher_ratio=0.1, have_punisher=True)

    # single group scenario, many punishers
    #sim = Simulation(group_sizes=[50, 1, 1], initial_cooperator_ratio=0.4, initial_punisher_ratio=0.4, have_punisher=True)

    # multiple group scenario, many punishers
    #sim = Simulation(group_sizes=[20, 3, 3], initial_cooperator_ratio=0.4, initial_punisher_ratio=0.4, have_punisher=True)

    sim.run()