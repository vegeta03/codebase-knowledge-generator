import keyboard
import os
import sys
import threading
import signal
import logging

# Configure logging
logger = logging.getLogger("keyboard_handler")

def setup_exit_handler():
    """
    Sets up a keyboard listener that terminates the process when ESC is pressed.
    This runs in a separate thread to avoid blocking the main execution flow.
    """
    def on_esc_press(e):
        if e.name == 'esc':
            logger.info("ESC key pressed - terminating process")
            print("\n🛑 ESC key pressed. Terminating process...")
            
            # Use os.kill to send SIGTERM to the current process
            # This is more reliable than sys.exit() as it will terminate all threads
            os.kill(os.getpid(), signal.SIGTERM)
    
    def start_keyboard_listener():
        # Register the ESC key handler
        keyboard.on_press(on_esc_press)
        
        # This keeps the listener active without blocking the main thread
        # It will automatically terminate when the main process ends
        keyboard.wait()
    
    # Create and start the keyboard listener thread
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    logger.info("Keyboard handler initialized. Press ESC at any time to terminate the process.")
    print("ℹ️ Press ESC at any time to terminate the process.")
    
    return keyboard_thread

if __name__ == "__main__":
    # For testing the keyboard handler
    logging.basicConfig(level=logging.INFO)
    print("Testing keyboard handler. Press ESC to exit.")
    setup_exit_handler()
    
    # Simulate a running process
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Process terminated by CTRL+C")
