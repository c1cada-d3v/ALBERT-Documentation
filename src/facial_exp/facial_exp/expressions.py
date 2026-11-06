import os
import time
import pygame
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from ament_index_python.packages import get_package_share_directory

class FacialExpressions(Node):

    def __init__(self):
        super().__init__("expressions")
        pygame.init()
        
        # Screen setup (800x480)
        self.screen_width = 800
        self.screen_height = 480
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
        
        # Load all sprites
        package_share_directory = get_package_share_directory('facial_exp')
        self.sprite_folder_path = os.path.join(package_share_directory, 'sprite_folder')
        
        # Create sprite dictionary
        self.sprite_images = {}
        self.load_sprites()
        
        # Verify base assets exist
        if 0 not in self.sprite_images:
            self.get_logger().error("Critical error: Sprite 0.png failed to load!")
            raise RuntimeError("Base sprite missing, shutting down node.")
            
        # --- PHYSICAL ALIGNMENT FOR VERTICAL ---
        shift_left_axis = -50  
        shift_down_axis = -100  
        
        # Anchor points
        screen_upper_y = 10 + shift_left_axis
        screen_upper_x = 20 + shift_down_axis
        
        screen_lower_y = 10 + shift_left_axis
        screen_lower_x = 0 + shift_down_axis
        
        screen_nose_y = 10 + shift_left_axis
        screen_nose_x = 0 + shift_down_axis
        
        screen_eyebrow_y = 10 + shift_left_axis
        screen_eyebrow_x = 20 + shift_down_axis
        
        self.sprite_upper_pos = (screen_upper_x, screen_upper_y)
        self.sprite_lower_pos = (screen_lower_x, screen_lower_y)
        self.sprite_nose_pos = (screen_nose_x, screen_nose_y)
        self.sprite_eyebrow_pos = (screen_eyebrow_x, screen_eyebrow_y)
            
        # --- FIXED EASTER EGG ALIGNMENT ---
        # Pull the actual surface asset for image 13 to query sizes accurately
        egg_surface = self.sprite_images.get(13, self.sprite_images[0])
        egg_width, egg_height = egg_surface.get_size()
        
        centered_x = screen_nose_x
        centered_y = screen_nose_y
        
        # OPTIONAL OFFSETS (Change these values if sprite 13 needs minor pixel adjustments)
        egg_micro_x_offset = 0
        egg_micro_y_offset = 0
        
        self.centered_pos = (centered_x + egg_micro_x_offset, centered_y + egg_micro_y_offset)
        # ----------------------------------
        
        # Internal state tracking
        self.emot_state = 0
        self.easter_egg = False  
        
        # Subscriber to receive emotion states from other nodes
        self.esp_exp_subscriber = self.create_subscription(
            Int32,
            'face_state_req',
            self.face_state_callback,
            10
        )
        
        # Blinking parameters
        self.blink = True
        self.last_blink_time = time.time()
        self.blink_interval = 2.0
        
        # Frame rate control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # ROS2 timer calls update at 60Hz
        self.timer = self.create_timer(1.0 / self.fps, self.update)
        self.get_logger().info("Expressions running...")

    def face_state_callback(self, msg):
        """Callback to update the emotion state when a message is received."""
        if not self.easter_egg:
            self.emot_state = msg.data

    def load_sprites(self):
        # Scan explicitly for numbers 0 through 13
        for i in range(14):
            path = os.path.join(self.sprite_folder_path, f'{i}.png')
            if not os.path.exists(path):
                self.get_logger().warn(f"PYGAME: Sprite not found: {path}")
                continue
            image = pygame.image.load(path).convert_alpha()
            
            # --- SCALE ADJUSTER ---
            # Current width/height * 1.15
            orig_w, orig_h = image.get_size()
            new_w = int(orig_w * 1.15)
            new_h = int(orig_h * 1.15)
            
            # Apply smooth scaling to keep transparency borders clean
            image = pygame.transform.smoothscale(image, (new_w, new_h))
            # --------------------------------------
            
            # Bind image explicitly to its ID key, skipping gaps smoothly
            self.sprite_images[i] = image 
        self.get_logger().info(f"Loaded {len(self.sprite_images)} sprites scaled to 115%.")

    def update(self):
        # Handle Pygame events exactly once per frame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.get_logger().info("PYGAME: Quit event received!")
                rclpy.shutdown()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.get_logger().info("SPACE pressed!")
                elif event.key == pygame.K_h:
                    self.easter_egg = not self.easter_egg
                    self.get_logger().info(f"Easter egg mode set to: {self.easter_egg}")

        # Reset screen
        self.screen.fill((0, 0, 0))

        # --- EASTER EGG OVERRIDE ---
        if self.easter_egg:
            # Safely fetch key 13, fallback to key 0 if it isn't compiled yet
            egg_sprite = self.sprite_images.get(13, self.sprite_images[0])
            
            # Match the 270-degree rotation of other face elements
            egg_sprite = pygame.transform.rotate(egg_sprite, 270)
            
            # Blit the single full face to the custom aligned position
            self.screen.blit(egg_sprite, self.centered_pos)
            
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        # ---------------------------

        # Toggle blink state on interval
        current_time = time.time()
        if current_time - self.last_blink_time > self.blink_interval:
            self.blink = not self.blink
            self.last_blink_time = current_time

        # Safe dictionary lookups with fallback definitions
        eye_sprite = self.sprite_images.get(0 if self.blink else 1, self.sprite_images[0])
        eyebrow_sprite = self.sprite_images.get(4, self.sprite_images[0])
        mouth_sprite = self.sprite_images.get(5, self.sprite_images[0])
        nose_sprite = self.sprite_images.get(3, self.sprite_images[0])

        # Actual emotional state selection
        if self.emot_state == 1: 
            # Neutral-happy
            eyebrow_sprite = self.sprite_images.get(4, eyebrow_sprite) # Neutral raised eyebrows
            mouth_sprite = self.sprite_images.get(5, mouth_sprite) # Neutral happy resting mouth
            nose_sprite = self.sprite_images.get(13, nose_sprite) # Neutral relaxed nose
        elif self.emot_state == 2:
            # Placeholder for sad
            pass
        elif self.emot_state == 3:
            # Placeholder for angry
            pass
            # ...

        # Rotate all features vertically
        eye_sprite = pygame.transform.rotate(eye_sprite, 270)
        mouth_sprite = pygame.transform.rotate(mouth_sprite, 270)
        nose_sprite = pygame.transform.rotate(nose_sprite, 270)
        eyebrow_sprite = pygame.transform.rotate(eyebrow_sprite, 270)

        # Blit all features
        self.screen.blit(eye_sprite, self.sprite_upper_pos)
        self.screen.blit(mouth_sprite, self.sprite_lower_pos)
        self.screen.blit(nose_sprite, self.sprite_nose_pos)
        self.screen.blit(eyebrow_sprite, self.sprite_eyebrow_pos)
        
        pygame.display.flip()
        self.clock.tick(self.fps)

# --- MAIN ---
def main(args=None):
    rclpy.init(args=args)
    try:
        node = FacialExpressions()
        rclpy.spin(node)
    except RuntimeError as e:
        print(e)
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
