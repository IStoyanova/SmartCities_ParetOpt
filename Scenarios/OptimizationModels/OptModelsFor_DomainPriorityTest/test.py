from Scenarios.inftest import *
from openpyxl import Workbook

print('multiobjective Optimization of the multi-domain operation')
print()

T=96
a=light.get_energy_curves()
print(a)





"""wb = Workbook()
ws = wb.active

for t in range(T):
    ws.cell(row=2 + t, column= 2, value=a[t])


wb.save('opttest.xlsx')"""