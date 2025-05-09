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
    Sets up a keyboard listener that terminates the process when Ctrl+Q is pressed.
    This runs in a separate thread to avoid blocking the main execution flow.
    """
    def on_exit_key():
        logger.info("Ctrl+Q pressed - terminating process")
        print("\n🛑 Ctrl+Q pressed. Terminating process...")
        
        # Use os.kill to send SIGTERM to the current process
        # This is more reliable than sys.exit() as it will terminate all threads
        os.kill(os.getpid(), signal.SIGTERM)
    
    def start_keyboard_listener():
        # Register the Ctrl+Q key handler
        keyboard.add_hotkey('ctrl+q', on_exit_key)
        
        # This keeps the listener active without blocking the main thread
        # It will automatically terminate when the main process ends
        keyboard.wait()
    
    # Create and start the keyboard listener thread
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    logger.info("Keyboard handler initialized. Press Ctrl+Q at any time to terminate the process.")
    print("ℹ️ Press Ctrl+Q at any time to terminate the process.")
    
    return keyboard_thread

if __name__ == "__main__":
    # For testing the keyboard handler
    logging.basicConfig(level=logging.INFO)
    print("Testing keyboard handler. Press Ctrl+Q to exit.")
    setup_exit_handler()
    
    # Simulate a running process
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Process terminated by CTRL+C")
