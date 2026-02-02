results/summary — Summary outputs from the OFDM simulation (organized by metric type).

ORGANIZED STRUCTURE:
  ber/                    — BER comparison plots and tables
  evm/                    — EVM comparison plots and tables
  constellation/          — Constellation comparison plots
  pilots/                 — Pilot-based channel estimation comparison plots
  docs/                   — Summary documentation

See README.md for detailed structure and contents.

To regenerate: run from project root as described in docs/RUN_AND_TEST.md
  (plot_ber_comparison.py for BER; plot_evm_comparison.py for EVM;
   plot_constellation_comparison.py for constellation;
   plot_pilots_comparison.py for pilots comparison).

To organize existing files: py results/summary/ORGANIZE_EXISTING.py

Results folder layout: <N>_symbols (AWGN), <N>_symbols_multipath (no equalizer), 
<N>_symbols_multipath_zf, <N>_symbols_multipath_mmse, 
<N>_symbols_multipath_zf_pilots, <N>_symbols_multipath_mmse_pilots.
Each run directory contains: images/ (BER, EVM, constellation plots), CSV files.
