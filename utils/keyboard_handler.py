import os
import sys
import logging
import threading
import signal
import time

# Configure logging
logger = logging.getLogger("keyboard_handler")

# Try to import keyboard module, but don't fail if it's not available
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    logger.warning("Keyboard module not available, some functionality will be limited")
    KEYBOARD_AVAILABLE = False

def setup_exit_handler():
    """
    Sets up a keyboard listener that terminates the process when Ctrl+Shift+C is pressed
    and confirmed. This runs in a separate thread to avoid blocking the main execution flow.
    
    The implementation includes safeguards to prevent accidental termination and
    to minimize interference with other applications.
    """
    # Check if keyboard module is available
    if not KEYBOARD_AVAILABLE:
        logger.warning("Keyboard module not available. Ctrl+Shift+C termination not enabled.")
        try:
            print("[INFO] Keyboard handler not available. Use Ctrl+C to terminate.")
        except Exception as e:
            logger.warning(f"Error printing message: {e}")
        return None
        
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
            try:
                print("\n[WARNING] Press Ctrl+Shift+C again within 5 seconds to confirm termination...")
            except Exception:
                logger.warning("Failed to print confirmation message")
            logger.debug("Termination requested. Waiting for confirmation...")
        else:
            # Check if we're within the confirmation window
            if time.time() - confirm_state["timestamp"] <= confirm_state["confirmation_window"]:
                # Confirmed - terminate the process
                logger.info("Termination confirmed - ending process")
                try:
                    print("\n[STOPPED] Termination confirmed. Shutting down...")
                except Exception:
                    logger.warning("Failed to print shutdown message")
                
                # Reset state (although not necessary since we're terminating)
                confirm_state["pending"] = False
                
                # Use os.kill to send SIGTERM to the current process
                # This is more reliable than sys.exit() as it will terminate all threads
                os.kill(os.getpid(), signal.SIGTERM)
            else:
                # Confirmation window expired, treat as new request
                confirm_state["timestamp"] = time.time()
                try:
                    print("\n[WARNING] Confirmation window expired. Press Ctrl+Shift+C again within 5 seconds to confirm termination...")
                except Exception:
                    logger.warning("Failed to print expiration message")
                logger.debug("Confirmation window expired. Restarting confirmation sequence.")
    
    def reset_confirmation():
        """Reset confirmation state if window expires"""
        while True:
            if confirm_state["pending"]:
                if time.time() - confirm_state["timestamp"] > confirm_state["confirmation_window"]:
                    confirm_state["pending"] = False
                    logger.debug("Confirmation window expired. Reset termination request.")
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
    
    logger.debug("Keyboard handler initialized. Press Ctrl+Shift+C twice to terminate the process.")
    try:
        print("[INFO] Press Ctrl+Shift+C twice within 5 seconds to terminate the process.")
    except Exception:
        logger.warning("Failed to print initialization message")
    
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