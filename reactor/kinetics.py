import numpy as np
from scipy.integrate import solve_ivp
from .parameters import BETA, LAMBDA, BETA_TOTAL, REACTOR_TYPES
from .thermal_feedback import ThermalFeedback

def point_kinetics(t, y, rho_ext_func, feedback, lambda_prompt):
    P, C, Tf, Tc = y[0], y[1:7], y[7], y[8]
    rho_total = rho_ext_func(t) + feedback(Tf, Tc)
    dPdt = ((rho_total - BETA_TOTAL) / lambda_prompt) * P + np.dot(LAMBDA, C)
    dCdt = (BETA / lambda_prompt) * P - LAMBDA * C
    return [dPdt] + list(dCdt) + [
        feedback.dTfdt(P, Tf, Tc),
        feedback.dTcdt(P, Tf, Tc)
    ]

def simulate_transient(rho_ext_func, reactor_type="SMR (demo-friendly)", t_span=(0, 60), P0=1.0):
    params = REACTOR_TYPES[reactor_type]
    lambda_prompt = params["lambda_prompt"]
    feedback = ThermalFeedback(reactor_type)

    y0 = np.array([P0] + [0]*6 + [params["T_fuel0"], params["T_coolant0"]])

    sol = solve_ivp(
        lambda t, y: point_kinetics(t, y, rho_ext_func, feedback, lambda_prompt),
        t_span, y0, method='LSODA', rtol=1e-8, atol=1e-10, dense_output=True
    )

    # Compute reactivity history for plotting
    t_dense = np.linspace(t_span[0], t_span[1], 1000)
    y_dense = sol.sol(t_dense)
    P = y_dense[0]
    Tf = y_dense[7]
    Tc = y_dense[8]
    rho_ext = np.array([rho_ext_func(t) for t in t_dense])
    rho_fb = np.array([feedback(Tf[i], Tc[i]) for i in range(len(t_dense))])
    rho_total = rho_ext + rho_fb

    return {
        "t": t_dense,
        "P": P,
        "rho_ext": rho_ext,
        "rho_fb": rho_fb,
        "rho_total": rho_total,
        "Tf": Tf,
        "Tc": Tc
    }