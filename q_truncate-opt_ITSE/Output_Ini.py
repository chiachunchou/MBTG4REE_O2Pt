import numpy as np
import time

# --- 1. 參數與網格設定 ---
eV_to_H = 0.0367493
A_to_Bohr = 1.889726
fs_to_au = 41.341
amu_to_me = 1822.89
Phi = 5.82
EaO = 1.46 
mr = (15.999 / 2) * amu_to_me 
mz = (15.999 * 2) * amu_to_me

hr = 0.01
hZ = 0.01
hr_bohr = hr * A_to_Bohr
hZ_bohr = hZ * A_to_Bohr

Ri, Rf = 0.7, 4.0
Zi, Zf = 0.2, 5.7

My = int(np.round((Zf - Zi) / hZ)) + 1
Mx = int(np.round((Rf - Ri) / hr)) + 1
r = np.linspace(Ri, Rf, Mx)
Z = np.linspace(Zi, Zf, My)
Rm, Zm = np.meshgrid(r, Z)

Dg, Bg, rg, Ag, Cg, zg = 5.22, 2.65, 1.21, 20000, 3.3, -1.3
Dm, Bm, rm, Am, Cm, zm = 4.14, 1.64, 1.37, 5.77, 1.33, 1.7
Da, Ba, ra, Aa, Ca, za = 0.93, 2.82, 1.85, 16.1, 0.92, 0.85

# --- 2. 計算各項位能 ---
Vg = Dg * (np.exp(-2*Bg*(Rm-rg)) - 2*np.exp(-Bg*(Rm-rg))) + Ag * np.exp(-Cg * (Zm-zg))
Vm = Dm * (np.exp(-2*Bm*(Rm-rm)) - 2*np.exp(-Bm*(Rm-rm))) + Am * (np.exp(-2*Cm*(Zm-zm)) - 2*np.exp(-Cm*(Zm-zm))) + Phi - EaO
Va = Da * np.exp(-Ba*(Rm-ra)) + Aa * (np.exp(-2*Ca*(Zm-za)) - 2*np.exp(-Ca*(Zm-za))) + 2*(Phi - EaO)

Vgm = 0.62 * np.exp(-2.9 * (Zm - 2.35)**2)
Vam = 2.0 * np.exp(-10 * (Zm - 1.3)**2) * np.exp(-10 * (Rm - 1.62)**2)

# --- 3. 初始化儲存空間 ---
rows, cols = Rm.shape
Vgr = np.zeros((rows, cols))   
Cg_sq = np.zeros((rows, cols)) 
Cm_sq = np.zeros((rows, cols)) 
Ca_sq = np.zeros((rows, cols)) 

# --- 4. 雙層迴圈對角化 ---
print('Starting diagonalization loop...')
start_time = time.time()

for i in range(rows):       
    for j in range(cols):   
        H_local = np.array([[Vg[i,j],  Vgm[i,j], 0], 
                            [Vgm[i,j], Vm[i,j],  Vam[i,j]], 
                            [0,        Vam[i,j], Va[i,j]]])
        
        eigenvals, EigVecs = np.linalg.eigh(H_local)
        Vgr[i,j] = eigenvals[0]
        
        vec = EigVecs[:, 0]
        Cg_sq[i,j] = vec[0]**2
        Cm_sq[i,j] = vec[1]**2
        Ca_sq[i,j] = vec[2]**2

print(f'Loop finished in {time.time() - start_time:.2f} seconds.')

V = Vm * eV_to_H
Rm_calc = Rm * A_to_Bohr
Zm_calc = Zm * A_to_Bohr

# --- 5. 建立初始波函數 ---
f = np.sqrt(2/np.pi) * np.exp(-((Rm_calc - 2*A_to_Bohr)**2 + (Zm_calc - 2*A_to_Bohr)**2)/0.2)
f = f.astype(complex)
f[0, :] = 0; f[-1, :] = 0
f[:, 0] = 0; f[:, -1] = 0

# --- 6. 輸出起始條件 ---
print(f'目前矩陣大小: Z方向(My)={rows}, r方向(Mx)={cols}')
print('正在輸出 IniCndt_ITSE.dat...')
f_flat = f.flatten()
np.savetxt('IniCndt_ITSE.dat', np.column_stack((f_flat.real, f_flat.imag)), fmt='%.16e %.16e')

print('正在輸出 PES_ITSE.dat...')
V_flat = V.flatten()
np.savetxt('PES_ITSE.dat', np.column_stack((V_flat.real, np.zeros_like(V_flat))), fmt='%.16e %.16e')

print('========== 輸出完成 ==========')
