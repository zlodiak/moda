import csv

with open('test.csv', 'w', newline='') as fp:
    a = csv.writer(fp, delimiter=',')
    data = [['Me', 'You'],
            ['293', '219'],
            ['54', '13']]
    a.writerows(data)
