import logging
import random
import pygame
from typing import List, Union

from constants import ERROR_RATE, PUNISHER_COST, PUNISHMENT_COST, COMPETITION_CHANCE, COLOR_GROUP_FRAME, \
    COLOR_SELECTION, MIGRATION_RATE, COOPERATION_COST, LEARNING_RATE
from individual import Individual, Role
from individual_renderer import IndividualRenderer


class Group:
    """Class representing a group of individuals or subgroups"""

    def __init__(self, members: List[Union['Group', Individual]] = None, level: int = 1):
        """Initialize a group with given members or empty"""
        self.members = members if members is not None else []
        self.level = level  # 1 for first-order groups containing individuals

        # Position for rendering
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def is_first_order(self) -> bool:
        """Check if this is a first-order group (containing individuals)"""
        return self.level == 1

    def get_all_individuals(self) -> List[Individual]:
        """Get all individuals in this group recursively"""
        if self.is_first_order():
            return self.members  # type: ignore - we know these are Individuals in first-order groups

        individuals = []
        for subgroup in self.members:  # type: ignore - we know these are Groups in higher-order groups
            individuals.extend(subgroup.get_all_individuals())
        return individuals

    def get_first_order_groups(self) -> List['Group']:
        """Get all first-order groups in this group recursively"""
        if self.is_first_order():
            return [self]

        first_order_groups = []
        for subgroup in self.members:  # type: ignore - we know these are Groups in higher-order groups
            if subgroup.is_first_order():
                first_order_groups.append(subgroup)
            else:
                first_order_groups.extend(subgroup.get_first_order_groups())
        return first_order_groups

    def clone(self) -> 'Group':
        """Create a copy of this group with cloned members"""
        if self.is_first_order():
            # Clone individuals
            cloned_members = [member.clone() for member in self.members]  # type: ignore
        else:
            # Clone subgroups
            cloned_members = [member.clone() for member in self.members]  # type: ignore

        cloned_group = Group(cloned_members, self.level)
        return cloned_group

    def stage1_cooperation(self) -> None:
        """Stage 1: Cooperation stage"""
        if self.is_first_order():
            for individual in self.members:  # type: ignore
                # Determine if the individual cooperates based on role and error rate
                if individual.role == Role.COOPERATOR or individual.role == Role.PUNISHER:
                    individual.cooperates = random.random() > ERROR_RATE
                    individual.payoff -= COOPERATION_COST
                else:  # Role.DEFECTOR
                    individual.cooperates = False
            # determine cooperation payoff by percentage of cooperating individuals
            no_of_cooperators = (len([m for m in self.members if m.role == Role.COOPERATOR and m.cooperates]) +
                                 0.6 * len([m for m in self.members if m.role == Role.COOPERATOR and m.cooperates]))
            coop_gain = no_of_cooperators / len(self.members) / 3
            logging.info("gain from %i cooperators: %f", no_of_cooperators, coop_gain)
            # apply payoff gain and costs fo
            for individual in self.members:  # type: ignore
                individual.payoff += coop_gain
                self.sanitize_payoff(individual)
            self.log_members("stage1_cooperation")
        else:
            # For higher-order groups, apply to all subgroups
            for subgroup in self.members:  # type: ignore
                subgroup.stage1_cooperation()

    def stage2_punishment(self) -> List[tuple]:
        """Stage 2: Punishment stage, returns list of punisher-defector connections"""
        connections = []

        if self.is_first_order():
            # Get all punishers and non-cooperators in this group
            punishers = [ind for ind in self.members if ind.role == Role.PUNISHER]  # type: ignore
            defectors = [ind for ind in self.members if not ind.cooperates]  # type: ignore

            # Each punisher punishes all defectors
            for punisher in punishers:
                n = len(defectors)  # Number of defectors

                # Each punisher pays a cost to punish each defector
                if n > 0:
                    punisher_cost_per_defector = PUNISHER_COST / n
                    punishment_per_defector = PUNISHMENT_COST / n

                    # Apply punishment
                    for defector in defectors:
                        punisher.payoff -= punisher_cost_per_defector
                        defector.payoff -= punishment_per_defector
                        self.sanitize_payoff(punisher)
                        self.sanitize_payoff(defector)
                        connections.append((punisher, defector))
            self.log_members("stage2_punishment")
        else:
            # For higher-order groups, apply to all first-order subgroups
            for group in self.get_first_order_groups():
                connections.extend(group.stage2_punishment())

        return connections

    def stage3_learning(self) -> List[tuple]:
        """Stage 3: Payoff-biased learning stage, returns list of learner-teacher connections"""
        connections = []

        if self.level == 2:  # Only apply to second-order groups
            # Get all first-order groups
            first_order_groups = self.get_first_order_groups()

            # For each individual in each first-order group
            for group_idx, group in enumerate(first_order_groups):
                learning_individuals = [i for i in group.members if random.random() < LEARNING_RATE]
                for individual in group.members:  # type: ignore
                    # Determine if interaction is within-group or between-group
                    if random.random() < MIGRATION_RATE:
                        # Between-group interaction: choose a random different group
                        other_groups = [g for i, g in enumerate(first_order_groups) if i != group_idx]
                        if not other_groups:
                            continue

                        other_group = random.choice(other_groups)
                        # Choose a random individual from that group
                        chosen_individual = random.choice(other_group.members)  # type: ignore
                    else:
                        # Within-group interaction: choose a random different individual from same group
                        other_individuals = [ind for ind in group.members if ind != individual]  # type: ignore
                        if not other_individuals:
                            continue

                        chosen_individual = random.choice(other_individuals)

                    # Determine if individual adopts the role of chosen individual
                    p_i = max(individual.payoff, 0.01)  # Ensure non-zero
                    p_c = max(chosen_individual.payoff, 0.01)  # Ensure non-zero

                    if random.random() < (p_c / (p_c + p_i)):
                        individual.role = chosen_individual.role
                        connections.append((individual, chosen_individual))
                logging.info("stage3_learning: %s", repr(group.members))

        elif self.level > 2:
            # For higher-order groups, apply to all second-order subgroups
            for subgroup in self.members:  # type: ignore
                if subgroup.level == 2:
                    connections.extend(subgroup.stage3_learning())
                else:
                    connections.extend(subgroup.stage3_learning())

        return connections

    def stage4_competition(self) -> List[tuple]:
        """Stage 4: Competition between groups, returns list of competing group connections"""
        connections = []

        if self.level > 1:  # Only apply to higher-order groups
            # Shuffle the list of subgroups
            subgroups = list(self.members)  # type: ignore
            random.shuffle(subgroups)

            # Pair subgroups and have them compete
            for i in range(0, len(subgroups), 2):
                if i + 1 < len(subgroups) and random.random() < COMPETITION_CHANCE:
                    group1 = subgroups[i]
                    group2 = subgroups[i + 1]

                    # Calculate cooperation rates
                    g1_individuals = group1.get_all_individuals()
                    g2_individuals = group2.get_all_individuals()

                    c1 = sum(1 for ind in g1_individuals if ind.role in [Role.COOPERATOR, Role.PUNISHER]) / len(
                        g1_individuals)
                    c2 = sum(1 for ind in g2_individuals if ind.role in [Role.COOPERATOR, Role.PUNISHER]) / len(
                        g2_individuals)

                    # Calculate win probability for group1
                    win_prob = 0.5 + (c1 - c2) / 2

                    # Determine winner
                    if random.random() < win_prob:
                        # Group 1 wins
                        winner, loser = group1, group2
                    else:
                        # Group 2 wins
                        winner, loser = group2, group1

                    # Replace loser with clone of winner
                    winner_clone = winner.clone()

                    # Find the index of the loser in self.members
                    loser_index = self.members.index(loser)  # type: ignore

                    # Replace loser with clone of winner
                    self.clone_coordinates(loser, winner_clone)

                    logging.info("loser %s will be replaced by winner %s", repr(loser), repr(winner))
                    self.members[loser_index] = winner_clone  # type: ignore

                    connections.append((winner, loser))

            # Recursively apply to subgroups
            for subgroup in self.members:  # type: ignore
                if not subgroup.is_first_order():
                    connections.extend(subgroup.stage4_competition())

        return connections

    def stage5_mutation(self) -> None:
        """Stage 5: Mutation of individuals"""
        for individual in self.get_all_individuals():
            individual.mutate()

    def sanitize_payoff(self, individual):
        individual.payoff = max(individual.payoff, 0.01)
        individual.payoff = min(individual.payoff, 1.00)

    def log_members(self, stage):
        logging.info("%s: %s", stage, repr(self.members))

    def clone_coordinates(self, loser, winner_clone):
        winner_clone.x = loser.x
        winner_clone.y = loser.y
        winner_clone.width = loser.width
        winner_clone.height = loser.height
        if winner_clone.members != None:
            for (i, val) in enumerate(loser.members):
                self.clone_coordinates(val, winner_clone.members[i])

    def render(self, surface, is_selected=False):
        """Render the group as a rectangle containing its members"""
        # Render frame
        frame_color = COLOR_SELECTION if is_selected else COLOR_GROUP_FRAME
        pygame.draw.rect(surface, frame_color, (self.x, self.y, self.width, self.height), 2)
        renderer = IndividualRenderer()
        # Render members
        if self.is_first_order():
            for individual in self.members:  # type: ignore
                renderer.render(individual, surface)
        else:
            for subgroup in self.members:  # type: ignore
                subgroup.render(surface)

    def __repr__(self):
        return ("[" + repr(self.members) +"]")
