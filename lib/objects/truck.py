from pygame.math import Vector2
from loadimage import load_image  # Custom utility for loading and scaling images
from pygame.math import Vector2
from box import BoxPile  # Import BoxPile class for box management

class Truck:
    def __init__(self, sorting_area, start_y=220, cycle_name=None):
        self.sorting_area = sorting_area  # Reference to SortingAreaScene
        self.cycle = cycle_name  # Delivery cycle

        # Positioning
        self.target_position = Vector2(-150 + 96 * 3, start_y)  # Where truck stops to unload
        self.position = Vector2(-150, self.target_position.y)  # Start offscreen left
        self.exit_position = Vector2(-150, self.target_position.y)  # Despawn path

        self.speed = 120
        self.image = load_image("truck.png", (96, 48))

        # State flags
        self.arrived = False
        self.departing = False
        self.despawned = False
        self.boxes_to_deliver = 0
        self.unloaded = False

        if self.cycle:
            self.boxes_to_deliver = 20 if self.cycle == "ACycle" else 30 if self.cycle == "BCycle" else 40

    def update(self, dt):
        if not self.arrived:
            direction = self.target_position - self.position
            if direction.length() > 1:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)
            else:
                self.arrived = True
                self.spawn_boxpile()  # ✅ Spawn boxes and trigger reverse

        elif self.departing:
            direction = self.exit_position - self.position
            if direction.length() > 1:
                direction.normalize_ip()
                self.position += direction * self.speed * (dt / 1000.0)
            else:
                self.despawned = True

    def spawn_boxpile(self):
        if not self.unloaded:
            pile_position = Vector2(self.target_position.x + 40, self.target_position.y - 20)

            if not self.sorting_area.box_pile:
                self.sorting_area.box_pile = BoxPile(position=pile_position)
            else:
                self.sorting_area.box_pile.position = pile_position

            self.sorting_area.box_pile.increment(self.boxes_to_deliver)
            self.unloaded = True
            self.departing = True  # ✅ Begin reversing immediately
            print(f"[Truck] Unloaded {self.boxes_to_deliver} boxes and is departing from {pile_position}")

    def render(self, screen):
        screen.blit(self.image, self.position)
        if self.arrived and not self.departing:
            box_img = load_image("box.png")
            screen.blit(box_img, (self.position.x + 40, self.position.y - 20))

    def is_ready_to_unload(self):
        return self.arrived and not self.unloaded

    def is_ready_to_despawn(self):
        return self.despawned