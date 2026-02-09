from .kinetics import simulate_transient

def step_reactivity_insertion(rho_step=0.005, t_insert=5, reactor_type="SMR (demo-friendly)"):
    def rho_ext(t):
        return 0.0 if t < t_insert else rho_step
    return simulate_transient(rho_ext, reactor_type=reactor_type, t_span=(0, 30))

def load_following(target_power_ratio=0.8, ramp_time=30, reactor_type="SMR (demo-friendly)"):
    def rho_ext(t):
        return 0.003 * min(t / ramp_time, 1.0) * (target_power_ratio - 1)
    return simulate_transient(rho_ext, reactor_type=reactor_type, t_span=(0, 120))