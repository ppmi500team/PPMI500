import ppmi500

qc_AR = '../ppmi500/data/QC/ppmi500_AR.csv'
qc_BA = '../ppmi500/data/QC/ppmi500_BA.csv'
qc_LF = '../ppmi500/data/QC/ppmi500_LF.csv'
qc_XW = '../ppmi500/data/QC/ppmi500_XW.csv'

df = ppmi500.process_qc_data(qc_AR, qc_LF, qc_BA, qc_XW)
print(df)
