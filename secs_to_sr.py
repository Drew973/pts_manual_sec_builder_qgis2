def secsToSR(secs,sr,header=True):
    with open(sr,'w') as f:
        if header:
            f.write('section,reversed\n')
        for s in secs:
            if s.reverse:
                f.write(s.label+','+'Yes'+'\n')
            else:
                f.write(s.label+','+'No'+'\n')
