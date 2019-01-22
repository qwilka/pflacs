import logging 

from pflacs import Premise, Calc


logger = logging.getLogger()
logger.setLevel(logging.INFO)  # logging.DEBUG 
lh = logging.StreamHandler()
logger.addHandler(lh)

pflacs_filepath = "very_simple_study.pflacs"

def adda(a, b, c=0, d=0, e=0):
    """Add number b to number a. Optionally also add 
    any of numbers c, d, e to the result.
    """
    print(f"Function `adda` called with arguments a={a} b={b}", end="")
    if c: print(f" c={c}", end="")
    if d: print(f" d={d}", end="")
    if e: print(f" e={e}", end="")
    print()
    return a + b + c + d + e

def suba(a, b, c, d=0, e=0):
    """Subtract numbers b and c from number a. Optionally also subtract 
    either or both of numbers d and e from the result.
    """
    print(f"Function `suba` called with arguments a={a} b={b} c={c}", end="")
    if d: print(f" d={d}", end="")
    if e: print(f" e={e}", end="")
    print()
    return a - b - c - d - e

print(f"Open existing study from `pflacs` file «{pflacs_filepath}».")
basecase = Premise.openfile(pflacs_filepath)
print(basecase.to_texttree())
