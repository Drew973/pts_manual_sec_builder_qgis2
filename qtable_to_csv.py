
def qtable_to_csv(table,csv,header=True):
    xr=range(0,table.columnCount())

    with open(csv,'w') as f:
        if header:
            row=[]
            for x in xr:
                item=table.horizontalHeaderItem(x)
                if item:
                    row.append(item.text())
                else:
                    row.append(None)
            f.write(','.join(row)+'\n')
            
        for y in range(0,table.rowCount()):
            row=[]
            for x in xr:
                item=table.item(y,x)#y then x. QT documentation lies. 
                if item:
                    row.append(item.text())
                else:
                    row.append(None)
            f.write(','.join(row)+'\n')
           

