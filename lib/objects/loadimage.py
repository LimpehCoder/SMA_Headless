import os
import pygame

IMAGE_CACHE = {}  # Cache to store loaded and scaled images
def load_image(name, size=(32, 32)):
    path = os.path.join("..", "images", name)  # Resolve relative path to image

    if (name, size) in IMAGE_CACHE:
        return IMAGE_CACHE[(name, size)]  # Return cached version if already loaded

    if pygame.display.get_surface() is None:
        raise RuntimeError(f"Cannot load '{name}' before display is initialized.")  # Prevent loading before display

    raw_image = pygame.image.load(path).convert_alpha()  # Load image and preserve alpha channel
    scaled = pygame.transform.scale(raw_image, size)  # Resize image to desired size
    IMAGE_CACHE[(name, size)] = scaled  # Store scaled image in cache
    return scaled  # Return image