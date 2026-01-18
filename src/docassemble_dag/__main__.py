"""
Entry point for running docassemble_dag as a module.

Allows: python -m docassemble_dag <args>
"""

from .cli import main

if __name__ == "__main__":
    main()
