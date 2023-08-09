import random
from ucb import main, interact, trace
from collections import OrderedDict

class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name, exit=None):
        self.name = name
        self.exit = exit
        self.bees = []        # A list of Bees
        self.ant = None       # An Ant
        self.entrance = None  # A Place
        if exit != None:
            exit.entrance = self

    def add_insect(self, insect):
        """
        Asks the insect to add itself to the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect):
        """
        Asks the insect to remove itself from the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    damage = 0
    is_waterproof = False

    def __init__(self, health, place=None):
        """Creates an Insect with a health amount and a starting PLACE."""
        self.health = health
        self.place = place  # set by Place.add_insect and Place.remove_insect
        self.is_waterproof = False
    def reduce_health(self, amount):
        """Reduces health by AMOUNT, and removes the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.death_callback()
            self.place.remove_insect(self)

    def action(self, gamestate):
        """The action performed each turn.

        gamestate -- The GameState, used to access game state information.
        """

    def death_callback(self):
        # overriden by the gui
        pass

    def add_to(self, place):
        """Adds this Insect to the given Place
        """
        self.place = place

    def remove_from(self, place):
        self.place = None


    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False
    food_cost = 0
    is_container = False

    def __init__(self, health=1):
        """Creates an Insect with a HEALTH quantity."""
        super().__init__(health)

    def can_contain(self, other):
        return False

    def store_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
        else:
            if place.ant.is_container and place.ant.can_contain(self):
                place.ant.store_ant(self)
            elif self.is_container and self.can_contain(place.ant):
                self.store_ant(place.ant)
                place.ant = self
            else:
                assert place.ant is None, 'Two ants in {0}'.format(place)
        Insect.add_to(self, place)

    def remove_from(self, place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def buff(self):
        """Doubles this ants's damage, if it has not already been buffed."""
        self.damage = self.damage * 2

class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    food_cost = 2

    def action(self, gamestate):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        gamestate.food += 1



class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    damage = 1
    food_cost = 3
    min_range = 0
    max_range = float('inf')
    def nearest_bee(self):
        """Returns the nearest Bee in a Place that is not the HIVE, connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        current_place = self.place
        counter = 0
        while not current_place.is_hive:
            if self.min_range<=counter<=self.max_range and current_place.bees:
                return random_bee(current_place.bees)
            counter = counter + 1
            current_place = current_place.entrance
        return None

    def throw_at(self, target):
        """Throws a leaf at the TARGET Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate):
        """Throws a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())

def random_bee(bees):
    """Returns a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    max_range = 3
    implemented = True   # Change to True to view in the GUI

class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    min_range = 5
    implemented = True 

class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    implemented = True

    def __init__(self, health=3):
        """Creates an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the FireAnt from its place if it
        has no health remaining.
        """

        for bee in self.place.bees[:]:
            bee.reduce_health(amount)
        
        if self.health <= amount:
            for bee in self.place.bees[:]:
                bee.reduce_health(self.damage)
            super().reduce_health(amount)
        else:
            super().reduce_health(amount)


class WallAnt(Ant):
    """A WallAnt that does not do any action."""

    name = 'Wall'
    food_cost = 4
    max_range = 0
    implemented = True 

    def __init__(self, health=4):
        super().__init__(health)

class HungryAnt(Ant):
    """A HungryAnt that selects a random bee from its place and eats it whole."""

    name = 'Hungry'
    food_cost = 4
    max_range = 0
    chew_duration = 3
    implemented = True

    def __init__(self, health=1):
        self.chew_countdown = 0
        super().__init__(health)
    def action(self, gamestate):
        "Checks to see if HungryAnt is chewing. If so, decrements chew_countdown by 1. If not, eats a random_bee in its place by reducing the bee's health to 0."
        if self.chew_countdown > 0:
            self.chew_countdown -= 1
        else:
            if len(self.place.bees) > 0:
                bee = random_bee(self.place.bees)
                bee.reduce_health(bee.health)
                self.chew_countdown = self.chew_duration


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ant_contained = None

    def can_contain(self, other):
        if self.ant_contained is None and other.is_container is False:
            return True
        else:
           return  False
        self.health = other.health

    def store_ant(self, ant):
        self.ant_contained = ant

    def remove_ant(self, ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place):
        if place.ant is self:
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            Ant.remove_from(self, place)

    def action(self, gamestate):
        if self.ant_contained:
            self.ant_contained.action(gamestate)

class BodyguardAnt(ContainerAnt):
    name = 'Bodyguard'
    food_cost = 4
    def __init__(self, health=2):
        super().__init__(health)
    implemented = True

class TankAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants and does 1 damage to all bees in its place each turn."""

    name = 'Tank'
    food_cost = 6
    damage = 1
    implemented = True 
    def __init__(self, health=2,damage = 1):
        super().__init__(health)
        self.health = health
        self.damage = damage

    def action(self, gamestate):
        copy_bees = list(self.place.bees)
        super().action(gamestate)
        for bee in copy_bees:
            bee.reduce_health(self.damage)


class Water(Place):

    def add_insect(self, insect):
        super().add_insect(insect)
        if insect.is_waterproof is False:
            insect.reduce_health(insect.health)

class ScubaThrower(ThrowerAnt):
    """A ScubaThrower that goes in the water."""

    name = 'Scuba'
    food_cost = 6
    is_waterproof = True
    def __init__(self, health = 1, place=None):
        self.place = place
        self.health = health
        self.is_waterproof = True
    implemented = True


class QueenAnt(ScubaThrower): 
    """The Queen of the colony. The game is over if a bee enters her place."""

    name = 'Queen'
    food_cost = 7
    was_doubled = True
    implemented = True 

    def __init__(self, gamestate,health = 1):
         self.health = health

    def action(self, gamestate):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """

        super().action(gamestate)
        current_place = self.place.exit

        while current_place:
            if current_place.ant != None:
                current_place.ant.double()
            current_place = current_place.exit


    def reduce_health(self, amount):

        super().reduce_health(amount)
        if self.health <= 0:
            ants_lose()





class AntRemover(Ant):
    """Allows the player to remove ants from the board in the GUI."""

    name = 'Remover'
    implemented = False

    def __init__(self):
        super().__init__(0)

class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True
    def __init__(self, health, place=None):
        self.health = health
        self.place = place 
        self.is_waterproof = True

    def sting(self, ant):
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place):
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self):
        """Return True if this Bee cannot advance to the next Place."""
        return self.place.ant is not None

    def action(self, gamestate):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.
        """
        destination = self.place.exit


        if self.blocked():
            self.sting(self.place.ant)
        elif self.health > 0 and destination is not None:
            self.move_to(destination)

    def add_to(self, place):
        place.bees.append(self)
        Insect.add_to(self, place)

    def remove_from(self, place):
        place.bees.remove(self)
        Insect.remove_from(self, place)

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1


class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2

class Hornet(Bee):
    """Class of bee that is capable of taking two actions per turn, although
    its overall damage output is lower. Immune to statuses.
    """
    name = 'Hornet'
    damage = 0.25

    def action(self, gamestate):
        for i in range(2):
            if self.health > 0:
                super().action(gamestate)

    def __setattr__(self, name, value):
        if name != 'action':
            object.__setattr__(self, name, value)

class NinjaBee(Bee):
    """A Bee that cannot be blocked. Is capable of moving past all defenses to
    assassinate the Queen.
    """
    name = 'NinjaBee'

    def blocked(self):
        return False

class Boss(Wasp, Hornet):
    """The leader of the bees. Combines the high damage of the Wasp along with
    status immunity of Hornets. Damage to the boss is capped up to 8
    damage by a single attack.
    """
    name = 'Boss'
    damage_cap = 8
    action = Wasp.action

    def reduce_health(self, amount):
        super().reduce_health(self.damage_modifier(amount))

    def damage_modifier(self, amount):
        return amount * self.damage_cap/(self.damage_cap + amount)

class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees:
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)


class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, strategy, beehive, ant_types, create_places, dimensions, food=2):
        """Creates a GameState for simulating a game.

        Arguments:
        strategy -- a function to deploy ants to places
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.strategy = strategy
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)

    def configure(self, beehive, create_places):
        """Configures the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []
        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place, self.dimensions[0], self.dimensions[1])

    def simulate(self):
        """Simulates an attack on the ant colony (i.e., play the game)."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self)         # Bees invade
                self.strategy(self)                 # Ants deploy
                for ant in self.ants:               # Ants take actions
                    if ant.health > 0:
                        ant.action(self)
                for bee in self.active_bees[:]:     # Bees take actions
                    if bee.health > 0:
                        bee.action(self)
                    if bee.health <= 0:
                        num_bees -= 1
                        self.active_bees.remove(bee)
                if num_bees == 0:
                    raise AntsWinException()
                self.time += 1
        except AntsWinException:
            print('All bees are vanquished. You win!')
            return True
        except AntsLoseException:
            print('The ant queen has perished. Please try again.')
            return False

    def deploy_ant(self, place_name, ant_type_name):
        """Places an ant if enough food is available.
        """
        constructor = self.ant_types[ant_type_name]
        if self.food < constructor.food_cost:
            print('Not enough food remains to place ' + ant_type_name)
            raise NotEnoughFoodException()
        if constructor.__name__ == 'QueenAnt':
            try:
                ant = constructor(self)
            except DuplicateQueensException:
                print("you cannot create a second QueenAnt")
        else:
            ant = constructor()

        if ant:
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Removes an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status

class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen resides."""

    def add_insect(self, insect):
        """Adds an Insect to this Place.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()

def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()

def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()

def ant_types():
    """Returns a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]

class GameOverException(Exception):
    """Base game over Exception."""
    pass

class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass

class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass

class DuplicateQueensException(Exception):
    """Occurs when more than one queen gets created."""
    pass

class NotEnoughFoodException(Exception):
    """Occurs when there is not enough food to create an Ant."""
    pass

def interactive_strategy(gamestate):
    """A strategy that starts an interactive session and lets the user make
    changes to the gamestate.
    """
    print('gamestate: ' + str(gamestate))
    msg = '<Control>-D (<Control>-Z <Enter> on Windows) completes a turn.\n'
    interact(msg)


def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Registers a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)

def dry_layout(queen, register_place, tunnels=3, length=9):
    """Registers dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.
    """

    def add_wave(self, bee_type, bee_health, time, count):
        """Adds a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    @property
    def all_bees(self):
        """Places all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]
