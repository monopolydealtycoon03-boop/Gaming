import random
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

SET_SIZES = {
    'Brown': 2, 'Light Blue': 3, 'Pink': 3, 'Orange': 3,
    'Red': 3, 'Yellow': 3, 'Green': 3, 'Dark Blue': 2,
    'Railroad': 4, 'Utility': 2
}

class Card:
    def __init__(self, card_type, name, value, color=None, is_wildcard=False, wildcard_options=None):
        self.card_type = card_type
        self.name = name
        self.value = value
        self.color = color
        self.is_wildcard = is_wildcard
        self.wildcard_options = wildcard_options if wildcard_options else []

    def __str__(self):
        if self.card_type == 'Property':
            if self.is_wildcard:
                return f"[WILD] {self.name} (Value: {self.value}M)"
            return f"[{self.color}] {self.name} (Value: {self.value}M)"
        elif self.card_type == 'Action':
            return f"[Action] {self.name} (Value: {self.value}M)"
        elif self.card_type == 'Building':
            return f"[Building] {self.name} (Value: {self.value}M)"
        return f"[Money] {self.name} (Value: {self.value}M)"

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bank = []
        self.properties = []
        self.buildings = {} # Maps color to list of building cards (House/Hotel)

    def draw(self, deck, discard_pile, count=1):
        for _ in range(count):
            if not deck and discard_pile:
                print("\n🔄 Deck is empty! Reshuffling discard pile...")
                deck.extend(discard_pile)
                random.shuffle(deck)
                discard_pile.clear()
                time.sleep(1.5)
            if deck:
                self.hand.append(deck.pop())

    def show_hand(self):
        print(f"\n--- {self.name}'s SECRET HAND ---")
        for i, card in enumerate(self.hand):
            print(f"{i + 1}. {card}")
        print("---------------------------------")

    def get_completed_sets(self):
        """Returns a list of completed colors. If a player has 2 sets of Brown, 'Brown' appears twice."""
        color_counts = {}
        for p in self.properties:
            if p.color:
                color_counts[p.color] = color_counts.get(p.color, 0) + 1
            
        completed = []
        for color, count in color_counts.items():
            num_sets = count // SET_SIZES.get(color, 99)
            for _ in range(num_sets):
                completed.append(color)
        return completed

    def get_tradable_properties(self):
        """Returns properties that are NOT currently locked into a completed set."""
        color_groups = {}
        for p in self.properties:
            color = p.color if p.color else "Other"
            if color not in color_groups: color_groups[color] = []
            color_groups[color].append(p)
            
        tradable = []
        for color, cards in color_groups.items():
            if color == "Other":
                tradable.extend(cards)
                continue
            req = SET_SIZES.get(color, 99)
            remainder = len(cards) % req
            if remainder > 0:
                # The extra properties outside the full set are unprotected
                tradable.extend(cards[-remainder:])
        return tradable

    def validate_buildings(self):
        """Checks if completed sets broke. If so, pops buildings into the bank."""
        for color, bldgs in list(self.buildings.items()):
            if bldgs:
                count = sum(1 for p in self.properties if p.color == color)
                req = SET_SIZES.get(color, 99)
                if count < req:
                    print(f"⚠️ {self.name}'s {color} set broke! Building(s) moved to Bank.")
                    self.bank.extend(bldgs)
                    self.buildings[color] = []

    def show_board(self):
        bank_total = sum(c.value for c in self.bank)
        print(f"\n--- {self.name}'s Table ---")
        print(f"💰 Bank Total: {bank_total}M")
        
        props_by_color = {}
        for p in self.properties:
            color_key = p.color if p.color else "Other"
            if color_key not in props_by_color:
                props_by_color[color_key] = []
            display_name = f"{p.name} (WILD)" if p.is_wildcard else p.name
            props_by_color[color_key].append(display_name)
            
        full_sets = len(self.get_completed_sets())
        if not props_by_color:
            print("🏠 Properties: None")
        else:
            print("🏠 Properties:")
            for color, names in props_by_color.items():
                if color != "Other":
                    sets_completed = len(names) // SET_SIZES[color]
                    status = f" (FULL SET x{sets_completed}!)" if sets_completed > 0 else f" ({len(names) % SET_SIZES[color]}/{SET_SIZES[color]})"
                    print(f"    [{color}]{status}: {', '.join(names)}")
                    
                    if color in self.buildings and self.buildings[color]:
                        b_names = [b.name for b in self.buildings[color]]
                        print(f"      + Buildings: {', '.join(b_names)}")
                else:
                    print(f"    [Other]: {', '.join(names)}")
                
        print(f"🏆 Full Sets Collected: {full_sets}/3")
        
    def check_win(self):
        return len(self.get_completed_sets()) >= 3

    def pay_to(self, amount, payee):
        print(f"\n💸 --- PAYMENT REQUIRED --- 💸")
        print(f"{self.name}, you owe {amount}M to {payee.name}!")
        print(f"⚠️ RULE: You can ONLY pay with cards currently on your board (Bank or Properties).")
        
        paid = 0
        while paid < amount:
            if not self.bank and not self.properties:
                print(f"\n❌ {self.name} has no more assets on the board! They pay what they can, and the rest is forgiven.")
                break
                
            print(f"\nAmount remaining to pay: {amount - paid}M")
            self.show_board()
            
            print("\nWhere do you want to pay from?")
            if self.bank: print("[1] Bank")
            if self.properties: print("[2] Properties")
            
            choice = input("Choice: ")
            
            if choice == '1' and self.bank:
                print("\nSelect a Bank card to give:")
                for idx, c in enumerate(self.bank):
                    print(f"[{idx + 1}] {c.name} ({c.value}M)")
                try:
                    c_idx = int(input("Choice: ")) - 1
                    if 0 <= c_idx < len(self.bank):
                        card = self.bank.pop(c_idx)
                        payee.bank.append(card)
                        paid += card.value
                        print(f"Paid {card.value}M!")
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
                    
            elif choice == '2' and self.properties:
                print("\nSelect a Property to give (Value goes towards debt):")
                for idx, c in enumerate(self.properties):
                    color_disp = c.color if c.color else "Other"
                    print(f"[{idx + 1}] {c.name} ({color_disp}, Value: {c.value}M)")
                try:
                    c_idx = int(input("Choice: ")) - 1
                    if 0 <= c_idx < len(self.properties):
                        card = self.properties.pop(c_idx)
                        payee.properties.append(card)
                        paid += card.value
                        
                        # Validate buildings now that a property was lost
                        self.validate_buildings()
                            
                        print(f"Handed over {card.name} (Worth {card.value}M)!")
                    else:
                        print("Invalid choice.")
                except ValueError:
                    print("Please enter a number.")
            else:
                print("Invalid choice. Try again.")

def run_jsn_battle(attacker, defender, initial_action_name, discard_pile):
    """
    Handles the ping-pong battle of Just Say No! cards.
    Returns True if the action is officially CANCELED. Returns False if it PROCEEDS.
    """
    current_target = defender
    current_challenger = attacker
    action_canceled = False
    
    print(f"\n🚨 WAIT! {attacker.name} is targeting {defender.name} with {initial_action_name}!")
    
    while True:
        jsn_idx = -1
        for i, card in enumerate(current_target.hand):
            if card.name == "Just Say No!":
                jsn_idx = i
                break
                
        if jsn_idx != -1:
            input(f"{current_target.name}, step up to the screen and press ENTER...")
            print(f"\n✋ 🛑 {current_target.name.upper()}, you have a 'Just Say No!' card in your hand.")
            action_status = "CANCEL" if not action_canceled else "FORCE"
            choice = input(f"Do you want to use it to {action_status} the action? (y/n): ").lower()
            if choice == 'y':
                discarded = current_target.hand.pop(jsn_idx)
                discard_pile.append(discarded)
                action_canceled = not action_canceled
                
                if action_canceled:
                    print(f"\n💥 BOOM! {current_target.name} played {discarded.name}! The action is CANCELED!")
                else:
                    print(f"\n💥 COUNTER-BOOM! {current_target.name} played {discarded.name}! The action is BACK ON!")
                time.sleep(2.5)
                
                # Swap roles for the potential counter-attack
                current_target, current_challenger = current_challenger, current_target
                continue
            else:
                break # They chose not to play their JSN
        else:
            break # No JSN in hand
            
    return action_canceled

def create_deck():
    deck = []
    # Money
    for _ in range(30): deck.append(Card('Money', '1M Bill', 1))
    for _ in range(20): deck.append(Card('Money', '2M Bill', 2))
    for _ in range(10): deck.append(Card('Money', '5M Bill', 5))
    
    # Standard Properties
    properties_data = [
        ('Brown', 1, ['Mediterranean Ave', 'Baltic Ave']),
        ('Light Blue', 1, ['Oriental Ave', 'Vermont Ave', 'Connecticut Ave']),
        ('Pink', 2, ['St. Charles Place', 'States Ave', 'Virginia Ave']),
        ('Orange', 2, ['St. James Place', 'Tennessee Ave', 'New York Ave']),
        ('Red', 3, ['Kentucky Ave', 'Indiana Ave', 'Illinois Ave']),
        ('Yellow', 3, ['Atlantic Ave', 'Ventnor Ave', 'Marvin Gardens']),
        ('Green', 4, ['Pacific Ave', 'North Carolina Ave', 'Pennsylvania Ave']),
        ('Dark Blue', 4, ['Park Place', 'Boardwalk']),
        ('Railroad', 2, ['Reading RR', 'Pennsylvania RR', 'B. & O. RR', 'Short Line RR']),
        ('Utility', 2, ['Water Works', 'Electric Company'])
    ]
    for color, value, names in properties_data:
        for name in names:
            deck.append(Card('Property', name, value, color))
            
    # Property Wildcards (2-color)
    wildcards_data = [
        ("Dark Blue/Green", 4, ['Dark Blue', 'Green'], 1),
        ("Light Blue/Brown", 1, ['Light Blue', 'Brown'], 1),
        ("Pink/Orange", 2, ['Pink', 'Orange'], 2),
        ("Red/Yellow", 3, ['Red', 'Yellow'], 2),
        ("Green/Railroad", 4, ['Green', 'Railroad'], 1),
        ("Light Blue/Railroad", 4, ['Light Blue', 'Railroad'], 1),
        ("Railroad/Utility", 2, ['Railroad', 'Utility'], 1)
    ]
    for name, value, colors, count in wildcards_data:
        for _ in range(count):
            deck.append(Card('Property', f'{name} Wild', value, color=None, is_wildcard=True, wildcard_options=colors))
            
    # Property Wildcards (10-color / ANY Color)
    all_colors = list(SET_SIZES.keys())
    for _ in range(2):
        deck.append(Card('Property', '10-Color Property Wild', 0, color=None, is_wildcard=True, wildcard_options=all_colors))
            
    # Buildings (House & Hotel)
    for _ in range(3): deck.append(Card('Building', 'House', 3))
    for _ in range(2): deck.append(Card('Building', 'Hotel', 4))
            
    # Actions
    actions = [
        ("Sly Deal", 3, 3), ("Forced Deal", 3, 3), ("Deal Breaker", 5, 2),
        ("Debt Collector", 5, 3), ("It's My Birthday", 2, 3),
        ("Pass Go", 1, 10), ("Just Say No!", 4, 3),
        ("Double The Rent!", 1, 2), ("Rent (Green/Dark Blue)", 1, 2),
        ("Rent (Brown/Light Blue)", 1, 2), ("Rent (Pink/Orange)", 1, 2),
        ("Rent (Red/Yellow)", 1, 2), ("Rent (Railroad/Utility)", 1, 2),
        ("Rent (Any Color)", 3, 3)
    ]
    for name, value, count in actions:
        for _ in range(count):
            deck.append(Card('Action', name, value))
            
    random.shuffle(deck)
    return deck

def play_game():
    clear_screen()
    print("Welcome to Property Tycoon (Secure Pass-and-Play Edition)!")
    print("Goal: Be the first player to collect 3 FULL PROPERTY SETS.\n")
    
    while True:
        try:
            num_players = int(input("How many players will be playing? (2-5): "))
            if 2 <= num_players <= 5:
                break
            print("Please enter a number between 2 and 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    players = []
    print("\n--- Enter Player Names ---")
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ").strip()
        if not name:
            name = f"Player {i+1}"
        players.append(Player(name))

    deck = create_deck()
    discard_pile = []
    
    for player in players:
        player.draw(deck, discard_pile, 5)
    
    turn = 0
    game_over = False
    
    while not game_over:
        current_player = players[turn % len(players)]
        
        clear_screen()
        print(f"\n{'='*40}")
        print(f"    🛑 PREPARING {current_player.name.upper()}'S TURN 🛑")
        print(f"{'='*40}")
        print(f"Everyone else, please look away! 👀")
        input(f"\n{current_player.name}, press ENTER when you are the only one looking at the screen...")
        
        print("\nDrawing 2 cards...")
        current_player.draw(deck, discard_pile, 2)
        time.sleep(1)
        actions_left = 3
        
        while actions_left > 0:
            clear_screen()
            
            print(f"=== 👁️ OPPONENTS' CARDS ON TABLE 👁️ ===")
            for p in players:
                if p != current_player:
                    p.show_board()
            print("=========================================\n")

            print(f"=== 👤 YOUR CARDS ({current_player.name.upper()}) 👤 ===")
            current_player.show_board()
            current_player.show_hand()
            
            print(f"\nActions remaining: {actions_left}")
            print("Options: [1-99] Play a Card | [0] End Turn")
            
            try:
                choice = int(input("Choose an option: "))
                
                if choice == 0:
                    break
                elif 1 <= choice <= len(current_player.hand):
                    played_card = current_player.hand.pop(choice - 1)
                    
                    if played_card.card_type == 'Money':
                        current_player.bank.append(played_card)
                        print("\nAdded to your Bank!")
                        actions_left -= 1
                        time.sleep(1.5)
                        
                    elif played_card.card_type == 'Property':
                        if played_card.is_wildcard:
                            print(f"\n🎨 You played a Wildcard! Choose a color to set it as:")
                            for idx, c in enumerate(played_card.wildcard_options):
                                print(f"[{idx + 1}] {c}")
                                
                            while True:
                                try:
                                    wc_choice = int(input("Choice: ")) - 1
                                    if 0 <= wc_choice < len(played_card.wildcard_options):
                                        played_card.color = played_card.wildcard_options[wc_choice]
                                        break
                                    print("Invalid choice. Try again.")
                                except ValueError:
                                    print("Please enter a valid number.")
                        
                        current_player.properties.append(played_card)
                        print(f"\nAdded to your Properties as {played_card.color}!")
                        actions_left -= 1
                        time.sleep(1.5)

                    elif played_card.card_type == 'Building':
                        print("\n1. Play to a Completed Set\n2. Bank as Money")
                        b_choice = input("Choice: ")
                        if b_choice == '2':
                            current_player.bank.append(played_card)
                            print("Banked for money!")
                            actions_left -= 1
                        else:
                            completed = current_player.get_completed_sets()
                            if not completed:
                                print("❌ You don't have any completed sets to build on! Card returned to hand.")
                                current_player.hand.append(played_card)
                                time.sleep(2)
                                continue
                            
                            print("\nSelect a full set to add this to:")
                            # unique choices for sets
                            unique_completed = list(set(completed))
                            for idx, c in enumerate(unique_completed):
                                print(f"[{idx + 1}] {c}")
                            try:
                                set_choice = int(input("Choice: ")) - 1
                                if 0 <= set_choice < len(unique_completed):
                                    chosen_color = unique_completed[set_choice]
                                    
                                    if chosen_color not in current_player.buildings:
                                        current_player.buildings[chosen_color] = []
                                        
                                    has_house = any(b.name == 'House' for b in current_player.buildings[chosen_color])
                                    if played_card.name == 'Hotel' and not has_house:
                                        print("❌ You must have a House on a set before adding a Hotel! Card returned.")
                                        current_player.hand.append(played_card)
                                        time.sleep(2)
                                        continue
                                        
                                    current_player.buildings[chosen_color].append(played_card)
                                    print(f"Added {played_card.name} to your {chosen_color} set!")
                                    actions_left -= 1
                                else:
                                    print("Invalid choice. Card returned.")
                                    current_player.hand.append(played_card)
                            except ValueError:
                                print("Invalid input. Card returned.")
                                current_player.hand.append(played_card)
                        time.sleep(1.5)
                        
                    elif played_card.card_type == 'Action':
                        if played_card.name == "Just Say No!":
                            print("\nYou can only play 'Just Say No!' when someone targets you! Card returned.")
                            current_player.hand.append(played_card)
                            time.sleep(2)
                            continue
                        if played_card.name == "Double The Rent!":
                            print("\nYou can only play 'Double The Rent!' ALONG with a Rent card! Card returned.")
                            current_player.hand.append(played_card)
                            time.sleep(2)
                            continue
                            
                        print("\n1. Play for Action\n2. Bank as Money")
                        if input("Choice: ") == '2':
                            current_player.bank.append(played_card)
                            print("Banked for money!")
                            actions_left -= 1
                        else:
                            print(f"\n>>> ACTION TRIGGERED: {played_card.name}! <<<")
                            discard_pile.append(played_card) # Add played action to discard pile
                            
                            if played_card.name.startswith("Rent"):
                                if "Any Color" in played_card.name:
                                    avail_colors = list(set([p.color for p in current_player.properties if p.color]))
                                    targets_all = False
                                else:
                                    color_str = played_card.name.replace("Rent (", "").replace(")", "")
                                    avail_colors = color_str.split("/")
                                    targets_all = True
                                    
                                owned_colors = [c for c in avail_colors if any(p.color == c for p in current_player.properties)]
                                
                                if not owned_colors:
                                    print(f"❌ You don't own any properties in {', '.join(avail_colors)} to charge rent!")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(2)
                                    continue
                                    
                                print("\nSelect which color to charge rent for:")
                                for idx, c in enumerate(owned_colors):
                                    print(f"[{idx + 1}] {c}")
                                col_choice = int(input("Choice: ")) - 1
                                
                                if 0 <= col_choice < len(owned_colors):
                                    chosen_color = owned_colors[col_choice]
                                    
                                    props_of_color = [p for p in current_player.properties if p.color == chosen_color]
                                    rent_amount = sum(p.value for p in props_of_color)
                                    for b in current_player.buildings.get(chosen_color, []):
                                        rent_amount += b.value
                                    
                                    dtr_idx = -1
                                    for i, c in enumerate(current_player.hand):
                                        if c.name == "Double The Rent!":
                                            dtr_idx = i
                                            break
                                            
                                    if dtr_idx != -1:
                                        if actions_left > 1:
                                            print(f"\n🤑 You have a 'Double The Rent!' card in your hand!")
                                            use_dtr = input("Do you want to use it? (y/n): ").lower()
                                            if use_dtr == 'y':
                                                discarded_dtr = current_player.hand.pop(dtr_idx)
                                                discard_pile.append(discarded_dtr)
                                                print(f"💥 You played {discarded_dtr.name}! Rent is DOUBLED!")
                                                rent_amount *= 2
                                                actions_left -= 1
                                        else:
                                            print("\n(You have a Double The Rent card, but not enough Actions left to use it!)")
                                            
                                    print(f"\n💰 Rent charged for {chosen_color}: {rent_amount}M!")
                                    
                                    if targets_all:
                                        for p in players:
                                            if p != current_player:
                                                if not run_jsn_battle(current_player, p, played_card.name, discard_pile):
                                                    p.pay_to(rent_amount, current_player)
                                    else:
                                        print("This Rent card targets ONE opponent. Choose target:")
                                        targets = [p for p in players if p != current_player]
                                        for idx, t in enumerate(targets):
                                            print(f"[{idx + 1}] {t.name}")
                                        t_choice = int(input("Choice: ")) - 1
                                        if 0 <= t_choice < len(targets):
                                            target = targets[t_choice]
                                            if not run_jsn_battle(current_player, target, played_card.name, discard_pile):
                                                target.pay_to(rent_amount, current_player)
                                        else:
                                            print("Invalid target, they escaped paying!")
                                            time.sleep(1.5)
                                            
                                    actions_left -= 1
                                else:
                                    print("Invalid color choice. Card returned to hand.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(1.5)
                                    continue

                            elif played_card.name == "Sly Deal":
                                targets = [p for p in players if p != current_player and p.properties]
                                if not targets:
                                    print("❌ No opponents have properties to steal! Card returned to hand.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(2)
                                    continue
                                
                                print("\nSelect an opponent to steal from:")
                                for idx, t in enumerate(targets):
                                    print(f"[{idx + 1}] {t.name}")
                                try:
                                    t_choice = int(input("Choice: ")) - 1
                                    target = targets[t_choice]
                                    
                                    # Use the new tradable logic!
                                    stealable = target.get_tradable_properties()
                                    
                                    if not stealable:
                                        print(f"❌ All of {target.name}'s properties are in completed sets. Card returned.")
                                        discard_pile.remove(played_card)
                                        current_player.hand.append(played_card)
                                        time.sleep(2)
                                        continue
                                        
                                    print(f"\nSelect a property to steal from {target.name}:")
                                    for idx, p in enumerate(stealable):
                                        print(f"[{idx + 1}] {p.name} ({p.color})")
                                    p_choice = int(input("Choice: ")) - 1
                                    stolen_prop = stealable[p_choice] # test index
                                    
                                    if not run_jsn_battle(current_player, target, played_card.name, discard_pile):
                                        target.properties.remove(stolen_prop)
                                        current_player.properties.append(stolen_prop)
                                        target.validate_buildings()
                                        print(f"🎭 You stole {stolen_prop.name}!")
                                    actions_left -= 1
                                except (ValueError, IndexError):
                                    print("Invalid choice. Card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)

                            elif played_card.name == "Forced Deal":
                                my_tradable = current_player.get_tradable_properties()
                                if not my_tradable:
                                    print("❌ You have no incomplete properties to trade! Card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(2)
                                    continue
                                    
                                targets = [p for p in players if p != current_player and p.properties]
                                if not targets:
                                    print("❌ No opponents have properties to trade! Card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(2)
                                    continue
                                
                                print("\nSelect an opponent to trade with:")
                                for idx, t in enumerate(targets):
                                    print(f"[{idx + 1}] {t.name}")
                                try:
                                    t_choice = int(input("Choice: ")) - 1
                                    target = targets[t_choice]
                                    
                                    their_tradable = target.get_tradable_properties()
                                    
                                    if not their_tradable:
                                        print(f"❌ All of {target.name}'s properties are in completed sets. Card returned.")
                                        discard_pile.remove(played_card)
                                        current_player.hand.append(played_card)
                                        time.sleep(2)
                                        continue
                                        
                                    print(f"\nSelect ONE of YOUR properties to give away:")
                                    for idx, p in enumerate(my_tradable):
                                        print(f"[{idx + 1}] {p.name} ({p.color})")
                                    my_p_choice = int(input("Choice: ")) - 1
                                    my_prop = my_tradable[my_p_choice]
                                    
                                    print(f"\nSelect ONE property to TAKE from {target.name}:")
                                    for idx, p in enumerate(their_tradable):
                                        print(f"[{idx + 1}] {p.name} ({p.color})")
                                    their_p_choice = int(input("Choice: ")) - 1
                                    their_prop = their_tradable[their_p_choice]
                                    
                                    if not run_jsn_battle(current_player, target, played_card.name, discard_pile):
                                        current_player.properties.remove(my_prop)
                                        target.properties.remove(their_prop)
                                        current_player.properties.append(their_prop)
                                        target.properties.append(my_prop)
                                        
                                        current_player.validate_buildings()
                                        target.validate_buildings()
                                        
                                        print(f"🔄 Swapped {my_prop.name} for {their_prop.name}!")
                                    actions_left -= 1
                                except (ValueError, IndexError):
                                    print("Invalid choice. Card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)

                            elif played_card.name == "Pass Go":
                                current_player.draw(deck, discard_pile, 2)
                                actions_left -= 1
                                
                            elif played_card.name == "Deal Breaker":
                                targets_with_sets = [p for p in players if p != current_player and p.get_completed_sets()]
                                
                                if not targets_with_sets:
                                    print("❌ No opponents have a complete set! You cannot play this card right now.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(2)
                                    continue
                                    
                                print("\nSelect an opponent to steal a full set from:")
                                for idx, t in enumerate(targets_with_sets):
                                    unique_sets = list(set(t.get_completed_sets()))
                                    print(f"[{idx + 1}] {t.name} (Sets available: {', '.join(unique_sets)})")
                                    
                                try:
                                    t_choice = int(input("Choice: ")) - 1
                                    if 0 <= t_choice < len(targets_with_sets):
                                        target = targets_with_sets[t_choice]
                                        avail_sets = list(set(target.get_completed_sets()))
                                        
                                        print(f"\nWhich set do you want to steal from {target.name}?")
                                        for idx, c in enumerate(avail_sets):
                                            print(f"[{idx + 1}] {c}")
                                        s_choice = int(input("Choice: ")) - 1
                                        
                                        if 0 <= s_choice < len(avail_sets):
                                            chosen_color = avail_sets[s_choice]
                                            
                                            if not run_jsn_battle(current_player, target, played_card.name, discard_pile):
                                                req = SET_SIZES[chosen_color]
                                                
                                                # Take EXACTLY the number required for a set (leaves extras behind)
                                                cards_to_move = [c for c in target.properties if c.color == chosen_color][:req]
                                                for c in cards_to_move:
                                                    target.properties.remove(c)
                                                    current_player.properties.append(c)
                                                    
                                                buildings_to_move = target.buildings.get(chosen_color, [])
                                                if chosen_color not in current_player.buildings:
                                                    current_player.buildings[chosen_color] = []
                                                current_player.buildings[chosen_color].extend(buildings_to_move)
                                                target.buildings[chosen_color] = []
                                                    
                                                print(f"\n🚨 BOOM! You stole {target.name}'s {chosen_color} set!")
                                                time.sleep(2)
                                            
                                            actions_left -= 1
                                        else:
                                            print("Invalid set choice. Card returned.")
                                            discard_pile.remove(played_card)
                                            current_player.hand.append(played_card)
                                            time.sleep(1.5)
                                    else:
                                        print("Invalid player choice. Card returned.")
                                        discard_pile.remove(played_card)
                                        current_player.hand.append(played_card)
                                        time.sleep(1.5)
                                except ValueError:
                                    print("Invalid choice. Card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(1.5)
                                    
                            elif played_card.name == "Debt Collector":
                                targets = [p for p in players if p != current_player]
                                print("\nSelect an opponent to collect 5M from:")
                                for idx, t in enumerate(targets):
                                    print(f"[{idx + 1}] {t.name}")
                                try:
                                    t_choice = int(input("Choice: ")) - 1
                                    if 0 <= t_choice < len(targets):
                                        target = targets[t_choice]
                                        if not run_jsn_battle(current_player, target, played_card.name, discard_pile):
                                            target.pay_to(5, current_player)
                                        actions_left -= 1
                                    else:
                                        print("Invalid choice, card returned.")
                                        discard_pile.remove(played_card)
                                        current_player.hand.append(played_card)
                                        time.sleep(1.5)
                                except ValueError:
                                    print("Invalid choice, card returned.")
                                    discard_pile.remove(played_card)
                                    current_player.hand.append(played_card)
                                    time.sleep(1.5)
                                    
                            elif played_card.name == "It's My Birthday":
                                print("\nEveryone owes you 2M for your birthday!")
                                time.sleep(1.5)
                                for p in players:
                                    if p != current_player:
                                        if not run_jsn_battle(current_player, p, played_card.name, discard_pile):
                                            p.pay_to(2, current_player)
                                actions_left -= 1
                                        
                    if current_player.check_win():
                        clear_screen()
                        print(f"\n🎉🏆 {current_player.name.upper()} HAS COLLECTED 3 FULL SETS AND WINS THE GAME! 🏆🎉")
                        current_player.show_board()
                        game_over = True
                        break
                else:
                    print("Invalid choice.")
                    time.sleep(1)
            except ValueError:
                print("Enter a valid number.")
                time.sleep(1)
                
        while not game_over and len(current_player.hand) > 7:
            clear_screen()
            print(f"\n⚠️ {current_player.name}, you have {len(current_player.hand)} cards! (Max 7 allowed)")
            print(f"You must select a card to discard.")
            current_player.show_hand()
            
            try:
                choice = int(input("Select a card to discard (1-99): "))
                if 1 <= choice <= len(current_player.hand):
                    discarded_card = current_player.hand.pop(choice - 1)
                    discard_pile.append(discarded_card) # Add to discard pile!
                    print(f"🗑️ Discarded: {discarded_card.name}")
                    time.sleep(1.5)
                else:
                    print("Invalid choice. Try again.")
                    time.sleep(1)
            except ValueError:
                print("Please enter a valid number.")
                time.sleep(1)

        if not game_over:
            input(f"\nEnd of {current_player.name}'s turn. Press ENTER to continue...")
        turn += 1

if __name__ == "__main__":
    play_game()