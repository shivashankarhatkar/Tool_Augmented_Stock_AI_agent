"""Convenience wrapper for module-level loggers."""
import logging


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
