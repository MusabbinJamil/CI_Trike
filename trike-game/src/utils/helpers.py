def load_image(file_path):
    # Function to load an image from the specified file path
    from PIL import Image
    return Image.open(file_path)

def load_sound(file_path):
    # Function to load a sound file from the specified file path
    import pygame
    return pygame.mixer.Sound(file_path)

def save_game_state(state, file_path):
    # Function to save the current game state to a file
    import json
    with open(file_path, 'w') as f:
        json.dump(state, f)

def load_game_state(file_path):
    # Function to load the game state from a file
    import json
    with open(file_path, 'r') as f:
        return json.load(f)

def get_player_input(prompt):
    # Function to get input from the player
    return input(prompt)