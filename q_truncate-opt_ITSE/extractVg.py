import numpy as np
import os

# --- 1. 參數設定 ---
TargetStep = 8000000       # 提取 ITSE 的最終基態
SourceFile = 'wave.dat'  # 你剛剛跑完 800萬步的檔案
OutputDir = 'Kick_Input_Vg'
IniOutFile = os.path.join(OutputDir, 'IniCndt_KICK.dat')
PesOutFile = os.path.join(OutputDir, 'PES_KICK.dat')

# 網格尺寸
My = 551
Mx = 331
hr, hZ = 0.01, 0.01
Ri, Rf = 0.7, 4.0
Zi, Zf = 0.2, 5.7

# 換算與物理參數
eV_to_H = 0.0367493
Dg, Bg, rg = 5.22, 2.65, 1.21
Ag, Cg, zg = 20000, 3.3, -1.3

print(f"🚀 開始準備 Kick 階段輸入檔...")

# --- 2. 計算 Vg 位能面 (Hartree) ---
r = np.linspace(Ri, Rf, Mx)
Z = np.linspace(Zi, Zf, My)
Rm, Zm = np.meshgrid(r, Z)

# 計算中性態 Vg
Vg_eV = Dg * (np.exp(-2*Bg*(Rm-rg)) - 2*np.exp(-Bg*(Rm-rg))) + Ag * np.exp(-Cg*(Zm-zg))
V = Vg_eV * eV_to_H

# --- 3. 提取 ITSE 基態波函數 ---
f_extracted = np.zeros((My, Mx), dtype=complex)
found = False

try:
    with open(SourceFile, 'r') as f:
        while True:
            line = f.readline()
            if not line: break
            line = line.strip()
            if not line: continue
            
            parts = line.split()
            if len(parts) < 3: continue
            
            try:
                current_step = int(parts[0])
                num_points = int(parts[2])
            except ValueError:
                continue
                
            if current_step == TargetStep:
                print(f"✅ 成功找到 ITSE 基態 (Step {TargetStep})！正在讀取...")
                for _ in range(num_points):
                    data = f.readline().split()
                    z_idx, r_idx = int(data[0]), int(data[1])
                    real_part, imag_part = float(data[4]), float(data[5])
                    f_extracted[z_idx, r_idx] = real_part + 1j * imag_part
                found = True
                break
            else:
                for _ in range(num_points):
                    f.readline()
except FileNotFoundError:
    print(f"❌ 錯誤：找不到檔案 {SourceFile}")
    exit()

if not found:
    print(f"❌ 錯誤：找不到 Step {TargetStep} 的數據！")
    exit()

# --- 4. 輸出檔案 ---
os.makedirs(OutputDir, exist_ok=True)

print(f"✍️  正在寫入初始波函數 -> {IniOutFile}")
with open(IniOutFile, 'w') as f_ini:
    for i in range(My):
        for j in range(Mx):
            val = f_extracted[i, j]
            f_ini.write(f"{val.real:.16e} {val.imag:.16e}\n")

print(f"✍️  正在寫入 Vg 位能面 -> {PesOutFile} (單位: Hartree)")
with open(PesOutFile, 'w') as f_pes:
    for i in range(My):
        for j in range(Mx):
            f_pes.write(f"{V[i, j]:.16e} 0.0000000000000000e+00\n")

print(f"\n🎉 任務完美達成！Kick 專用檔案已儲存於 [{OutputDir}] 資料夾中！")
