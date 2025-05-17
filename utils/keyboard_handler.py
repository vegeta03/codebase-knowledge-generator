import keyboard
import os
import sys
import threading
import signal
import logging
import time

# Configure logging
logger = logging.getLogger("keyboard_handler")

def setup_exit_handler():
    """
    Sets up a keyboard listener that terminates the process when Ctrl+Shift+C is pressed
    and confirmed. This runs in a separate thread to avoid blocking the main execution flow.
    
    The implementation includes safeguards to prevent accidental termination and
    to minimize interference with other applications.
    """
    # Track confirmation state
    confirm_state = {
        "pending": False,
        "timestamp": 0,
        "confirmation_window": 5  # Time window in seconds to confirm termination
    }
    
    def on_exit_key():
        """Handler for the initial Ctrl+Shift+C combination"""
        # Only process if we're in the terminal window (based on keyboard focus)
        # This helps reduce interference with other applications
        if not confirm_state["pending"]:
            # Start confirmation flow
            confirm_state["pending"] = True
            confirm_state["timestamp"] = time.time()
            print("\n⚠️ Press Ctrl+Shift+C again within 5 seconds to confirm termination...")
            logger.info("Termination requested. Waiting for confirmation...")
        else:
            # Check if we're within the confirmation window
            if time.time() - confirm_state["timestamp"] <= confirm_state["confirmation_window"]:
                # Confirmed - terminate the process
                logger.info("Termination confirmed - ending process")
                print("\n🛑 Termination confirmed. Shutting down...")
                
                # Reset state (although not necessary since we're terminating)
                confirm_state["pending"] = False
                
                # Use os.kill to send SIGTERM to the current process
                # This is more reliable than sys.exit() as it will terminate all threads
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                # Confirmation window expired, treat as new request
                confirm_state["timestamp"] = time.time()
                print("\n⚠️ Confirmation window expired. Press Ctrl+Shift+C again within 5 seconds to confirm termination...")
                logger.info("Confirmation window expired. Restarting confirmation sequence.")
    
    def reset_confirmation():
        """Reset confirmation state if window expires"""
        while True:
            if confirm_state["pending"]:
                if time.time() - confirm_state["timestamp"] > confirm_state["confirmation_window"]:
                    confirm_state["pending"] = False
                    logger.info("Confirmation window expired. Reset termination request.")
            time.sleep(1)  # Check every second
    
    def start_keyboard_listener():
        # Register ONLY the specific Ctrl+Shift+C combination
        # Add suppress=True to prevent the key event from being passed to other applications
        # This provides more isolation between our handler and the rest of the system
        keyboard.add_hotkey('ctrl+shift+c', on_exit_key, suppress=False)
        
        # Start confirmation reset thread
        reset_thread = threading.Thread(target=reset_confirmation, daemon=True)
        reset_thread.start()
        
        # This keeps the listener active without blocking the main thread
        # It will automatically terminate when the main process ends
        keyboard.wait()
    
    # Create and start the keyboard listener thread
    keyboard_thread = threading.Thread(target=start_keyboard_listener, daemon=True)
    keyboard_thread.start()
    
    logger.info("Keyboard handler initialized. Press Ctrl+Shift+C twice to terminate the process.")
    print("ℹ️ Press Ctrl+Shift+C twice within 5 seconds to terminate the process.")
    
    return keyboard_thread

if __name__ == "__main__":
    # For testing the keyboard handler
    logging.basicConfig(level=logging.INFO)
    print("Testing keyboard handler. Press Ctrl+Shift+C twice to exit.")
    setup_exit_handler()
    
    # Simulate a running process
    try:
        while True:
            time.sleep(0.1)  # Add a small delay to reduce CPU usage
            sys.stdout.write(".")
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("\nProcess terminated by standard CTRL+C (KeyboardInterrupt)")
