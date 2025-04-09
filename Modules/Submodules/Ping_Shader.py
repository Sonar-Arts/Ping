import pygame
import time
import numpy as np # Use 'np' convention
import atexit
import logging

# --- Configuration ---
# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Track if numpy/surfarray is available (essential for this version)
_has_numpy = False
try:
    # Test basic numpy and surfarray functionality
    _test_surf = pygame.Surface((1, 1))
    _test_arr = pygame.surfarray.pixels3d(_test_surf)
    _has_numpy = True
    del _test_surf, _test_arr
except (ImportError, AttributeError, pygame.error) as e:
    logging.error(f"Critical Error: numpy and/or pygame.surfarray not functional: {e}")
    # This shader heavily relies on numpy, so we might want to raise an error
    # or provide a clear message that it won't work.
    # For now, we'll let it proceed but it will likely fail later.

# --- Performance Monitoring ---
_shader_stats = {
    'processed_count': 0,
    'total_process_time': 0.0,
    'peak_process_time': 0.0,
    'last_apply_time': 0.0, # Time for the whole apply_to_surface call
    'errors': 0
}

def get_shader_stats():
    """Get current shader performance statistics."""
    stats = _shader_stats
    if stats['processed_count'] > 0:
        avg_time = stats['total_process_time'] / stats['processed_count']
        return {
            'processed': stats['processed_count'],
            'avg_process_time_ms': avg_time * 1000,
            'peak_process_time_ms': stats['peak_process_time'] * 1000,
            'last_apply_time_ms': stats['last_apply_time'] * 1000,
            'errors': stats['errors']
        }
    return None

def reset_shader_stats():
    """Reset performance counters."""
    global _shader_stats
    _shader_stats = {k: 0.0 if isinstance(v, float) else 0 for k, v in _shader_stats.items()}
    logging.info("Shader stats reset.")

# Register reset at exit (optional, good for long sessions)
atexit.register(reset_shader_stats)


# --- Pixel Shader Class ---
class PixelShader:
    """
    Applies a pixel art style effect to Pygame surfaces using numpy for optimization.
    Includes pixelation, optional edge glow, contrast, and sharpness adjustments.
    """

    def __init__(self, pixel_size=3, edge_threshold=0.4, glow_strength=1.2,
                 contrast_factor=1.2, sharpness=1.0, enable_edges=True):
        """
        Initialize the shader.

        Args:
            pixel_size (int): The side length of the square pixel blocks.
            edge_threshold (float): Sensitivity for edge detection (0.0 to 1.0).
            glow_strength (float): Intensity multiplier for edge glow (>= 1.0).
            contrast_factor (float): Factor to adjust color contrast (>= 0.0).
            sharpness (float): Factor to adjust color sharpness (>= 0.0).
            enable_edges (bool): Whether to apply edge detection and glow.
        """
        if not _has_numpy:
            # Log error and disable shader if numpy isn't working
            logging.error("PixelShader disabled: numpy/surfarray unavailable or failed initialization.")
            self._enabled = False
            return
        self._enabled = True

        # Configuration
        self.pixel_size = max(1, int(pixel_size))
        self.edge_threshold = np.clip(edge_threshold, 0.0, 1.0)
        self.glow_strength = max(1.0, glow_strength)
        self.contrast_factor = max(0.0, contrast_factor)
        self.sharpness = max(0.0, sharpness)
        self.enable_edges = enable_edges

        # Internal state
        self._cached_result_surface = None
        self._cached_surface_size = (0, 0)
        self._contrast_table = None
        self._sharpness_table = None
        self._needs_table_update = True # Flag to rebuild tables

        # Initialize color tables
        self._update_color_tables()

        logging.info(f"PixelShader initialized (numpy enabled: {_has_numpy})")

    def configure(self, **kwargs):
        """
        Update shader parameters dynamically.

        Args:
            pixel_size (int): Size of pixel blocks.
            edge_threshold (float): Edge detection sensitivity.
            glow_strength (float): Edge glow intensity.
            contrast_factor (float): Color contrast.
            sharpness (float): Edge sharpness.
            enable_edges (bool): Enable/disable edge effect.
        """
        if not self._enabled:
            return

        color_params_changed = False
        for key, value in kwargs.items():
            if hasattr(self, key):
                old_value = getattr(self, key)
                # Apply constraints/validation
                if key == 'pixel_size': value = max(1, int(value))
                elif key == 'edge_threshold': value = np.clip(value, 0.0, 1.0)
                elif key == 'glow_strength': value = max(1.0, value)
                elif key in ('contrast_factor', 'sharpness'): value = max(0.0, value)
                elif key == 'enable_edges': value = bool(value)

                setattr(self, key, value)
                if key in ('contrast_factor', 'sharpness') and old_value != value:
                    color_params_changed = True

        if color_params_changed:
            self._needs_table_update = True
            # No need to call _update_color_tables here, apply_to_surface will do it.
            logging.debug("Shader color parameters changed, tables will update on next apply.")

    def _update_color_tables(self):
        """Initialize or update lookup tables for color enhancement using numpy."""
        if not self._enabled or not self._needs_table_update:
            return

        try:
            indices = np.arange(256, dtype=np.float32)
            mid = 128.0

            # Contrast Table
            contrast = mid + (indices - mid) * self.contrast_factor
            self._contrast_table = np.clip(contrast, 0, 255).astype(np.uint8)

            # Sharpness Table (simplified approach)
            # Apply sharpness relative to the contrast-adjusted mid-point idea
            # This version enhances deviation from the mean
            sharp_indices = self._contrast_table.astype(np.float32) # Apply sharpness after contrast
            deviation = sharp_indices - mid
            sharpness_adj = mid + deviation * self.sharpness
            self._sharpness_table = np.clip(sharpness_adj, 0, 255).astype(np.uint8)

            self._needs_table_update = False
            logging.debug("Color lookup tables updated.")
            return True
        except Exception as e:
            logging.error(f"Failed to create color tables: {e}")
            _shader_stats['errors'] += 1
            # Use identity tables as fallback
            self._contrast_table = np.arange(256, dtype=np.uint8)
            self._sharpness_table = np.arange(256, dtype=np.uint8)
            self._needs_table_update = False # Avoid repeated errors
            return False

    def _enhance_color_batch(self, colors_rgb):
        """Enhance a batch of RGB colors using lookup tables."""
        if self._contrast_table is None or self._sharpness_table is None:
            logging.warning("Color tables not initialized, skipping enhancement.")
            return colors_rgb # Return original if tables failed

        # Apply contrast then sharpness using the tables
        contrasted = self._contrast_table[colors_rgb]
        sharpened = self._sharpness_table[contrasted]
        return sharpened

    def _init_cache(self, width, height):
        """Initialize or resize the result cache surface."""
        if (not self._cached_result_surface or
                self._cached_surface_size != (width, height)):
            try:
                # Create new cache surface with SRCALPHA for transparency
                self._cached_result_surface = pygame.Surface((width, height), pygame.SRCALPHA)
                self._cached_surface_size = (width, height)
                logging.debug(f"Shader cache resized to {width}x{height}")
            except Exception as e:
                logging.error(f"Failed to create cache surface: {e}")
                _shader_stats['errors'] += 1
                self._cached_result_surface = None
                self._cached_surface_size = (0, 0)
                return False
        return True

    def apply_to_surface(self, surface):
        """
        Apply the pixel art effect to the input surface.

        Args:
            surface (pygame.Surface): The surface to process.

        Returns:
            pygame.Surface: The processed surface (or the original if disabled/error).
        """
        apply_start_time = time.perf_counter()

        if not self._enabled:
            return surface # Return original if shader is disabled

        width, height = surface.get_width(), surface.get_height()

        # Basic checks
        if width < self.pixel_size or height < self.pixel_size:
            logging.warning("Surface too small for pixel size, skipping shader.")
            return surface # Not worth processing

        # Ensure color tables are up-to-date
        if self._needs_table_update:
            self._update_color_tables()

        # Ensure cache is ready
        if not self._init_cache(width, height) or not self._cached_result_surface:
            logging.error("Cache initialization failed, returning original surface.")
            return surface

        process_start_time = time.perf_counter()
        try:
            # --- Get Surface Data ---
            # Work with copies to avoid modifying the original surface directly
            # Using pixels3d for RGB, pixels_alpha for Alpha
            pixels3d = pygame.surfarray.pixels3d(surface).copy() # Shape (W, H, 3)
            alpha = pygame.surfarray.pixels_alpha(surface).copy() # Shape (W, H)

            # Transpose to (H, W, C) and (H, W) for easier block processing
            pixels3d = np.transpose(pixels3d, (1, 0, 2))
            alpha = np.transpose(alpha, (1, 0))

            # --- Prepare Result Arrays ---
            # Initialize result arrays (matching transposed shape)
            result_pixels3d = np.zeros_like(pixels3d)
            result_alpha = np.zeros_like(alpha)

            # --- Block Processing ---
            ps = self.pixel_size
            for y in range(0, height, ps):
                for x in range(0, width, ps):
                    # Define block boundaries, clamping to surface edges
                    y_end = min(y + ps, height)
                    x_end = min(x + ps, width)

                    # Extract block data
                    block_rgb = pixels3d[y:y_end, x:x_end]
                    block_alpha = alpha[y:y_end, x:x_end]

                    # Mask for non-transparent pixels within the block
                    mask = block_alpha > 0

                    if np.any(mask):
                        # Calculate average color ONLY for non-transparent pixels
                        # Reshape mask to allow broadcasting for RGB selection
                        mask_rgb = np.expand_dims(mask, axis=-1) # Shape (bh, bw, 1)
                        
                        # Efficiently calculate sum and count for non-transparent pixels
                        valid_pixels_rgb = block_rgb * mask_rgb # Zero out transparent pixels
                        valid_pixels_alpha = block_alpha * mask # Zero out transparent alphas
                        
                        count = np.sum(mask) # Number of non-transparent pixels
                        
                        avg_rgb = np.sum(valid_pixels_rgb.reshape(-1, 3), axis=0) / count
                        avg_alpha = np.sum(valid_pixels_alpha) / count

                        # Enhance the average color
                        enhanced_rgb = self._enhance_color_batch(avg_rgb.astype(np.uint8).reshape(1, 3))[0]

                        # Fill the block in the result arrays
                        result_pixels3d[y:y_end, x:x_end] = enhanced_rgb
                        result_alpha[y:y_end, x:x_end] = int(avg_alpha)
                    else:
                        # If block is fully transparent, keep it that way
                        result_pixels3d[y:y_end, x:x_end] = 0
                        result_alpha[y:y_end, x:x_end] = 0

            # --- Edge Detection and Glow (Optional) ---
            if self.enable_edges:
                # Calculate luminance (approximation) for edge detection
                # Using result_pixels3d before transposing back
                luminance = (result_pixels3d * np.array([0.299, 0.587, 0.114])).sum(axis=2) / 255.0

                # Simple Sobel-like edge detection (faster than complex neighborhood checks)
                grad_y = np.abs(luminance[:-1, :] - luminance[1:, :])
                grad_x = np.abs(luminance[:, :-1] - luminance[:, 1:])

                # Create edge map - combine gradients, threshold, consider alpha
                edge_map = np.zeros_like(luminance, dtype=bool)
                # Pad gradients to match original size before combining
                edge_map[:-1, :] |= (grad_y > self.edge_threshold)
                edge_map[:, :-1] |= (grad_x > self.edge_threshold)
                
                # Only consider edges where the pixel is not fully transparent
                edge_map &= (result_alpha > 0) 

                # Apply glow: Increase brightness/saturation of edge pixels
                # A simple approach: multiply color by glow_strength, clip
                edge_indices = np.where(edge_map)
                if edge_indices[0].size > 0:
                    edge_colors = result_pixels3d[edge_indices].astype(np.float32)
                    glow_colors = np.clip(edge_colors * self.glow_strength, 0, 255).astype(np.uint8)
                    result_pixels3d[edge_indices] = glow_colors
                    # Optionally slightly increase alpha on edges for emphasis
                    # result_alpha[edge_indices] = np.clip(result_alpha[edge_indices] * 1.1, 0, 255).astype(np.uint8)


            # --- Update Cache Surface ---
            # Transpose back to (W, H, C) and (W, H) for surfarray
            result_pixels3d = np.transpose(result_pixels3d, (1, 0, 2))
            result_alpha = np.transpose(result_alpha, (1, 0))

            # Update the cached surface directly using surfarray views
            target_pixels3d = pygame.surfarray.pixels3d(self._cached_result_surface)
            target_alpha = pygame.surfarray.pixels_alpha(self._cached_result_surface)

            target_pixels3d[...] = result_pixels3d
            target_alpha[...] = result_alpha

            # Release the views (important!)
            del target_pixels3d
            del target_alpha

            process_time = time.perf_counter() - process_start_time

            # Update stats
            _shader_stats['processed_count'] += 1
            _shader_stats['total_process_time'] += process_time
            _shader_stats['peak_process_time'] = max(_shader_stats['peak_process_time'], process_time)

            # Log performance warning if processing takes too long
            if process_time > 0.05: # 50ms threshold
                 logging.warning(f"Shader processing took {process_time*1000:.2f} ms")

            apply_time = time.perf_counter() - apply_start_time
            _shader_stats['last_apply_time'] = apply_time

            return self._cached_result_surface # Return the processed cache

        except Exception as e:
            logging.exception(f"Error applying shader: {e}") # Log full traceback
            _shader_stats['errors'] += 1
            self._enabled = False # Disable shader on critical error to prevent spam
            logging.error("Disabling PixelShader due to error.")
            return surface # Return original surface on error


# --- Global Shader Instance Management ---
_shader_instances = {}

def get_shader(preset='default', **kwargs):
    """
    Get a shared PixelShader instance based on a preset name.
    Creates a new instance if it doesn't exist for the preset.
    Allows overriding parameters for the specific preset on first creation.

    Args:
        preset (str): A name for the shader configuration (e.g., 'default', 'menu_glow').
        **kwargs: Configuration options passed to PixelShader constructor
                  ONLY when the preset instance is first created.

    Returns:
        PixelShader: The shared shader instance for the preset.
    """
    global _shader_instances
    if preset not in _shader_instances:
        logging.info(f"Creating new PixelShader instance for preset '{preset}' with options: {kwargs}")
        _shader_instances[preset] = PixelShader(**kwargs)
    # Note: Subsequent calls with the same preset name ignore kwargs.
    # Use the configure() method on the returned instance to change settings later.
    return _shader_instances[preset]

def cleanup_shaders():
    """Explicitly clear shader instances (optional)."""
    global _shader_instances
    logging.info("Cleaning up shader instances.")
    # Help garbage collection by removing references
    # No explicit shutdown needed for this version as there are no threads.
    _shader_instances.clear()

# Register cleanup at exit
atexit.register(cleanup_shaders)


# --- Example Usage (optional, for testing) ---
if __name__ == '__main__':
    pygame.init()

    # Check if numpy is available early
    if not _has_numpy:
        print("Numpy/Surfarray not available. Shader functionality is disabled.")
        pygame.quit()
        exit()

    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pixel Shader Test")

    # Load a test image or create one
    try:
        test_surface = pygame.image.load('test_image.png').convert_alpha() # Replace with your image
        test_surface = pygame.transform.scale(test_surface, (screen_width // 2, screen_height // 2))
    except pygame.error:
        print("Warning: test_image.png not found. Creating a gradient surface.")
        test_surface = pygame.Surface((screen_width // 2, screen_height // 2), pygame.SRCALPHA)
        for y in range(test_surface.get_height()):
            for x in range(test_surface.get_width()):
                r = int(x / test_surface.get_width() * 255)
                g = int(y / test_surface.get_height() * 255)
                b = int((x+y) / (test_surface.get_width() + test_surface.get_height()) * 255)
                a = 200 + int(x / test_surface.get_width() * 55) # Varying alpha
                test_surface.set_at((x, y), (r, g, b, a))

    # Get the default shader instance
    shader = get_shader('default', pixel_size=5, enable_edges=True, contrast_factor=1.3, sharpness=1.1)
    # Get another shader instance with different settings
    shader_no_edges = get_shader('no_edges', pixel_size=8, enable_edges=False)


    clock = pygame.time.Clock()
    running = True
    show_original = False
    use_no_edge_shader = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_original = not show_original
                if event.key == pygame.K_e:
                    # Toggle edge effect on the default shader
                    current_config = shader.enable_edges
                    shader.configure(enable_edges=not current_config)
                    print(f"Default shader edges: {shader.enable_edges}")
                if event.key == pygame.K_s:
                    use_no_edge_shader = not use_no_edge_shader
                    print(f"Using no-edge shader: {use_no_edge_shader}")
                if event.key == pygame.K_UP:
                    shader.configure(pixel_size=shader.pixel_size + 1)
                    print(f"Pixel size: {shader.pixel_size}")
                if event.key == pygame.K_DOWN:
                    shader.configure(pixel_size=max(1, shader.pixel_size - 1))
                    print(f"Pixel size: {shader.pixel_size}")
                if event.key == pygame.K_r:
                    reset_shader_stats()


        screen.fill((30, 30, 30)) # Dark background

        # Choose which shader to apply
        active_shader = shader_no_edges if use_no_edge_shader else shader

        if show_original:
            processed_surface = test_surface
            title = "Original"
        else:
            processed_surface = active_shader.apply_to_surface(test_surface)
            title = f"Processed (Edges: {active_shader.enable_edges}, Pixel: {active_shader.pixel_size})"
            title += " - NoEdgeShader" if use_no_edge_shader else " - DefaultShader"


        # Display the result centered
        rect = processed_surface.get_rect(center=screen.get_rect().center)
        screen.blit(processed_surface, rect)

        pygame.display.set_caption(f"{title} - SPACE: Toggle Original, E: Toggle Edges, S: Switch Shader, UP/DOWN: Pixel Size, R: Reset Stats")

        pygame.display.flip()
        clock.tick(60) # Limit FPS

        # Print stats occasionally
        if pygame.time.get_ticks() % 5000 < 20: # Print every 5 seconds approx
            stats = get_shader_stats()
            if stats:
                print(f"Stats: {stats}")


    cleanup_shaders()
    pygame.quit()