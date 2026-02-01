results/summary — Summary outputs from the OFDM simulation.

Contents (relative to project root):
  simulation_summary.md       — Results summary and conclusions
  comparison_table.csv        — BER by SNR, scenario, modulation (long format)
  comparison_table.md         — Same data in four tables (one per scenario)
  comparison_table_readable.txt — Same four tables, plain text
  ber_comparison_awgn_vs_multipath_*.png, ber_500_vs_5000_*.png, ber_comparison_zf_vs_mmse_*.png
  constellation_comparison_QPSK.png, constellation_comparison_16QAM.png

To regenerate: run from project root as described in docs/RUN_AND_TEST.md
  (plot_ber_comparison.py for table and BER plots; plot_constellation_comparison.py for 4×3 constellation grid).

Results folder layout: <N>_symbols (AWGN), <N>_symbols_multipath (no equalizer), <N>_symbols_multipath_zf, <N>_symbols_multipath_mmse.
