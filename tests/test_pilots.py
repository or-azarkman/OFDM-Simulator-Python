"""
test_pilots.py

Unit tests for pilot subcarrier insertion and channel estimation.
"""

import numpy as np
import pytest

from src.pilots import (
    generate_pilot_pattern,
    generate_pilot_symbols,
    insert_pilots,
    extract_pilots,
    estimate_channel_ls,
    get_data_indices,
)
from src.transmitter import qpsk_modulate, generate_ofdm_symbol
from src.receiver import remove_cyclic_prefix, fft_ofdm


class TestPilotPattern:
    def test_pilot_spacing(self):
        """Test pilot pattern with spacing."""
        indices = generate_pilot_pattern(64, pilot_spacing=8)
        expected = np.array([0, 8, 16, 24, 32, 40, 48, 56])
        np.testing.assert_array_equal(indices, expected)

    def test_num_pilots(self):
        """Test pilot pattern with specified number."""
        indices = generate_pilot_pattern(64, num_pilots=8)
        assert len(indices) == 8
        assert indices[0] == 0
        assert indices[-1] < 64

    def test_num_pilots_exceeds_fft_size(self):
        """Test that num_pilots > fft_size raises error."""
        with pytest.raises(ValueError, match="cannot exceed"):
            generate_pilot_pattern(64, num_pilots=100)

    def test_pilot_symbols_generation(self):
        """Test pilot symbol generation."""
        symbols = generate_pilot_symbols(8)
        assert len(symbols) == 8
        assert np.allclose(symbols, 1.0 + 0j)

    def test_custom_pilot_value(self):
        """Test custom pilot symbol value."""
        symbols = generate_pilot_symbols(4, pilot_value=2.0 + 1j)
        assert np.allclose(symbols, 2.0 + 1j)


class TestInsertPilots:
    def test_insert_pilots_basic(self):
        """Test basic pilot insertion."""
        fft_size = 8
        pilot_indices = np.array([0, 4])
        pilot_symbols = np.array([1.0 + 0j, 1.0 + 0j])
        data_symbols = np.array([1 + 1j, 2 + 2j, 3 + 3j, 4 + 4j, 5 + 5j, 6 + 6j])
        
        frame = insert_pilots(data_symbols, pilot_indices, pilot_symbols, fft_size)
        
        assert len(frame) == fft_size
        assert frame[0] == pilot_symbols[0]
        assert frame[4] == pilot_symbols[1]
        assert frame[1] == data_symbols[0]
        assert frame[2] == data_symbols[1]

    def test_insert_pilots_length_mismatch(self):
        """Test that wrong number of data symbols raises error."""
        fft_size = 8
        pilot_indices = np.array([0, 4])
        pilot_symbols = np.array([1.0 + 0j, 1.0 + 0j])
        data_symbols = np.array([1 + 1j, 2 + 2j])  # Wrong length
        
        with pytest.raises(ValueError, match="must equal"):
            insert_pilots(data_symbols, pilot_indices, pilot_symbols, fft_size)

    def test_get_data_indices(self):
        """Test getting data subcarrier indices."""
        fft_size = 8
        pilot_indices = np.array([0, 4])
        data_indices = get_data_indices(fft_size, pilot_indices)
        expected = np.array([1, 2, 3, 5, 6, 7])
        np.testing.assert_array_equal(data_indices, expected)


class TestExtractPilots:
    def test_extract_pilots(self):
        """Test pilot extraction from frequency frame."""
        fft_size = 8
        pilot_indices = np.array([0, 4])
        frame = np.array([1.0 + 0j, 2.0, 3.0, 4.0, 1.0 + 0j, 5.0, 6.0, 7.0])
        
        pilots = extract_pilots(frame, pilot_indices)
        expected = np.array([1.0 + 0j, 1.0 + 0j])
        np.testing.assert_array_equal(pilots, expected)


class TestChannelEstimation:
    def test_perfect_channel_estimation(self):
        """Test LS channel estimation with perfect channel (H=1)."""
        fft_size = 64
        pilot_indices = generate_pilot_pattern(fft_size, pilot_spacing=8)
        tx_pilots = generate_pilot_symbols(len(pilot_indices))
        
        # Perfect channel: H = 1 for all subcarriers
        H_true = np.ones(fft_size, dtype=complex)
        rx_pilots = tx_pilots * H_true[pilot_indices]
        
        H_est = estimate_channel_ls(rx_pilots, tx_pilots, pilot_indices, fft_size)
        
        # Estimated channel should be close to true channel
        np.testing.assert_allclose(H_est, H_true, rtol=1e-10)

    def test_frequency_selective_channel(self):
        """Test LS channel estimation with frequency-selective channel."""
        fft_size = 64
        pilot_indices = generate_pilot_pattern(fft_size, pilot_spacing=8)
        tx_pilots = generate_pilot_symbols(len(pilot_indices))
        
        # Create frequency-selective channel
        H_true = np.fft.fft(np.array([1.0, 0.5, 0.3], dtype=complex), n=fft_size)
        rx_pilots = tx_pilots * H_true[pilot_indices]
        
        H_est = estimate_channel_ls(rx_pilots, tx_pilots, pilot_indices, fft_size)
        
        # At pilot positions, estimate should match true channel
        np.testing.assert_allclose(H_est[pilot_indices], H_true[pilot_indices], rtol=1e-10)

    def test_channel_estimation_with_noise(self):
        """Test LS channel estimation with noise (should still work, but less accurate)."""
        fft_size = 64
        pilot_indices = generate_pilot_pattern(fft_size, pilot_spacing=8)
        tx_pilots = generate_pilot_symbols(len(pilot_indices))
        
        H_true = np.ones(fft_size, dtype=complex)
        noise_power = 0.01
        noise = np.sqrt(noise_power) * (np.random.randn(len(pilot_indices)) + 1j * np.random.randn(len(pilot_indices)))
        rx_pilots = tx_pilots * H_true[pilot_indices] + noise
        
        H_est = estimate_channel_ls(rx_pilots, tx_pilots, pilot_indices, fft_size)
        
        # With noise, estimate should still be reasonable
        assert np.mean(np.abs(H_est - H_true)) < 0.2  # Allow some error due to noise


class TestPilotsWithOFDM:
    def test_ofdm_symbol_with_pilots(self):
        """Test generating OFDM symbol with pilots."""
        fft_size = 64
        cp_len = 16
        pilot_indices = generate_pilot_pattern(fft_size, pilot_spacing=8)
        pilot_symbols = generate_pilot_symbols(len(pilot_indices))
        
        # Generate bits for data subcarriers only
        num_data_subcarriers = fft_size - len(pilot_indices)
        bits_per_sub = 2  # QPSK
        total_bits = num_data_subcarriers * bits_per_sub
        bits = np.random.randint(0, 2, total_bits)
        
        ofdm_symbol = generate_ofdm_symbol(
            bits, fft_size, cp_len, "QPSK", pilot_indices, pilot_symbols
        )
        
        # Verify symbol structure
        assert len(ofdm_symbol) == fft_size + cp_len
        
        # Remove CP and check frequency domain
        symbol_no_cp = remove_cyclic_prefix(ofdm_symbol.reshape(1, -1), cp_len)[0]
        freq_frame = fft_ofdm(symbol_no_cp.reshape(1, -1))[0]
        
        # Verify pilots are in correct positions
        extracted_pilots = extract_pilots(freq_frame, pilot_indices)
        np.testing.assert_allclose(extracted_pilots, pilot_symbols, rtol=1e-10)

    def test_channel_estimation_integration(self):
        """Integration test: transmit with pilots, estimate channel, equalize."""
        np.random.seed(42)
        fft_size = 64
        cp_len = 16
        pilot_indices = generate_pilot_pattern(fft_size, pilot_spacing=8)
        pilot_symbols = generate_pilot_symbols(len(pilot_indices))
        
        # Generate OFDM symbol with pilots
        num_data_subcarriers = fft_size - len(pilot_indices)
        bits = np.random.randint(0, 2, num_data_subcarriers * 2)  # QPSK
        ofdm_symbol = generate_ofdm_symbol(
            bits, fft_size, cp_len, "QPSK", pilot_indices, pilot_symbols
        )
        
        # Simulate channel (frequency-selective)
        h_taps = np.array([1.0, 0.5, 0.3], dtype=complex)
        h_pad = np.zeros(fft_size, dtype=complex)
        h_pad[:len(h_taps)] = h_taps
        H_true = np.fft.fft(h_pad)
        
        # Apply channel in frequency domain
        symbol_no_cp = remove_cyclic_prefix(ofdm_symbol.reshape(1, -1), cp_len)[0]
        tx_freq = fft_ofdm(symbol_no_cp.reshape(1, -1))[0]
        rx_freq = tx_freq * H_true
        
        # Estimate channel from pilots
        rx_pilots = extract_pilots(rx_freq, pilot_indices)
        H_est = estimate_channel_ls(rx_pilots, pilot_symbols, pilot_indices, fft_size)
        
        # Verify estimation is reasonable
        pilot_mse = np.mean(np.abs(H_est[pilot_indices] - H_true[pilot_indices]) ** 2)
        assert pilot_mse < 1e-10  # Should be very accurate at pilot positions
