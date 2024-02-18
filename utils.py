import matplotlib.pyplot as plt


def display_dungeon(dungeon):
    for row in dungeon:
        for cell in row:
            if cell == 1:
                print("#", end="")
            else:
                print(".", end="")
        print()

def plot_dungeon(dungeon):
    plt.imshow(dungeon, cmap='gray')