import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from textwrap import dedent

# ---------- Paths ----------
root = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path(".")
data_dir = root / "data"
fig_dir = root / "figs"
fig_dir.mkdir(parents=True, exist_ok=True)

# ---------- Constants and calibration ----------
MU0 = 4e-7 * np.pi  # H/m

L = 0.075      # m
R1 = 5.0       # ohm
N1_sample1 = 60
N1_sample2 = 90
KH = {  # A/m per V
    "Sample1": N1_sample1 / (L * R1),   # 160
    "Sample2": N1_sample2 / (L * R1),   # 240
}

C2 = 20e-6     # F
R2 = 10e3      # ohm
N2 = 200
S = 120e-6     # m^2
KB = (C2 * R2) / (N2 * S)      # T per V  -> 8.333...
KB_per_mV = KB / 1000.0        # T per mV

# ---------- Helpers ----------
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def interp_zero_x(x, y):
    """Return x at y=0 using linear interpolation; assumes one crossing."""
    x = np.asarray(x); y = np.asarray(y)
    s = np.sign(y)
    idx = np.where(s[:-1] * s[1:] <= 0)[0]
    if len(idx) == 0:
        return np.nan
    i = idx[0]
    x0, x1, y0, y1 = x[i], x[i + 1], y[i], y[i + 1]
    if y1 == y0:
        return np.nan
    return x0 + (0 - y0) * (x1 - x0) / (y1 - y0)

def interp_y_at_x0(x, y):
    """Return y at x=0 using the two points closest to zero."""
    x = np.asarray(x); y = np.asarray(y)
    idx = np.argsort(np.abs(x))[:2]
    x0, x1, y0, y1 = x[idx[0]], x[idx[1]], y[idx[0]], y[idx[1]]
    if x1 == x0:
        return np.nan
    return y0 + (0 - x0) * (y1 - y0) / (x1 - x0)

def loop_area(H, B):
    """Shoelace formula for closed curve area; returns positive scalar."""
    H = np.asarray(H); B = np.asarray(B)
    if H[0] != H[-1] or B[0] != B[-1]:
        H = np.r_[H, H[0]]
        B = np.r_[B, B[0]]
    return 0.5 * np.abs(np.sum(H[:-1] * B[1:] - H[1:] * B[:-1]))

# ---------- Analysis ----------
def analyze_sample(base_path: Path, hyst_path: Path, name: str):
    base = load_csv(base_path)
    hyst = load_csv(hyst_path)

    # Relative plots (as in instruments)
    X = base.filter(regex="X").values.squeeze()   # ~ UH (V)
    Y = base.filter(regex="Y").values.squeeze()   # ~ UB (mV)
    UH = hyst.filter(regex="UH").values.squeeze()
    UB = hyst.filter(regex="UB").values.squeeze()

    # Initial slope (relative)
    i1 = np.argmax(X > 0)
    k0_simple = (Y[i1] - Y[0]) / (X[i1] - X[0]) if X[i1] != X[0] else np.nan
    mask_rel = Y <= (0.6 * Y.max())
    if mask_rel.sum() < 3:
        mask_rel = np.arange(min(4, len(X)))
    coef_rel = np.polyfit(X[mask_rel], Y[mask_rel], 1)
    k0_fit = coef_rel[0]

    # Hysteresis metrics (relative)
    Bs_rel = float(np.max(np.abs(UB)))
    Hc_rel = float(np.abs(interp_zero_x(UH, UB)))
    Br_rel = float(np.abs(interp_y_at_x0(UH, UB)))
    S_rel = Br_rel / Bs_rel if Bs_rel else np.nan
    area_rel = loop_area(UH, UB)  # V·mV

    # Plots (relative)
    plt.figure()
    plt.plot(X, Y, "o-", lw=1.8)
    plt.xlabel("X (V)  ~ H (relative)")
    plt.ylabel("Y (mV) ~ B (relative)")
    plt.title(f"{name} 基本磁化曲线（相对）")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_dir / f"{name.lower()}_base.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(UH, UB, "o-", lw=1.8)
    plt.xlabel("UH (V) ~ H (relative)")
    plt.ylabel("UB (mV) ~ B (relative)")
    plt.title(f"{name} 磁滞回线（相对）")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_dir / f"{name.lower()}_hyst.png", dpi=160)
    plt.close()

    # SI conversion
    kH = KH[name]
    H_base = kH * X
    B_base = KB_per_mV * Y
    H_hyst = kH * UH
    B_hyst = KB_per_mV * UB

    # Low-field slope and mu_r0
    mask_si = B_base <= min(0.5, 0.6 * B_base.max())
    if np.sum(mask_si) < 3:
        mask_si = np.arange(min(4, len(H_base)))
    p = np.polyfit(H_base[mask_si], B_base[mask_si], 1)
    dBdH = float(p[0])
    mu_r0 = dBdH / MU0

    # Hysteresis metrics (SI)
    Bs = float(np.max(np.abs(B_hyst)))
    Hc = float(np.abs(interp_zero_x(H_hyst, B_hyst)))
    Br = float(np.abs(interp_y_at_x0(H_hyst, B_hyst)))
    S_fac = Br / Bs if Bs else np.nan
    area_SI = loop_area(H_hyst, B_hyst)

    # Plots (SI)
    plt.figure()
    plt.plot(H_base, B_base, "o-", lw=1.8)
    plt.xlabel("H (A/m)")
    plt.ylabel("B (T)")
    plt.title(f"{name} 基本磁化曲线（SI）")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_dir / f"{name.lower()}_base_SI.png", dpi=160)
    plt.close()

    plt.figure()
    plt.plot(H_hyst, B_hyst, "o-", lw=1.8)
    plt.xlabel("H (A/m)")
    plt.ylabel("B (T)")
    plt.title(f"{name} 磁滞回线（SI）")
    plt.grid(True, ls="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(fig_dir / f"{name.lower()}_hyst_SI.png", dpi=160)
    plt.close()

    return {
        # Relative
        "name": name,
        "Bs_rel_mV": Bs_rel,
        "Br_rel_mV": Br_rel,
        "Hc_rel_V": Hc_rel,
        "S_rel": S_rel,
        "k0_simple_mV_per_V": k0_simple,
        "k0_fit_mV_per_V": k0_fit,
        "loop_area_rel_VmV": area_rel,
        # SI
        "kH_Apm_per_V": kH,
        "kB_T_per_V": KB,
        "Bs_T": Bs,
        "Br_T": Br,
        "Hc_A_per_m": Hc,
        "S": S_fac,
        "dBdH_T_per_Am": dBdH,
        "mu_r0": mu_r0,
        "loop_area_J_per_m3": area_SI,
    }

def main():
    res = []
    res.append(analyze_sample(data_dir / "sample1_base.csv", data_dir / "sample1_hyst.csv", "Sample1"))
    res.append(analyze_sample(data_dir / "sample2_base.csv", data_dir / "sample2_hyst.csv", "Sample2"))
    df = pd.DataFrame(res)
    out = root / "results_summary.csv"
    df.to_csv(out, index=False)
    print("Saved:", out)
    for r in res:
        print(dedent(f"""
        {r['name']} (SI):
          Bs = {r['Bs_T']:.3f} T, Br = {r['Br_T']:.3f} T, Hc = {r['Hc_A_per_m']:.1f} A/m, S = {r['S']:.3f}
          dB/dH = {r['dBdH_T_per_Am']:.4e} T/(A/m),  μr0 ≈ {r['mu_r0']:.0f}
          Loop area ≈ {r['loop_area_J_per_m3']:.1f} J/m^3 per cycle
        """))

if __name__ == "__main__":
    main()