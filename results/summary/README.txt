results/summary — Summary outputs from the OFDM simulation.

Contents (relative to project root):
  simulation_summary.md       — Results summary and conclusions
  comparison_table.csv        — BER by SNR, scenario, modulation (long format)
  comparison_table.md         — BER data in four tables (one per scenario)
  comparison_table_readable.txt — BER tables, plain text
  evm_comparison_table.csv    — EVM (%) by SNR, scenario, modulation (long format)
  evm_comparison_table.md      — EVM data in four tables (one per scenario)
  ber_comparison_awgn_vs_multipath_*.png, ber_500_vs_5000_*.png, ber_comparison_zf_vs_mmse_*.png
  evm_comparison_awgn_vs_multipath_*.png, evm_comparison_zf_vs_mmse_*.png, evm_comparison_all_scenarios_*.png
  constellation_comparison_QPSK.png, constellation_comparison_16QAM.png

To regenerate: run from project root as described in docs/RUN_AND_TEST.md
  (plot_ber_comparison.py for BER table and plots; plot_evm_comparison.py for EVM table and plots;
   plot_constellation_comparison.py for 4×3 constellation grid).

Results folder layout: <N>_symbols (AWGN), <N>_symbols_multipath (no equalizer), <N>_symbols_multipath_zf, <N>_symbols_multipath_mmse.
Each run directory contains: images/ (BER, EVM, constellation plots), CSV files (ber_vs_snr_*.csv, evm_vs_snr_*.csv).
