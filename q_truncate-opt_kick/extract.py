import numpy as np
import os

# --- 1. 參數設定 ---
TargetStep = 2000          # 提取 Kick 完 2fs 的步數
SourceFile = 'wave.dat'
OutputDir = 'TDSE_Input'
IniOutFile = os.path.join(OutputDir, 'IniCndt_TDSE.dat')

# 網格與物理參數 (與你之前的設定保持一致)
My, Mx = 551, 331
hr, hZ = 0.01, 0.01  # Angstrom
A_to_Bohr = 1.889726
hr_b = hr * A_to_Bohr
hZ_b = hZ * A_to_Bohr

# 質量 (me 原子單位)
amu_to_me = 1822.89
mr = (15.999 / 2) * amu_to_me
mz = (15.999 * 2) * amu_to_me

H_to_eV = 27.2114

print(f"🚀 開始提取 Step {TargetStep} 並分析動能...")

# --- 2. 讀取 wave.dat ---
psi = np.zeros((My, Mx), dtype=complex)
found = False

try:
    with open(SourceFile, 'r') as f:
        while True:
            line = f.readline()
            if not line: break
            parts = line.split()
            if len(parts) < 3: continue
            
            cur_step, num_pts = int(parts[0]), int(parts[2])
            if cur_step == TargetStep:
                for _ in range(num_pts):
                    d = f.readline().split()
                    psi[int(d[0]), int(d[1])] = float(d[4]) + 1j * float(d[5])
                found = True
                break
            else:
                for _ in range(num_pts): f.readline()
except FileNotFoundError:
    print(f"❌ 找不到 {SourceFile}"); exit()

if not found:
    print(f"❌ 找不到 Step {TargetStep}"); exit()

# --- 3. 計算動能 (Kinetic Energy) ---
# 使用二階中心差分計算二階導數 d^2/dx^2
# 邊界點不參與導數運算 (設為0)
d2psi_dz2 = np.zeros_like(psi)
d2psi_dr2 = np.zeros_like(psi)

# Z 方向 (Row 方向)
d2psi_dz2[1:-1, :] = (psi[2:, :] - 2*psi[1:-1, :] + psi[0:-2, :]) / (hZ_b**2)
# r 方向 (Col 方向)
d2psi_dr2[:, 1:-1] = (psi[:, 2:] - 2*psi[:, 1:-1] + psi[:, 0:-2]) / (hr_b**2)

# 計算期望值 <psi| -1/2m * nabla^2 |psi>
# 注意：積分包含 dr * dz 的體積元
Tz_au = -0.5 / mz * np.sum(np.conj(psi) * d2psi_dz2) * hr_b * hZ_b
Tr_au = -0.5 / mr * np.sum(np.conj(psi) * d2psi_dr2) * hr_b * hZ_b

Tz_eV = Tz_au.real * H_to_eV
Tr_eV = Tr_au.real * H_to_eV

print("\n" + "="*30)
print(f"📊 波包動能分析 (Step {TargetStep}):")
print(f"  - Z 方向 (平移) 動能: {Tz_eV:.6f} eV")
print(f"  - r 方向 (振動) 動能: {Tr_eV:.6f} eV")
print(f"  - 總動能: {Tz_eV + Tr_eV:.6f} eV")
print("="*30 + "\n")

# --- 4. 寫入 IniCndt.dat ---
os.makedirs(OutputDir, exist_ok=True)
with open(IniOutFile, 'w') as f_out:
    for i in range(My):
        for j in range(Mx):
            f_out.write(f"{psi[i,j].real:.16e} {psi[i,j].imag:.16e}\n")

print(f"✅ 提取完成！新初始檔位於: {IniOutFile}")
