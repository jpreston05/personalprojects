import random
import numpy as np

player_board = [["☐" for _ in range(10)] for _ in range(10)]
cpu_board = [["☐" for _ in range(10)] for _ in range(10)]
letters_to_nums = {"A":1, "B":2, "C":3, "D":4, "E":5, "F":6, "G":7, "H":8, "I":9, "J":10}
nums_to_letters = {value:key for key, value in letters_to_nums.items()}

player_ships_sunk = 0
cpu_ships_sunk = 0
hit_or_miss = ""

cpu_ships = []
player_ships = []
temp_ships = []
ship_lengths = [5, 4, 3, 3, 2]

cpu_hits = []
cpu_misses = []
cpu_sunk_ships = []

def print_board(board, board_name):
    print(f"\n{board_name} ship board:")
    print("  1 2 3 4 5 6 7 8 9 10")
    for i in range(10):
        print(nums_to_letters.get(i+1), end=' ')
        for j in range(10):
            print(board[i][j], end=" ")
        print('\n', end='')

def print_result():
    print("\n"+("~" * 10))
    print(f"{hit_or_miss}!")
    print("~" * 10)

def wait_for_input():
    input("\nPress enter to continue...")
    print("")

def player_move():
    while True:
        try:
            move = input("Make a Move! (eg: A,1): ").strip()
            row, col = move.split(",")
            col = int(col)
            row = letters_to_nums.get(row.upper())

            if row is None:
                raise ValueError("Invalid row. Use letters A-J.")
            if col < 1 or col > 10:
                raise ValueError("Invalid column. Use numbers 1-10.")

            if cpu_board[row-1][col-1] == "☐":
                is_hit = check_hit("player", (row-1,col-1), cpu_ships)
                cpu_board[row-1][col-1] = "\033[31mX\033[0m" if is_hit else "0"
                break
            else:
                print("You already guessed here!")

        except ValueError as ve:
            print(f"Invalid move: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def generate_possible_board():
    global temp_ships
    temp_ships = []
    if (cpu_hits):
        hit_ship_created = False
        while not hit_ship_created:
            first_hit = cpu_hits[0]
            if len(cpu_hits) > 1:
                second_hit = cpu_hits[1]
                if first_hit[0] == second_hit[0]:
                    ship_direction = 4 if second_hit[1] > first_hit[1] else 3
                else:
                    ship_direction = 2 if second_hit[0] > first_hit[0] else 1
            else:
                ship_direction = random.randint(1,4)

            hit_ship_length = random.choice(get_unsunk_ships_lengths(player_ships))
            
            ship_coords = create_ship(first_hit, ship_direction, hit_ship_length)

            if valid_ship(ship_coords, temp_ships) and not any(coord in cpu_misses for coord in ship_coords) and not any(coord in cpu_sunk_ships for coord in ship_coords) :
                temp_ships.append(ship_coords)
                hit_ship_created = True
        for ship_length in ship_lengths:
            if not hit_ship_length:
                ship_created = False
                while not ship_created:
                    ship_start = (random.randint(0,9), random.randint(0,9))
                    ship_direction = random.randint(1,4)

                    ship_coords = create_ship(ship_start, ship_direction, ship_length)

                    if valid_ship(ship_coords, temp_ships) and not any(coord in cpu_misses for coord in ship_coords) and not any(coord in cpu_sunk_ships for coord in ship_coords):
                        temp_ships.append(ship_coords)
                        ship_created = True
        # all_hits_covered = False
        # while not all_hits_covered:
        #     for ship_length in ship_lengths:
        #         ship_created = False
        #         while not ship_created:
        #             ship_start = (random.randint(0,9), random.randint(0,9))
        #             ship_direction = random.randint(1,4)

        #             ship_coords = create_ship(ship_start, ship_direction, ship_length)

        #             if valid_ship(ship_coords, temp_ships) and not any(coord in cpu_misses for coord in ship_coords) and not any(coord in cpu_sunk_ships for coord in ship_coords) :
        #                 temp_ships.append(ship_coords)
        #                 ship_created = True
        #     if not any(coord in cpu_hits for coord in ship_coords):
        #         temp_ships = []
        #     else:
        #         all_hits_covered = True
    else:
        for ship_length in ship_lengths:
            ship_created = False
            while not ship_created:
                ship_start = (random.randint(0,9), random.randint(0,9))
                ship_direction = random.randint(1,4)

                ship_coords = create_ship(ship_start, ship_direction, ship_length)

                if valid_ship(ship_coords, temp_ships) and not any(coord in cpu_misses for coord in ship_coords) and not any(coord in cpu_sunk_ships for coord in ship_coords):
                    temp_ships.append(ship_coords)
                    ship_created = True


def cpu_move():
    print("Calculating CPU move...")
    heatmap = np.zeros((10,10))
    number_of_runs = 10000
    progress_bar(0, number_of_runs)
    for current_run in range(number_of_runs):
        generate_possible_board()
        cpu_test_shot = (random.randint(0,9), random.randint(0,9))

        while cpu_test_shot in cpu_misses or cpu_test_shot in cpu_hits:
            cpu_test_shot = (random.randint(0,9), random.randint(0,9))
            
        for ship in temp_ships:
            if cpu_test_shot in ship:
                heatmap[cpu_test_shot] += 1
        if current_run % 100 == 0:
            progress_bar(current_run, number_of_runs)
    progress_bar(number_of_runs, number_of_runs)
    print("")

    row, col = np.unravel_index(np.argmax(heatmap, axis=None), heatmap.shape)
    print(f"\nCPU shoots at: {nums_to_letters[row+1]},{col+1}")
    is_hit = check_hit("cpu", (row, col), player_ships)
    if is_hit:
        player_board[row][col] = "\033[31mX\033[0m"
        cpu_hits.append((row,col))
    else:
        player_board[row][col] = "0"
        cpu_misses.append((row,col))

def update_hits():
    for hit in cpu_hits:
        if hit not in player_ships:
            cpu_sunk_ships.append(hit)
            cpu_hits.remove(hit)

def create_ship(ship_start, ship_direction, ship_length):
    row, col = ship_start

    if ship_direction == 1:
        return [(row - i, col) for i in range(ship_length)]
    elif ship_direction == 2: 
        return [(row + i, col) for i in range(ship_length)]
    elif ship_direction == 3:
        return [(row, col - i) for i in range(ship_length)]
    elif ship_direction == 4:
        return [(row, col + i) for i in range(ship_length)]

def valid_ship(ship_coords, ships):

    for row, col in ship_coords:
        if row < 0 or row >= 10 or col < 0 or col >= 10:
            return False
        for ship in ships:
            if (row, col) in ship:
                return False
    
    return True

def check_hit(player_type, move, ships):
    global player_ships_sunk, cpu_ships_sunk, hit_or_miss
    hit_or_miss = "MISS"
    for ship in ships:
        if move in ship:
            hit_or_miss = "HIT"
            ship.remove(move)
            if not ship:
                if player_type == "player":
                    cpu_ships_sunk+=1
                    print(f"You sunk a ship! {cpu_ships_sunk}/5 ships sunk.")
                else:
                    player_ships_sunk+=1
                    print(f"CPU sunk a ship! {player_ships_sunk}/5 ships sunk.")
                    update_hits()
            return True
    return False

def check_player_ships(ship_name, ship_length):
    ship_created = False
    while not ship_created:
        try:
            ship_start = input(f"\nShip: {ship_name}\nLength: {ship_length}\nEnter Starting Coordinate: ")
            if not ship_start:
                raise ValueError("Input cannot be empty.")

            row, col = ship_start.split(",")
            col = int(col)-1
            row = letters_to_nums.get(row.upper())-1

            if row is None or not (0 <= col <=9):
                raise ValueError("Invalid coordinates.")

            ship_direction = int(input("Enter ship direction (1 = Up, 2 = Down, 3 = Left, 4 = Right): "))

            if ship_direction not in [1, 2, 3, 4]:
                raise ValueError("Invalid direction. Choose 1-4.")

            ship_coords = create_ship((row, col), ship_direction, ship_length)

            if valid_ship(ship_coords, player_ships):
                player_ships.append(ship_coords)
                for coord in ship_coords:
                    row, col = coord
                    player_board[row][col] = "X"
                ship_created = True
            else:
                print("\nThat is not a valid ship placement, try again.")

        except ValueError as ve:
            print(f"Invalid input: {ve}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def get_unsunk_ships_lengths(ships):
    unsunk_ships_lengths = [len(ship) for ship in ships if ship]
    return unsunk_ships_lengths

def progress_bar(progress, total):
    percentage = 100 * (progress/float(total))
    bar = "█" * int(percentage) + "-" * (100 - int(percentage))
    print(f"\r|{bar}| {percentage:.2f}%", end="\r")

for ship_length in ship_lengths:
    ship_created = False
    while not ship_created:
        ship_start = (random.randint(0,9), random.randint(0,9))
        ship_direction = random.randint(1,4)

        ship_coords = create_ship(ship_start, ship_direction, ship_length)

        if valid_ship(ship_coords, cpu_ships):
            cpu_ships.append(ship_coords)
            ship_created = True


#for i, ship in enumerate(cpu_ships, start=1):
#   print(f"Ship {i}: {ship}")

print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|\033[34m Monte Carlo \033[0m|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
print("██████╗░░█████╗░████████╗████████╗██╗░░░░░███████╗░██████╗██╗░░██╗██╗██████╗░░██████╗")
print("██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██║░░░░░██╔════╝██╔════╝██║░░██║██║██╔══██╗██╔════╝")
print("██████╦╝███████║░░░██║░░░░░░██║░░░██║░░░░░█████╗░░╚█████╗░███████║██║██████╔╝╚█████╗░")
print("██╔══██╗██╔══██║░░░██║░░░░░░██║░░░██║░░░░░██╔══╝░░░╚═══██╗██╔══██║██║██╔═══╝░░╚═══██╗")
print("██████╦╝██║░░██║░░░██║░░░░░░██║░░░███████╗███████╗██████╔╝██║░░██║██║██║░░░░░██████╔╝")
print("╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░╚═╝░░░╚══════╝╚══════╝╚═════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═════╝░")
print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|\033[34m Jack Preston \033[0m|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
input("\033[33mPress enter to begin...\033[0m")

print("PLACE YOUR SHIPS:")
print_board(player_board, "PLAYER")
check_player_ships("Carrier", 5)
print_board(player_board, "PLAYER")
check_player_ships("Battleship", 4)
print_board(player_board, "PLAYER")
check_player_ships("Cruiser", 3)
print_board(player_board, "PLAYER")
check_player_ships("Submarine", 3)
print_board(player_board, "PLAYER")
check_player_ships("Destroyer", 2)
print_board(player_board, "PLAYER")

game_over = False
while not game_over:
    print_board(cpu_board, "CPU")
    player_move()
    print_board(cpu_board, "CPU")
    print_result()
    if cpu_ships_sunk == 5:
        game_over = True
        print("You Win!")
    wait_for_input()
    cpu_move()
    print_board(player_board, "PLAYER")
    print_result()
    if player_ships_sunk == 5:
        game_over = True
        print("You Lose!")
    wait_for_input()