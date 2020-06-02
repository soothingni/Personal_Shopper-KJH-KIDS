from django.shortcuts import render

# Create your views here.
def home(req):
    return render(req, 'step1/home.html')

def main(req):
    stars = ['iu', 'irene', 'hyuna']
    thumbnails = os.listdir('static/step1/star_thumbnails')
    context = {"stars": stars, "thumbnails": thumbnails, "length": len(thumbnails)}
    return render(req, 'step1/main.html', context)

def aboutus(req):
    return render(req, 'step1/aboutus.html')

def stars(req):
    return render(req, 'step1/stars.html')

def StarsView(req):
    return render(req, 'step1/stars.html')

def goods(req):
    return render(req, 'step1/goods.html')
