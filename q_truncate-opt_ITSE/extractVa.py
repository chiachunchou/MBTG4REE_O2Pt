import numpy as np
import os

# --- 參數設定 ---
TargetStep = 8000000
SourceFile = 'wave.dat'
OutputDir = 'KICK_Input_Va' 
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
Da, Ba, ra = 0.93, 2.82, 1.85
Aa, Ca, za = 16.1, 0.92, 0.85
Phi, EaO = 5.82, 1.46

print(f"🚀 開始執行！準備從 {SourceFile} 提取 Step {TargetStep} 的波函數...")

# --- 1. 計算位能面 V (Hartree) ---
r = np.linspace(Ri, Rf, Mx)
Z = np.linspace(Zi, Zf, My)
Rm, Zm = np.meshgrid(r, Z)

Va = Da * np.exp(-Ba*(Rm-ra)) + Aa * (np.exp(-2*Ca*(Zm-za)) - 2*np.exp(-Ca*(Zm-za))) + 2*(Phi - EaO)
V = Va * eV_to_H

# --- 2. 提取波函數 ---
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
                print(f"✅ 找到目標步數 Step {TargetStep}！正在讀取資料...")
                for _ in range(num_points):
                    data = f.readline().split()
                    z_idx, r_idx = int(data[0]), int(data[1])
                    real_part, imag_part = float(data[4]), float(data[5])
                    f_extracted[z_idx, r_idx] = real_part + 1j * imag_part
                found = True
                break
            else:
                # 快速跳過不相關的行數
                for _ in range(num_points):
                    f.readline()
except FileNotFoundError:
    print(f"❌ 錯誤：找不到檔案 {SourceFile}")
    exit()

if not found:
    print(f"❌ 錯誤：在檔案中找不到 Step {TargetStep} 的數據！")
    exit()

# --- 3. 輸出檔案 ---
os.makedirs(OutputDir, exist_ok=True)

print(f"✍️  正在寫入初始波函數 -> {IniOutFile}")
with open(IniOutFile, 'w') as f_ini:
    for i in range(My):
        for j in range(Mx):
            val = f_extracted[i, j]
            f_ini.write(f"{val.real:.16e} {val.imag:.16e}\n")

print(f"✍️  正在寫入位能面 -> {PesOutFile} (單位: Hartree)")
with open(PesOutFile, 'w') as f_pes:
    for i in range(My):
        for j in range(Mx):
            f_pes.write(f"{V[i, j]:.16e} 0.0000000000000000e+00\n")

print(f"\n🎉 任務完美達成！檔案已儲存於 {OutputDir} 資料夾中！")
