from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Any, Tuple

class ThreadPoolManager:
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers

    def run(
        self,
        func: Callable,
        *iterables: Iterable,
        return_exceptions: bool = False,
        preserve_order: bool = True,
    ) -> List[Any]:
        """
        Execute `func` concurrently using arguments from zipped iterables.

        Example:
            manager.run(my_func, list1, list2): calls my_func(a, b) for a, b in zip(list1, list2)

        Args:
            func: Function to execute
            *iterables: Argument iterables (zipped together)
            return_exceptions: If True, return exceptions instead of raising
            preserve_order: If True, results match input order

        Returns:
            List of results

        WARNING: 
            This should be used for functions that take a set of input parameters and return outputs, without modifying the inputs or global variables.
            If multiple concurrent tasks attempt to change data outside of their own scope, negative outcomes are likely to occur.
        """

        tasks: List[Tuple] = list(zip(*iterables))
        results = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(func, *args): idx
                for idx, args in enumerate(tasks)
            }

            if preserve_order:
                for future in future_to_index:
                    idx = future_to_index[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        if return_exceptions:
                            results[idx] = e
                        else:
                            raise
            else:
                results = []
                for future in as_completed(future_to_index):
                    try:
                        results.append(future.result())
                    except Exception as e:
                        if return_exceptions:
                            results.append(e)
                        else:
                            raise

        return results
