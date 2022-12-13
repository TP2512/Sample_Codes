def anagram(str1,str2):
  if sorted(str1)==sorted(str2):
    return True

def checklist(clist):
  List2=[]
  n=len(clist)
  for i in range(n):
    str1=List1[i]
    k=i+1
    for j in range(n-1):
      ei=k%n
      str2=clist[ei]
      if anagram(str1,str2):
          List2.append(str1)
          break
      k+=1
  return List2

List1 = ["pool", "hey", "why", "polo", "pol", "lopo", "apolo", "hye"]
print(checklist(List1))
#result:  ['pool', 'hey', 'polo', 'lopo', 'hye']
