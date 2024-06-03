'''
Inspiration Source: https://github.com/hasnainroopawalla/Ant-Colony-Optimization/blob/master/aco_routing/aco.py
'''


class WaveConfig:
    """
    encapsulates all parameters for a wave in an object
    """

    # Maximum number of steps an ant is allowed is to take in order to reach the destination
    ant_max_steps: int = 20

    # Number of cycles/waves of search ants to be deployed
    max_iterations: int = 15

    # Indicates if the search ants should spawn at random nodes in the graph
    ant_random_spawn: bool = False

    # Sets a manual start node, if it is not random
    ant_spawn_node: str = "S"

    # Evaporation rate (rho)
    evaporation_rate: float = 0.1

    # Pheromone bias
    alpha: float = 0.7

    # Edge cost bias
    beta: float = 0.3

    # Pick a random edge by chance
    random_chance: float = 0.05

    # Search ants
    concurrent_ants: int = 2

    # type of ant: random | routing | minority
    ant_class: str = "routing"

    # if the ant puts pheromones on its way or just backwards once on success
    put_pheromones_always: bool = False

    # if the ant dies at first success node
    stop_on_success: bool = True

    # Minority Ant: If weakest trace should be selected only from traces edges
    prioritize_pheromone_routes: bool = False

    # Sleep times for different loops
    step_sleep: float = 0.5
    iteration_sleep: float = 0.5
    wave_sleep: float = 0.5

    # change graph values for this wave
    node_value_changes: dict

    # remove edges
    remove_edges: list[list[str]]
    
    # clear pheromones before start
    clear_pheromones: bool = False

    def __init__(self, wave: dict):
        self.ant_class = wave.get('class', 'routing')
        self.ant_max_steps = wave.get('ant_max_steps', 20)
        self.max_iterations = wave.get('max_iterations', 15)
        self.ant_random_spawn = wave.get('random_spawn', False)
        self.ant_spawn_node = wave.get('spawn_node', "AU")
        self.evaporation_rate = wave.get('evaporation_rate', 0.1)
        self.alpha = wave.get('alpha', 0.7)
        self.beta = wave.get('beta', 0.3)
        self.random_chance = wave.get('random_chance', 0.05)
        self.concurrent_ants = wave.get('concurrent_ants', 2)
        self.put_pheromones_always = wave.get('put_pheromones_always', False)
        self.stop_on_success = wave.get('stop_on_success', True)
        self.prioritize_pheromone_routes = wave.get('prioritize_pheromone_routes', False)

        self.step_sleep = wave.get('step_sleep', 0.5)
        self.iteration_sleep = wave.get('iteration_sleep', 0.5)
        self.wave_sleep = wave.get('wave_sleep', 0.5)

        self.node_value_changes = wave.get('node_value_changes', {})
        self.remove_edges = wave.get('remove_edges', [])
        
        self.clear_pheromones = wave.get('clear_pheromones', False)

    def to_dict(self):
        """
        Convert the wave configuration to a JSON-compatible dictionary.
        :return: A dictionary containing the wave configuration parameters
        :rtype: dict
        """
        return {
            'class': self.ant_class,
            'ant_max_steps': self.ant_max_steps,
            'max_iterations': self.max_iterations,
            'random_spawn': self.ant_random_spawn,
            'spawn_node': self.ant_spawn_node,
            'evaporation_rate': self.evaporation_rate,
            'alpha': self.alpha,
            'beta': self.beta,
            'random_chance': self.random_chance,
            'concurrent_ants': self.concurrent_ants,
            'put_pheromones_always': self.put_pheromones_always,
            'stop_on_success': self.stop_on_success,
            'prioritize_pheromone_routes': self.prioritize_pheromone_routes,
            'step_sleep': self.step_sleep,
            'iteration_sleep': self.iteration_sleep,
            'wave_sleep': self.wave_sleep,
            'node_value_changes': self.node_value_changes,
            'remove_edges': self.remove_edges,
            'clear_pheromones': self.clear_pheromones
        }


