import numpy as np
class StressDetector:
    def __init__(self, window_size=15, baseline_rmssd=30, stress_rmssd_threshold=0.5, high_bpm_threshold=100):
        """
        Initialize the stress detector.
        :param window_size: Number of RR intervals in the sliding window.
        :param baseline_rmssd: Baseline RMSSD value (measured at rest).
        :param stress_rmssd_threshold: Fraction of baseline RMSSD below which stress is detected.
        :param high_bpm_threshold: BPM above which physical exertion is likely.
        """
        self.window_size = window_size
        self.rr_intervals = []  # Store RR intervals
        self.baseline_rmssd = baseline_rmssd
        self.rmssd_threshold = baseline_rmssd * stress_rmssd_threshold
        self.high_bpm_threshold = high_bpm_threshold
    def add_heart_rate(self, heart_rate):
        """
        Add a heart rate reading and update RR intervals.
        :param heart_rate: Current heart rate in BPM.
        :return: Stress status ('Relaxed', 'Physical Exertion', 'Stressed') or None if insufficient data.
        """
        # Convert heart rate to RR interval (ms)
        rr_interval = 60000 / heart_rate
        self.rr_intervals.append(rr_interval)
        
        # Maintain sliding window
        if len(self.rr_intervals) > self.window_size:
            self.rr_intervals.pop(0)
        
        # Calculate HRV (RMSSD) if enough data
        if len(self.rr_intervals) > 1:
            rmssd = self.calculate_rmssd()
            return self.detect_stress(rmssd, heart_rate)
        else:
            return None  # Not enough data
    def calculate_rmssd(self):
        """
        Calculate RMSSD from RR intervals.
        :return: RMSSD value in ms.
        """
        rr_diffs = np.diff(self.rr_intervals)
        squared_diffs = rr_diffs ** 2
        rmssd = np.sqrt(np.mean(squared_diffs))
        return rmssd
    def detect_stress(self, rmssd, heart_rate):
        """
        Detect stress using RMSSD and BPM.
        :param rmssd: Current RMSSD value.
        :param heart_rate: Current heart rate in BPM.
        :return: Stress status ('Relaxed', 'Physical Exertion', 'Stressed').
        """
        if heart_rate > self.high_bpm_threshold:
            if rmssd < self.rmssd_threshold:
                return "Stressed (High BPM + Low HRV)"
            else:
                return "Physical Exertion (High BPM)"
        else:
            if rmssd < self.rmssd_threshold:
                return "Stressed (Low HRV)"
            else:
                return "Relaxed (Normal BPM + High HRV)"

if __name__ == "__main__":
    # Example Usage
    baseline_rmssd = 40  # Baseline RMSSD value
    stress_threshold = 0.5  # 50% of baseline
    high_bpm_threshold = 100  # BPM above which exertion is likely
    stress_detector = StressDetector(
        window_size=60,
        baseline_rmssd=baseline_rmssd,
        stress_rmssd_threshold=stress_threshold,
        high_bpm_threshold=high_bpm_threshold
    )
    # Simulated heart rates
    heart_rates = [75, 76, 85, 120, 125, 100, 85, 80, 55, 95, 105, 90,]
    for heart_rate in heart_rates:
        status = stress_detector.add_heart_rate(heart_rate)
        if status is not None:
            print(f"Heart Rate: {heart_rate} BPM, Status: {status}")
        else:
            print(f"Heart Rate: {heart_rate} BPM, Collecting more data...")

    # webpage:
    # https://www.kubios.com/blog/hrv-analysis-methods/