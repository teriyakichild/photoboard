from backend import pictures, boards

p = pictures()
#print p.new('asdf',1,1)
print p.get(1)

b = boards()
print p.all(1)
print b.get(1)
