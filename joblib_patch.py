"""
Patch for joblib ResourceTracker.__del__ method to fix the AttributeError:
'super' object has no attribute '__del__'

This patch modifies the ResourceTracker.__del__ method at runtime to properly
check if the parent class has a __del__ method before trying to call it.
"""

import sys
import types
import logging

logger = logging.getLogger(__name__)

def apply_joblib_patches():
    """Apply runtime patches to joblib to fix known issues."""
    try:
        # Import the module containing ResourceTracker
        from joblib.externals.loky.backend import resource_tracker
        from joblib.externals.loky.backend.resource_tracker import ResourceTracker

        # Check if the class has a __del__ method
        if hasattr(ResourceTracker, "__del__"):
            original_del = ResourceTracker.__del__

            # Define the fixed __del__ method
            def fixed_del(self):
                # Check if the parent class has a __del__ method
                if not hasattr(super(ResourceTracker, self), "__del__"):
                    return
                try:
                    super(ResourceTracker, self).__del__()
                except ChildProcessError:
                    pass

            # Replace the original __del__ method with our fixed version
            ResourceTracker.__del__ = fixed_del
            
            logger.info("Successfully patched joblib.externals.loky.backend.resource_tracker.ResourceTracker.__del__")
        else:
            logger.warning("ResourceTracker.__del__ method not found, patch not applied")
            
    except ImportError:
        logger.warning("Could not import joblib.externals.loky.backend.resource_tracker, patch not applied")
    except Exception as e:
        logger.error(f"Error applying joblib patch: {e}")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Apply the patch
    apply_joblib_patches()
    
    # Test if the patch works
    print("Testing joblib import...")
    import joblib
    print("Joblib imported successfully!")
    
    # Test parallel execution
    from joblib import Parallel, delayed
    import math
    print("Testing parallel execution...")
    result = Parallel(n_jobs=2)(delayed(math.sqrt)(i) for i in range(5))
    print(f"Parallel execution result: {result}")
    print("Test completed successfully!")
