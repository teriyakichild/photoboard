from backend import photos, boards

p = photos()
#print p.new('asdf',1,1)
print p.get(1)

b = boards()
print p.all(1)
print b.get(1)
