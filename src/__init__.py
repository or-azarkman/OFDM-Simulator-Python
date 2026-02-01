"""
OFDM Simulator — core PHY-layer modules.

Usage:
    from src.transmitter import generate_ofdm_stream
    from src.receiver import demodulate_ofdm_symbols, compute_ber
    from src.channel import awgn_channel
    from src.theory import theoretical_ber
"""

__all__ = [
    "transmitter",
    "receiver",
    "channel",
    "theory",
    "equalizers",
]
