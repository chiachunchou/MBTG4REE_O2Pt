#!/bin/bash
# ==========================================
# 量子動力學自動化管線 (完全依照手繪架構圖)
# ==========================================
set -e 

# ==========================================
# 徹底封鎖所有圖形介面請求 (Headless Exodia)
# ==========================================
unset DISPLAY
unset XAUTHORITY
export MPLBACKEND=Agg
export QT_QPA_PLATFORM=offscreen

# 啟動 16 執行緒平行運算
export OMP_DYNAMIC=FALSE
export OMP_NUM_THREADS=16
export OMP_PROC_BIND=spread
export OMP_PLACES=cores
echo "使用 $OMP_NUM_THREADS 執行緒！"

# 紀錄「project」總部的路徑
BASE_DIR=$(pwd)

# ==========================================
# 階段 1: q_truncate-opt_ITSE 處理區
# ==========================================
echo -e "\n[進入] q_truncate-opt_ITSE ..."
cd q_truncate-opt_ITSE

echo " 執行 Output_Ini.py (輸出初始波包)"
python3 Output_Ini.py

echo " 執行 ITSE (尋找基態)"
/usr/bin/time -p -a -o log0.txt ./qtr_mpi ./ini.test

echo " -> ③ 執行 extractVa.py (產生 KICK_Input_Va 檔案)"
python3 extractVa.py
cd $BASE_DIR

# ==========================================
# 階段 2: 傳輸檔案至 Kick & 執行 Kick
# ==========================================
echo -e "\n[傳輸] 複製 KICK_Input_Va 到 q_truncate-opt_kick..."
# 注意：這裡在複製時，順便將檔名改回 C++ 看得懂的通用名稱 IniCndt.datk/
cp q_truncate-opt_ITSE/KICK_Input_Va/PES_KICK.dat     q_truncate-opt_kick/
cp q_truncate-opt_ITSE/KICK_Input_Va/IniCndt_KICK.dat q_truncate-opt_kick/

echo -e "\n[進入] q_truncate-opt_kick ..."
cd q_truncate-opt_kick

echo " -> 執行 Kick"
/usr/bin/time -p -a -o log0.txt ./qtr_mpi ./ini.test

echo " -> 執行 extract.py (產生 TDSE_Input 檔案)"
python3 extract.py
cd $BASE_DIR

# ==========================================
# 階段 3: 傳輸檔案至 TDSE & 執行 TDSE
# ==========================================
echo -e "\n[傳輸] 複製 TDSE_Input 到 q_truncate-opt_TDSE..."
# 同樣地，複製過去時順便改回通用名稱
cp q_truncate-opt_kick/TDSE_Input/IniCndt_TDSE.dat q_truncate-opt_TDSE/

echo -e "\n[進入] q_truncate-opt_TDSE ..."
cd q_truncate-opt_TDSE

echo " -> 執行 TDSE (最終演化)"
/usr/bin/time -p -a -o log0.txt ./qtr_mpi ./ini.test
cd $BASE_DIR

echo -e "\n 全部流程執行完畢！完美對應流程圖！"