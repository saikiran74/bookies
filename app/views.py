from math import ceil
from sys import flags
from django.shortcuts import render
from django.contrib.auth.models import User,auth
import csv
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from django.contrib.auth.decorators import login_required
from app.models import All,Like
from csv import DictWriter
# Create your views here.

def landingpage(request):
    return render(request,"landingpage.html")



def author(request,pk):
    authorbook = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    authorbook=authorbook[(authorbook['bookauthor']==pk)]
    author=authorbook.to_dict('records')
    return render(request,"author.html",{'author':author,'pk':pk})
    
def publisher(request,pk):
    publisherbook = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    publisherbook=publisherbook[(publisherbook['publisher']==pk)]
    publisher=publisherbook.to_dict('records')
    return render(request,"publisher.html",{'publisher':publisher,'pk':pk})


def rating(request,pk):
    if(request.method=="POST"):
        rating = pd.read_csv('Ratings.csv',dtype='unicode', sep=',')
        user = pd.read_csv('Users.csv',dtype='unicode', sep=',')
        rating.columns=['userid','ISBN','bookrating']
        user.columns=['userid','location','age']
        ratinggiven= request.POST['rating']
        #print("rating given",ratinggiven)
        #print(pk)
        #print(request.user.id)
        #rating.loc[len(rating.index)] = [request.user.id, pk, ratinggiven] 
        dic= {'userid':request.user.id, "ISBN":pk, "bookrating":ratinggiven}
        with open('Ratings.csv', 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=rating.columns)
            dictwriter_object.writerow(dic)
            #print("done successfully")
            f_object.close()
        return redirect('index')




def likepage(request):
    tmp=Like.objects.filter(username=request.user.username).filter(like="like")
    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']
    book=book.to_dict('records')
    return render(request,"like.html",{"tmp":tmp,'book':book})

def like(request,pk): 
    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    like=Like()
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']
    tmp=Like.objects.all()
    book=book[book['ISBN']==pk]
    book=book['ISBN'].tolist()
    flag=False
    for i in tmp:
        if(str(i.username)==str(request.user.username) and i.ISBN==book[0]):
            flag=True
            if(i.like=="dislike"):
                i.like="like"
            else:
                i.like="dislike"
            i.save()
    if(flag==False):
        like.username=request.user
        like.ISBN=book[0]
        like.like="like"
        like.save()
    return redirect('likepage')






@login_required(login_url='signin')
def history(request):
    all=All.objects.get(username=request.user.username)
    list=all.history.split(",")
    #print(list)
    list=list[::-1] 
    #print(list)
    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']

    book=book.to_dict('records')
    return render(request,"history.html",{'l':list,'book':book})



@login_required(login_url='signin')
def update(request):
    if(request.method=='POST'):
        pk=request.user.username
        all=All.objects.get(username=pk)
        #all.username= request.POST['username']
        all.firstname= request.POST['first_name']
        all.lastname= request.POST['last_name']
        all.email= request.POST['email1']
        all.age=request.POST['age']
        all.country=request.POST['country']
        all.save()
        return redirect('index')
    else:
        all=All.objects.get(username=request.user.username)
        return render(request,"update.html",{'all':all})




@login_required(login_url='signin')
def index(request):
    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    rating = pd.read_csv('Ratings.csv',dtype='unicode', sep=',')
    user = pd.read_csv('Users.csv',dtype='unicode', sep=',')    
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']
    rating.columns=['userid','ISBN','bookrating']
    user.columns=['userid','location','age']
    
    count=rating['ISBN'].value_counts()
    rating=rating[rating['ISBN'].isin(count[count>=50].index)] 
    book=book.drop_duplicates(['booktitle'])
    fin=pd.merge(rating,book,on="ISBN")
    filloc=pd.merge(fin,user,on="userid")
    
    filloc=filloc.drop_duplicates(['userid','booktitle'])
    mat=filloc.pivot(index='booktitle',columns="userid",values="bookrating").fillna(0)

    model=NearestNeighbors(metric="cosine",algorithm="brute")
    model.fit(mat)

    query_index=np.random.choice(mat.shape[0]) 
    #print(query_index)
    distances,indices=model.kneighbors(mat.iloc[query_index,:].values.reshape(1,-1),n_neighbors=6)

    l=[]
    for i in range(0,len(distances.flatten())):
        if i==0:
            pass
            #print("Recommended {0}:\n".format(mat.index[query_index])) 
        else:
            #print("{0}:{1},with of {2}:".format(i,mat.index[indices.flatten()[i]],distances.flatten()[i]))
            l.append(mat.index[indices.flatten()[i]])
    #print(l)
    

    book=book.to_dict('records')
    
    return render(request,"index.html",{'book':book,'l':l}) 

@login_required(login_url='signin')
def bookvisit(request,pk):
    #history
    all=All.objects.get(username=request.user.username)
    if(all.history=="None"):
        all.history=""
        all.history+=pk 
        historylist=all.history.split(",")
    else:
        str=""
        historylist=all.history.split(",")
        if(pk in historylist):
            #print("true")
            historylist.remove(pk)
        for i in range(len(historylist)):
            if(i==0):
                str+=historylist[i]
            else:
                str+=","+historylist[i]
        str+=","+pk
        all.history=str 
    all.save()

    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    rating = pd.read_csv('Ratings.csv',dtype='unicode', sep=',')
    user = pd.read_csv('Users.csv',dtype='unicode', sep=',')    
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']
    rating.columns=['userid','ISBN','bookrating']
    user.columns=['userid','location','age']
    book=book.drop_duplicates(['booktitle','ISBN'])
    
    res1=book[(book['booktitle']==pk)]
    res=res1.to_dict('records')
    book=book.to_dict('records')
    #my ratings
    filter=rating[rating['ISBN'].str.contains(res[0]['ISBN'])] 
    coun=filter['ISBN'].value_counts()
    t=coun[0]
    #for average rating
    list=filter['bookrating'].tolist()
    tot=0
    sum=0
    for i in range(len(list)):
        if(list[i]!='0'):
            sum+=int(list[i])
            tot+=1
    avg=ceil(sum/tot)
    #like
    tmp=Like.objects.all()
    likebook=res1['ISBN'].tolist()
    like="None"
    for i in tmp:
        if(i.username==request.user.username and i.ISBN==likebook[0] and i.like=="like"):
            like="liked"
        else:
            like="None"
    
    return render(request,"bookvisit.html",{'res':res,'book':book,'t':t,'avg':avg,'s':pk,'like':like})
    #'t':t,'avg':avg,

@login_required(login_url='signin')
def visit(request,pk):
    all=All.objects.get(username=request.user.username)
    if(all.history=="None"):
        all.history=""
        all.history+=pk 
        historylist=all.history.split(",")
    else:
        str=""
        historylist=all.history.split(",")
        if(pk in historylist):
            #print("true")
            historylist.remove(pk)
        for i in range(len(historylist)):
            if(i==0):
                str+=historylist[i]
            else:
                str+=","+historylist[i]
        str+=","+pk
        all.history=str 
    all.save()

    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    authorbook = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    publisherbook = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    rating = pd.read_csv('Ratings.csv',dtype='unicode', sep=',')
    user = pd.read_csv('Users.csv',dtype='unicode', sep=',')    
    book.columns=['ISBN','booktitle','bookauthor','yearofpublication','publisher' ,'imageurll']
    rating.columns=['userid','ISBN','bookrating']
    user.columns=['userid','location','age']
    count=rating['ISBN'].value_counts()
    rating=rating[rating['ISBN'].isin(count[count>=50].index)] 
    book=book.drop_duplicates(['booktitle','ISBN'])
    fin=pd.merge(rating,book,on="ISBN")
    res=fin[fin['booktitle']==pk]
    filloc=pd.merge(fin,user,on="userid")
    filloc=filloc.drop_duplicates(['userid','booktitle'])
    mat=filloc.pivot(index='booktitle',columns="userid",values="bookrating").fillna(0) 
    model=NearestNeighbors(metric="cosine",algorithm="brute")
    model.fit(mat)
    query_index=pk
    #print(query_index)
    distances,indices=model.kneighbors(mat.loc[query_index,:].values.reshape(1,-1),n_neighbors=6)
    l=[]
    for i in range(0,len(distances.flatten())):
        if i==0:
            pass
            #print("Recommended {0}:\n".format(mat.index[query_index])) 
        else:
            #print("{0}:{1},with of {2}:".format(i,mat.index[indices.flatten()[i]],distances.flatten()[i]))
            l.append(mat.index[indices.flatten()[i]])
    #print(l)
    #print("pk is",pk)
    res1=book[(book['booktitle']==pk)]
    res=res1.to_dict('records')
    book=book.to_dict('records')
    #total rating count
    filter=fin[fin['booktitle']==pk]
    coun=filter['booktitle'].value_counts()
    t=coun[0]
    #for average rating
    list=filter['bookrating'].tolist()
    tot=0
    sum=0
    for i in range(len(list)):
        if(list[i]!='0'):
            sum+=int(list[i])
            tot+=1
    avg=ceil(sum/tot)
    #like
    tmp=Like.objects.all()
    likebook=res1['ISBN'].tolist()
    like="None"
    for i in tmp:
        if(i.username==request.user.username and i.ISBN==likebook[0] and i.like=="like"):
            like="liked"
        else:
            like="None"
    #publisher books
    fin=fin.drop_duplicates(['booktitle','ISBN'])
    
    print(res[0]['publisher'])
    publisherbook=fin[fin['publisher']==res[0]['publisher']]
    publisherbookdic=publisherbook.to_dict('records')
    #author books
    print(res[0]['bookauthor'])
    authorbook=fin[(fin['bookauthor']==res[0]['bookauthor'])]
    authorbookdic=authorbook.to_dict('records')
    '''
    #publisher books
    print(res[0]['publisher'])
    publisherbook=publisherbook[publisherbook['publisher']==res[0]['publisher']]
    publisherbookdic=publisherbook.to_dict('records')
    #author books
    print(res[0]['bookauthor'])
    authorbook=authorbook[(authorbook['bookauthor']==res[0]['bookauthor'])]
    authorbookdic=authorbook.to_dict('records')
    '''

    return render(request,"visit.html",{'res':res,'book':book,'s':pk,'l':l,'t':t,'avg':avg,'like':like,'authorbookdic':authorbookdic,'publisherbookdic':publisherbookdic})
@login_required(login_url='signin')
def search(request):
    book = pd.read_csv('Books.csv',dtype='unicode', sep=',')
    if request.method=='POST':
        search=request.POST['search'] 
        #res=book[book['booktitle'].str.contains(search)] 
        #res=res.to_dict('records')
        book=book.to_dict('records')
        search=search.lower()
        l=[]
        count=0
        for i in book:
            if(search in i['booktitle'].lower()):
                l.append(i['ISBN'])
                count+=1
        return render(request,'search.html',{'book':book,'s':search,'l':l}) 
    '''
    if request.method=='POST':
        search=request.POST['search'] 
        res=book[book['booktitle'].str.contains(search)] 
        res=res.to_dict('records')
        #res=Books.objects.filter(BookTitle__contains=search)
        return render(request,'search.html',{'res':res,'s':search}) 
    '''

def createaccount(request):
    if request.method=='POST':
        tmp=All()
        username= request.POST['username']
        first_name= request.POST['first_name']
        last_name= request.POST['last_name']
        email= request.POST['email1']
        password1= request.POST['password1']
        password2= request.POST['password2']
        if password1==password2:
            if(User.objects.filter(username=username).exists()):
                messages.info(request,'Username already exist')
                return render(request,'createaccount.html')
            elif(User.objects.filter(email=email).exists()):
                messages.info(request,'email already exist')
                return render(request,'createaccount.html')
            else:
                user=User.objects.create_user(username=username,password=password1,email=email,first_name=first_name,last_name=last_name)
                tmp.username=username
                tmp.firstname=first_name
                tmp.lastname=last_name
                tmp.email=email
                tmp.age=request.POST['age']
                tmp.country=request.POST['country']
                user.save()
                tmp.save()
                #print("User created in create account also")
                return render(request,'signin.html')
        else:
            messages.info(request,'password did not matched')
            return render(request,'createaccount.html')
        
    else:
        return render(request,'createaccount.html')


def signin(request):
    if request.method=='POST':
        username=request.POST['username']
        password=request.POST['password']
        user=auth.authenticate(username=username ,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('index')
        else:
            messages.info(request,'Invalid username and password')
            return redirect('index')
    else:
        return render(request,'signin.html')

def logout(request):
    auth.logout(request)
    return redirect('signin')
