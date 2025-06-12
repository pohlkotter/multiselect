# Constants
INITIAL_COOPERATOR_RATIO = 0
INITIAL_PUNISHER_RATIO = 1

ERROR_RATE = 0.05  # Error rate for cooperation (e)
COOPERATION_COST = 0.2  # Cost of cooperation
COOPERATION_GAIN = 0.4 # Gain of cooperation
UPKEEP_COST = 0.05 # Cost of daily life to upkeep status quo
PUNISHMENT_COST = 0.8  # Cost to the punished individual (p)
PUNISHER_COST = 0.2  # Cost to the punisher (k)
LEARNING_RATE = 0.05  # Probability of individual learning from any other individual
MIGRATION_RATE = 0.01  # Probability of interacting with other groups (m)
COMPETITION_CHANCE = 0.2  # Chance of competition between groups
MUTATION_CHANCE = 0.02  # Chance of mutation for each individual

# Colors
COLOR_COOPERATOR = (0, 255, 0)  # Green
COLOR_PUNISHER = (0, 0, 0)  # Black
COLOR_DEFECTOR = (255, 0, 0)  # Red
COLOR_GROUP_FRAME = (100, 100, 100)  # Gray
COLOR_SELECTION = (0, 0, 255)  # Blue
COLOR_CONNECTION = (0, 0, 0)  # Black

# Screen settings
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
INDIVIDUAL_SIZE = 20
MARGIN = 5
